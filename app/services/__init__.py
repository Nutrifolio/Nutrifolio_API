from passlib.context import CryptContext
from app.services.authentication import AuthService


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
auth_service = AuthService(pwd_context)
