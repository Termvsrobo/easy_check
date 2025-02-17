from typing import List, Optional

from pydantic import EmailStr
from sqlalchemy_utils import PasswordType
from sqlmodel import Field, Relationship, SQLModel


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    email: EmailStr = Field(unique=True)
    password: bytes = Field(
        sa_type=PasswordType(
            schemes=[
                'pbkdf2_sha512',
                'md5_crypt'
            ],
        )
    )
    is_admin: bool = Field(default=False)

    notes: List["Note"] = Relationship(back_populates="user")


class Note(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=256)
    body: str = Field(max_length=65536)
    is_deleted: bool = Field(default=False)

    user_id: int = Field(foreign_key='user.id', ondelete='CASCADE')
    user: User = Relationship(back_populates='notes')
