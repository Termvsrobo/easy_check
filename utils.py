import json
from base64 import b64decode, b64encode
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, SQLModel, create_engine, select

from settings import settings


def _get_engine():
    engine = create_engine(settings.DB_URL)
    return engine


def create_db_and_tables():
    engine = _get_engine()
    SQLModel.metadata.create_all(engine)


def get_session():
    engine = _get_engine()
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


def get_user_model():
    from models import User
    return User


def get_subject(user):
    payload = {'id': user.id, 'username': user.username}
    subject = b64encode(json.dumps(payload).encode()).decode()
    return subject


async def get_current_user(
    session: SessionDep,
    token: Annotated[str, Depends(oauth2_scheme)]
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = json.loads(
        b64decode(token)
    )
    user_id = payload.get('id')
    username = payload.get('username')
    user_model = get_user_model()
    user_query = select(user_model).filter(
        user_model.id == user_id,
        user_model.username == username
    )
    result = session.exec(user_query)
    session.commit()
    user = result.one_or_none()
    if user is None:
        raise credentials_exception
    return user
