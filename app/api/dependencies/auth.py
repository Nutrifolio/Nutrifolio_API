from typing import Annotated
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.services import auth_service
from app.services.authentication import AuthenticationException
from app.db.repositories.users import UsersRepository
from app.db.repositories.store_profiles import StoreProfilesRepository
from app.api.dependencies.database import get_repository
from app.models.users import UserInDB
from app.models.store_profiles import StoreProfileInDB


oauth2_scheme_users = OAuth2PasswordBearer(tokenUrl="/api/users/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme_users)],
    user_repo: Annotated[UsersRepository, Depends(get_repository(UsersRepository))],
) -> UserInDB:
    try:
        user_id = auth_service.verify_access_token_user(token=token)
        db_user = await user_repo.get_user_by_id(user_id=user_id)
        return db_user
    except AuthenticationException as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate":"Bearer"}
        )


oauth2_scheme_stores = OAuth2PasswordBearer(tokenUrl="/api/stores/login")


async def get_current_store_id(
    token: Annotated[str, Depends(oauth2_scheme_stores)]
) -> int:
    try:
        store_id = auth_service.verify_access_token_store(token=token)
        return store_id
    except AuthenticationException as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate":"Bearer"}
        )


async def get_current_store_profile(
    token: Annotated[str, Depends(oauth2_scheme_stores)],
    store_profile_repo: Annotated[
        StoreProfilesRepository,
        Depends(get_repository(StoreProfilesRepository))
    ],
) -> StoreProfileInDB:
    try:
        store_id = auth_service.verify_access_token_store(token=token)
        db_store_profile = await store_profile_repo.get_store_profile_by_id(
            store_id=store_id
        )
        return db_store_profile
    except AuthenticationException as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate":"Bearer"}
        )
