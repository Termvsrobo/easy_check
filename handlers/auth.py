from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select

from models import User
from utils import SessionDep, get_subject

auth_router = APIRouter(prefix='/auth', tags=['Auth'])


@auth_router.post('/login')
async def login(
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user_query = select(User).filter(User.username == form_data.username)
    user = session.exec(user_query).one_or_none()
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Incorrect username or password"
        )

    if not form_data.password == user.password:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Incorrect username or password"
        )

    # Тут, конечно, надо сделать нормальную авторизацию с JWT.
    # Но для теста пока и так норм
    subject = get_subject(user)
    return {"access_token": subject, "token_type": "bearer"}
