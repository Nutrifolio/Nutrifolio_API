from pydantic import EmailStr
from fastapi import HTTPException, status
from app.db.repositories.base import BaseRepository
from app.models.users import UserCreate, UserInDB
from app.services import auth_service
from databases import Database


GET_USER_BY_ID_QUERY = """
    SELECT id, email, password
    FROM users
    WHERE id = :id;
"""

GET_USER_BY_EMAIL_QUERY = """
    SELECT id, email, password
    FROM users
    WHERE email = :email;
"""
 
REGISTER_NEW_USER_QUERY = """
    INSERT INTO users (email, password)
    VALUES (:email, :password)
    RETURNING id, email, password;
"""


class UsersRepository(BaseRepository):
    """"
    All database actions associated with the User resource
    """

    def __init__(self, db: Database) -> None:
        super().__init__(db)
        self.auth_service = auth_service
    

    async def get_user_by_id(self, *, user_id: int) -> UserInDB:
        user_record = await self.db.fetch_one(
            query=GET_USER_BY_ID_QUERY,
            values={"id": user_id}
        )

        if not user_record:
            return None

        return UserInDB(**user_record)


    async def get_user_by_email(self, *, email: EmailStr) -> UserInDB:
        user_record = await self.db.fetch_one(
            query=GET_USER_BY_EMAIL_QUERY,
            values={"email": email}
        )

        if not user_record:
            return None

        return UserInDB(**user_record)


    async def register_new_user(self, *, new_user: UserCreate) -> UserInDB:
        hashed_password = self.auth_service.hash_password(
            password=new_user.password
        )

        new_user = new_user.model_copy(
            update={'password': hashed_password}
        )

        created_user_record = await self.db.fetch_one(
            query=REGISTER_NEW_USER_QUERY, 
            values={**new_user.model_dump(exclude={'conf_password'})}
        )

        return UserInDB(**created_user_record)
