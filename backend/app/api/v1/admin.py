from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.database import get_db
from app.schemas.admin import UserAdminResponse, UserListResponse, AnalyticsResponse, ApiUsageResponse
from app.api.deps import get_admin_user
from app.models.user import User, UserRole
from app.models.conversation import Conversation
from app.models.document import Document
from app.models.citation import Citation
from app.models.study import Quiz
from loguru import logger

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    total_query = select(func.count()).select_from(User)
    total_result = await db.execute(total_query)
    total = total_result.scalar()

    query = select(User).order_by(desc(User.created_at)).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    users = result.scalars().all()

    user_list = []
    for u in users:
        conv_count = await db.execute(select(func.count()).select_from(Conversation).where(Conversation.user_id == u.id))
        doc_count = await db.execute(select(func.count()).select_from(Document).where(Document.user_id == u.id))

        user_list.append(UserAdminResponse(
            id=str(u.id), email=u.email, full_name=u.full_name,
            role=u.role.value if hasattr(u.role, 'value') else u.role,
            auth_provider=u.auth_provider.value if hasattr(u.auth_provider, 'value') else u.auth_provider,
            is_active=u.is_active, is_verified=u.is_verified,
            created_at=u.created_at,
            conversation_count=conv_count.scalar(),
            document_count=doc_count.scalar(),
        ))

    return UserListResponse(users=user_list, total=total, page=page, per_page=per_page)


@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics(
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    total_users = (await db.execute(select(func.count()).select_from(User))).scalar()
    total_convs = (await db.execute(select(func.count()).select_from(Conversation))).scalar()
    total_docs = (await db.execute(select(func.count()).select_from(Document))).scalar()
    total_cits = (await db.execute(select(func.count()).select_from(Citation))).scalar()
    total_quizzes = (await db.execute(select(func.count()).select_from(Quiz))).scalar()

    return AnalyticsResponse(
        total_users=total_users,
        active_users_today=total_users,
        total_conversations=total_convs,
        total_documents=total_docs,
        total_citations=total_cits,
        total_quizzes=total_quizzes,
        api_usage_today=0,
        users_by_day=[],
        feature_usage={"chat": total_convs, "documents": total_docs, "citations": total_cits, "quizzes": total_quizzes},
    )


@router.put("/users/{user_id}/toggle-active")
async def toggle_user_active(
    user_id: str,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("User not found")

    user.is_active = not user.is_active
    await db.flush()
    return {"id": str(user.id), "is_active": user.is_active}
