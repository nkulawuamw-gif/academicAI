import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User, UserProfile, UserRole, AuthProvider
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.core.exceptions import ConflictException, UnauthorizedException, BadRequestException, NotFoundException
from app.config import settings
from loguru import logger


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, email: str, password: str, full_name: str) -> dict:
        result = await self.db.execute(select(User).where(User.email == email))
        existing = result.scalar_one_or_none()
        if existing:
            raise ConflictException("Email already registered")

        user = User(
            id=uuid.uuid4(),
            email=email,
            hashed_password=hash_password(password),
            full_name=full_name,
            auth_provider=AuthProvider.EMAIL,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.db.add(user)

        profile = UserProfile(
            id=uuid.uuid4(),
            user_id=user.id,
        )
        self.db.add(profile)
        await self.db.flush()

        access_token = create_access_token({"sub": str(user.id), "role": user.role.value})
        refresh_token = create_refresh_token({"sub": str(user.id)})

        logger.info(f"New user registered: {email}")
        return {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value,
            "is_verified": user.is_verified,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    async def login(self, email: str, password: str) -> dict:
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user or not user.hashed_password or not verify_password(password, user.hashed_password):
            raise UnauthorizedException("Invalid email or password")

        if not user.is_active:
            raise UnauthorizedException("Account is disabled")

        access_token = create_access_token({"sub": str(user.id), "role": user.role.value})
        refresh_token = create_refresh_token({"sub": str(user.id)})

        logger.info(f"User logged in: {email}")
        return {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value,
            "is_verified": user.is_verified,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    async def refresh_token(self, refresh_token: str) -> dict:
        payload = decode_token(refresh_token)
        if not payload:
            raise UnauthorizedException("Invalid refresh token")

        user_id = payload.get("sub")
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user or not user.is_active:
            raise UnauthorizedException("User not found or disabled")

        access_token = create_access_token({"sub": str(user.id), "role": user.role.value})
        new_refresh_token = create_refresh_token({"sub": str(user.id)})

        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
        }

    async def google_auth(self, code: str) -> dict:
        import httpx

        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }

        async with httpx.AsyncClient() as client:
            token_response = await client.post(token_url, data=data)
            if token_response.status_code != 200:
                raise UnauthorizedException("Failed to authenticate with Google")

            tokens = token_response.json()
            access_token = tokens["access_token"]

            user_info_response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if user_info_response.status_code != 200:
                raise UnauthorizedException("Failed to get user info from Google")

            user_info = user_info_response.json()

        google_id = user_info["id"]
        email = user_info["email"]
        full_name = user_info.get("name", email.split("@")[0])

        result = await self.db.execute(
            select(User).where((User.google_id == google_id) | (User.email == email))
        )
        user = result.scalar_one_or_none()

        if user:
            if not user.is_active:
                raise UnauthorizedException("Account is disabled")
            if not user.google_id:
                user.google_id = google_id
                user.auth_provider = AuthProvider.GOOGLE
                user.is_verified = True
        else:
            user = User(
                id=uuid.uuid4(),
                email=email,
                full_name=full_name,
                google_id=google_id,
                auth_provider=AuthProvider.GOOGLE,
                is_verified=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            self.db.add(user)

            profile = UserProfile(
                id=uuid.uuid4(),
                user_id=user.id,
            )
            self.db.add(profile)

        await self.db.flush()

        jwt_token = create_access_token({"sub": str(user.id), "role": user.role.value})
        jwt_refresh = create_refresh_token({"sub": str(user.id)})

        return {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value,
            "is_verified": user.is_verified,
            "access_token": jwt_token,
            "refresh_token": jwt_refresh,
        }

    async def forgot_password(self, email: str) -> dict:
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if not user:
            return {"message": "If the email exists, a reset link has been sent"}

        from datetime import timedelta
        reset_token = create_access_token({"sub": str(user.id), "purpose": "reset"}, expires_delta=timedelta(minutes=15))
        logger.info(f"Password reset requested for: {email}")
        return {"message": "If the email exists, a reset link has been sent", "reset_token": reset_token}

    async def reset_password(self, token: str, new_password: str) -> dict:
        payload = decode_token(token)
        if not payload or payload.get("purpose") != "reset":
            raise BadRequestException("Invalid or expired reset token")

        user_id = payload.get("sub")
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise NotFoundException("User not found")

        user.hashed_password = hash_password(new_password)
        user.updated_at = datetime.now(timezone.utc)
        await self.db.flush()

        logger.info(f"Password reset completed for user: {user.email}")
        return {"message": "Password reset successful"}

    async def get_profile(self, user_id: str) -> User:
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise NotFoundException("User not found")
        return user
