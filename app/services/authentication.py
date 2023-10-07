import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from app.models.token import JWTPayload
from app.core.config import SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


class AuthenticationException(Exception):
    pass


class AuthService:
    def __init__(self, pwd_context: CryptContext) -> None:
        self.pwd_context = pwd_context


    def hash_password(self, *, password: str) -> str:
        return self.pwd_context.hash(password)


    def verify_password(self, *, password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(password, hashed_password)


    def create_access_token_for_user(
        self,
        *,
        user_id: int,
        secret_key: str = str(SECRET_KEY),
        expires_in: int = ACCESS_TOKEN_EXPIRE_MINUTES,
    ) -> str:
        token_payload = JWTPayload(
            user_id=user_id,
            iat=datetime.timestamp(datetime.utcnow()),
            exp=datetime.timestamp(
                datetime.utcnow() + timedelta(minutes=expires_in)
            ),
        )

        access_token = jwt.encode(
            token_payload.model_dump(), secret_key, algorithm=JWT_ALGORITHM
        )
        return access_token
    

    def verify_access_token_user(
        self, *, token: str, secret_key: str = str(SECRET_KEY)
    ) -> int:
        try:
            payload = jwt.decode(
                token, secret_key, algorithms=[JWT_ALGORITHM]
            )
            return payload.get("user_id")
        except jwt.exceptions.ExpiredSignatureError:
            raise AuthenticationException('JWT token has expired.')
        except jwt.exceptions.InvalidTokenError:
            raise AuthenticationException('Invalid JWT token.')
