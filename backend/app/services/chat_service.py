import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.models.conversation import Conversation, Message, MessageRole
from app.services.llm_service import LLMService
from app.core.exceptions import NotFoundException
from loguru import logger


class ChatService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.llm = LLMService()

    async def create_conversation(self, user_id: uuid.UUID, title: str = "New Conversation", context: dict = None) -> Conversation:
        conversation = Conversation(
            id=uuid.uuid4(),
            user_id=user_id,
            title=title,
            context=context or {},
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.db.add(conversation)
        await self.db.flush()
        return conversation

    async def get_conversations(self, user_id: uuid.UUID, page: int = 1, per_page: int = 20) -> dict:
        total_query = select(func.count()).select_from(Conversation).where(
            Conversation.user_id == user_id, Conversation.is_active == True
        )
        total_result = await self.db.execute(total_query)
        total = total_result.scalar()

        query = (
            select(Conversation)
            .where(Conversation.user_id == user_id, Conversation.is_active == True)
            .order_by(desc(Conversation.updated_at))
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        result = await self.db.execute(query)
        conversations = result.scalars().all()

        result_list = []
        for conv in conversations:
            msg_query = select(Message).where(Message.conversation_id == conv.id).order_by(desc(Message.created_at)).limit(1)
            msg_result = await self.db.execute(msg_query)
            last_msg = msg_result.scalar_one_or_none()

            count_query = select(func.count()).select_from(Message).where(Message.conversation_id == conv.id)
            count_result = await self.db.execute(count_query)
            msg_count = count_result.scalar()

            result_list.append({
                "id": str(conv.id),
                "title": conv.title,
                "context": conv.context,
                "is_active": conv.is_active,
                "created_at": conv.created_at,
                "updated_at": conv.updated_at,
                "message_count": msg_count,
                "last_message": last_msg.content[:200] if last_msg else None,
            })

        return {"conversations": result_list, "total": total, "page": page, "per_page": per_page}

    async def get_conversation(self, conversation_id: str, user_id: uuid.UUID) -> Conversation:
        conv_uuid = uuid.UUID(conversation_id)
        result = await self.db.execute(
            select(Conversation).where(Conversation.id == conv_uuid, Conversation.user_id == user_id)
        )
        conversation = result.scalar_one_or_none()
        if not conversation:
            raise NotFoundException("Conversation not found")
        return conversation

    async def update_conversation(self, conversation_id: str, user_id: uuid.UUID, title: str = None, context: dict = None) -> Conversation:
        conversation = await self.get_conversation(conversation_id, user_id)
        if title:
            conversation.title = title
        if context is not None:
            conversation.context = context
        conversation.updated_at = datetime.now(timezone.utc)
        await self.db.flush()
        return conversation

    async def delete_conversation(self, conversation_id: str, user_id: uuid.UUID):
        conversation = await self.get_conversation(conversation_id, user_id)
        conversation.is_active = False
        conversation.updated_at = datetime.now(timezone.utc)
        await self.db.flush()

    async def add_message(self, conversation_id: str, role: MessageRole, content: str, metadata: dict = None, tokens_used: int = None, attachments: list = None) -> Message:
        conv_uuid = uuid.UUID(conversation_id)
        extra = dict(metadata or {})
        if attachments:
            extra["attachments"] = attachments
        message = Message(
            id=uuid.uuid4(),
            conversation_id=conv_uuid,
            role=role,
            content=content,
            extra_data=extra,
            tokens_used=tokens_used,
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(message)

        conv_result = await self.db.execute(select(Conversation).where(Conversation.id == conv_uuid))
        conversation = conv_result.scalar_one_or_none()
        if conversation:
            conversation.updated_at = datetime.now(timezone.utc)
            if role == MessageRole.USER:
                conversation.title = content[:100] if len(content) > 100 else content

        await self.db.flush()
        return message

    async def get_messages(self, conversation_id: str, user_id: uuid.UUID) -> list[Message]:
        await self.get_conversation(conversation_id, user_id)
        conv_uuid = uuid.UUID(conversation_id)
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conv_uuid)
            .order_by(Message.created_at)
        )
        return result.scalars().all()

    async def send_message(self, conversation_id: str, user_id: uuid.UUID, content: str, metadata: dict = None, attachments: list = None) -> dict:
        user_msg = await self.add_message(conversation_id, MessageRole.USER, content, metadata, attachments=attachments)
        conversation = await self.get_conversation(conversation_id, user_id)

        attachment_text = ""
        if attachments:
            names = [a.get("file_name", "file") for a in attachments]
            attachment_text = f"\n[Attached files: {', '.join(names)}]"

        messages = await self.get_messages(conversation_id, user_id)
        chat_history = "\n".join([f"{m.role.value}: {m.content}" for m in messages[-20:]])

        full_user_content = content + attachment_text

        system_prompt = """You are an AI Academic Assistant. You help students with:
- Answering academic questions
- Explaining concepts
- Providing study guidance
- Research assistance
- Writing help

Be concise, accurate, and educational. Use academic language but explain complex terms."""
        prompt = f"Conversation context: {conversation.context}\n\nChat history:\n{chat_history}\n\nUser: {full_user_content}\n\nAssistant:"

        try:
            ai_response = await self.llm.generate(prompt, system_prompt=system_prompt)
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            ai_response = "I apologize, but I'm currently unable to process your request due to a temporary issue with the AI service. Please try again later."
        ai_msg = await self.add_message(conversation_id, MessageRole.ASSISTANT, ai_response)

        return {
            "user_message": {
                "id": str(user_msg.id),
                "conversation_id": str(user_msg.conversation_id),
                "role": user_msg.role.value,
                "content": user_msg.content,
                "attachments": attachments or [],
                "created_at": user_msg.created_at,
            },
            "assistant_message": {
                "id": str(ai_msg.id),
                "conversation_id": str(ai_msg.conversation_id),
                "role": ai_msg.role.value,
                "content": ai_msg.content,
                "attachments": [],
                "created_at": ai_msg.created_at,
            },
        }

    async def stream_message(self, conversation_id: str, user_id: uuid.UUID, content: str):
        await self.add_message(conversation_id, MessageRole.USER, content)
        conversation = await self.get_conversation(conversation_id, user_id)

        system_prompt = "You are an AI Academic Assistant. Provide helpful, accurate academic support."
        full_response = ""
        try:
            stream = await self.llm.generate_stream(content, system_prompt=system_prompt)
            async for chunk in stream:
                full_response += chunk
                yield chunk
        except Exception as e:
            logger.error(f"Stream generation failed: {e}")
            fallback = "I apologize, but I'm currently unable to process your request due to a temporary issue with the AI service. Please try again later."
            yield fallback
            full_response = fallback

        await self.add_message(conversation_id, MessageRole.ASSISTANT, full_response)
