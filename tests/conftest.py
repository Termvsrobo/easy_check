import pytest
from fastapi.testclient import TestClient
from sqlalchemy_utils import create_database, database_exists, drop_database
from sqlmodel import SQLModel, delete

from app import app
from models import Note, User
from utils import get_session, get_subject


@pytest.fixture(scope='module')
def test_session():
    session = next(get_session())
    if database_exists(session.bind.engine.url):
        drop_database(session.bind.engine.url)
    create_database(session.bind.engine.url)
    SQLModel.metadata.create_all(session.bind.engine)
    yield session
    session.close()


@pytest.fixture
def get_user(test_session):
    def _get_user(username, email, password, is_admin=False):
        user = User(
            username=username,
            email=email,
            password=password,
            is_admin=is_admin
        )
        test_session.add(user)
        test_session.commit()
        test_session.refresh(user)
        return user
    yield _get_user
    test_session.exec(delete(User))
    test_session.commit()


@pytest.fixture
def get_note(test_session):
    def _get_note(title, body, user_id, is_deleted=False):
        note = Note(
            title=title,
            body=body,
            user_id=user_id,
            is_deleted=is_deleted
        )
        test_session.add(note)
        test_session.commit()
        test_session.refresh(note)
        return note
    yield _get_note
    test_session.exec(delete(Note))
    test_session.commit()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def get_authorized_client():
    def _get_client(user):
        subject = get_subject(user)
        headers = {'Authorization': f'Bearer {subject}'}
        auth_client = TestClient(app, headers=headers)
        return auth_client
    yield _get_client
