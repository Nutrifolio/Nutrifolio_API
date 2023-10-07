from typing import Annotated
from fastapi import APIRouter, Path, Body, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.services import auth_service
from app.models.token import AccessToken
from app.models.users import UserCreate, UserInDB, UserOut
from app.db.repositories.users import UsersRepository
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.database import get_repository
from app.api.exceptions.users import EmailAlreadyExists, InvalidCredentials
from app.core.logging import get_logger


router = APIRouter()

users_logger = get_logger(__name__)


@router.post("/register", response_model=AccessToken, name="register-new-user", status_code=status.HTTP_201_CREATED)
async def register_new_user(
    new_user: Annotated[UserCreate, Body(..., embed=True)],
    user_repo: Annotated[UsersRepository, Depends(get_repository(UsersRepository))],
) -> AccessToken:
    try:
        db_user = await user_repo.get_user_by_email(email=new_user.email)
        if db_user:
            raise EmailAlreadyExists(f"There is already an account registered with the email {new_user.email}")
        
        created_user = await user_repo.register_new_user(new_user=new_user)
        access_token = auth_service.create_access_token_for_user(
            user_id=created_user.id
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except EmailAlreadyExists as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc))
    except Exception as exc:
        users_logger.exception(exc)
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, 
            "Failed to register user."
        )


@router.post('/login', response_model=AccessToken, name="user-login")
async def user_login(
    user_credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_repo: Annotated[UsersRepository, Depends(get_repository(UsersRepository))],
) -> AccessToken:
    try:
        # OAuth2PasswordRequestForm's username corresponds to the email
        db_user = await user_repo.get_user_by_email(
            email=user_credentials.username
        )
        if not db_user:
            raise InvalidCredentials("Incorrect email or password.")

        if not auth_service.verify_password(
            password=user_credentials.password,
            hashed_password=db_user.password
        ):
            raise InvalidCredentials("Incorrect email or password.")

        access_token = auth_service.create_access_token_for_user(
            user_id=db_user.id
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except InvalidCredentials as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Basic"}
        )
    except Exception as exc:
        users_logger.exception(exc)
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, 
            "Failed to login."
        )


@router.get("/me", response_model=UserOut, name="get-current-user-info")
async def get_current_user_info(
    current_user: Annotated[UserInDB, Depends(get_current_user)]
) -> UserOut:
    return current_user
