import pytest
from app.models.conversation import Conversation, Message, MessageRole


@pytest.mark.asyncio
async def test_create_conversation(test_session):
    import uuid
    conv = Conversation(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        title="Test Conversation",
    )
    test_session.add(conv)
    await test_session.flush()

    assert conv.id is not None
    assert conv.title == "Test Conversation"
    assert conv.is_active is True


@pytest.mark.asyncio
async def test_add_message(test_session):
    import uuid
    conv_id = uuid.uuid4()
    conv = Conversation(id=conv_id, user_id=uuid.uuid4(), title="Test")
    test_session.add(conv)
    await test_session.flush()

    msg = Message(
        id=uuid.uuid4(),
        conversation_id=conv_id,
        role=MessageRole.USER,
        content="Hello, AI!",
    )
    test_session.add(msg)
    await test_session.flush()

    assert msg.content == "Hello, AI!"
    assert msg.role == MessageRole.USER
