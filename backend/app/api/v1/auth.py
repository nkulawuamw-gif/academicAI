from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.auth import (
    RegisterRequest, LoginRequest, TokenResponse, RefreshTokenRequest,
    ForgotPasswordRequest, ResetPasswordRequest, GoogleAuthRequest, AuthResponse,
)
from app.schemas.user import UserResponse, UserProfileUpdate, UserProfileResponse
from app.api.deps import get_current_user
from app.models.user import User
from app.services.auth_service import AuthService
from loguru import logger

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    return await service.register(request.email, request.password, request.full_name)


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    return await service.login(request.email, request.password)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    return await service.refresh_token(request.refresh_token)


@router.post("/google", response_model=AuthResponse)
async def google_auth(request: GoogleAuthRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    return await service.google_auth(request.code)


@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    return await service.forgot_password(request.email)


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    return await service.reset_password(request.token, request.password)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    profile = None
    if current_user.profile:
        profile = UserProfileResponse(
            id=str(current_user.profile.id),
            avatar_url=current_user.profile.avatar_url,
            bio=current_user.profile.bio,
            institution=current_user.profile.institution,
            course=current_user.profile.course,
            year_of_study=current_user.profile.year_of_study,
            preferences=current_user.profile.preferences,
        )

    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role.value if hasattr(current_user.role, 'value') else current_user.role,
        auth_provider=current_user.auth_provider.value if hasattr(current_user.auth_provider, 'value') else current_user.auth_provider,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at,
        profile=profile,
    )


@router.put("/profile", response_model=UserProfileResponse)
async def update_profile(
    request: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = current_user.profile
    if not profile:
        from app.models.user import UserProfile
        import uuid
        profile = UserProfile(id=uuid.uuid4(), user_id=current_user.id)
        db.add(profile)
        await db.flush()

    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(profile, key, value)

    await db.flush()
    return UserProfileResponse(
        id=str(profile.id),
        avatar_url=profile.avatar_url,
        bio=profile.bio,
        institution=profile.institution,
        course=profile.course,
        year_of_study=profile.year_of_study,
        preferences=profile.preferences,
    )
