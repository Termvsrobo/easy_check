from http import HTTPStatus
from unittest.mock import ANY

import pytest


def test_user_notes(get_user, get_authorized_client):
    username = 'test'
    password = 'test'
    user = get_user(
        username=username,
        email='test@test.com',
        password=password
    )
    auth_client = get_authorized_client(user)
    response = auth_client.get('/api/notes')
    assert response.status_code == 200
    assert response.json() == []


def test_create_note(get_user, get_authorized_client):
    username = 'test'
    password = 'test'
    user = get_user(
        username=username,
        email='test@test.com',
        password=password
    )
    auth_client = get_authorized_client(user)
    response = auth_client.post(
        '/api/notes',
        data={
            'title': 'test', 'body': 'test_body'
        }
    )
    assert response.status_code == 200
    assert response.json() == {
        'id': ANY,
        'title': 'test',
        'body': 'test_body',
        'user_id': user.id
    }


def test_get_note(get_user, get_authorized_client, get_note):
    username = 'test'
    password = 'test'
    user = get_user(
        username=username,
        email='test@test.com',
        password=password
    )
    note = get_note('older_title', 'older_body', user.id)
    auth_client = get_authorized_client(user)
    response = auth_client.get(
        f'/api/notes/{note.id}',
    )
    assert response.status_code == 200
    assert response.json() == {
        'id': note.id,
        'title': note.title,
        'body': note.body,
        'user_id': user.id
    }


def test_get_foreign_note(get_user, get_authorized_client, get_note):
    username = 'test'
    password = 'test'
    user = get_user(
        username=username,
        email='test@test.com',
        password=password
    )
    foreign_user = get_user(
        username='other_user',
        email='othertest@test.com',
        password='other_pass'
    )
    note = get_note('older_title', 'older_body', foreign_user.id)
    auth_client = get_authorized_client(user)
    response = auth_client.get(
        f'/api/notes/{note.id}',
    )
    assert response.status_code == 404
    assert response.json() == {
        'detail': 'Note not found'
    }


def test_update_note(get_user, get_authorized_client, get_note):
    username = 'test'
    password = 'test'
    user = get_user(
        username=username,
        email='test@test.com',
        password=password
    )
    note = get_note('older_title', 'older_body', user.id)
    auth_client = get_authorized_client(user)
    response = auth_client.put(
        f'/api/notes/{note.id}',
        data={
            'title': 'new_title', 'body': 'new_body'
        }
    )
    assert response.status_code == 200
    assert response.json() == {
        'id': note.id,
        'title': 'new_title',
        'body': 'new_body',
        'user_id': user.id
    }


def test_update_foreign_note(get_user, get_authorized_client, get_note):
    username = 'test'
    password = 'test'
    user = get_user(
        username=username,
        email='test@test.com',
        password=password
    )
    foreign_user = get_user(
        username='other_user',
        email='othertest@test.com',
        password='other_pass'
    )
    note = get_note('older_title', 'older_body', foreign_user.id)
    auth_client = get_authorized_client(user)
    response = auth_client.put(
        f'/api/notes/{note.id}',
        data={
            'title': 'new_title', 'body': 'new_body'
        }
    )
    assert response.status_code == 404
    assert response.json() == {
        'detail': 'Note not found'
    }


def test_delete_note(test_session, get_user, get_authorized_client, get_note):
    username = 'test'
    password = 'test'
    user = get_user(
        username=username,
        email='test@test.com',
        password=password
    )
    note = get_note('older_title', 'older_body', user.id)
    auth_client = get_authorized_client(user)
    response = auth_client.delete(
        f'/api/notes/{note.id}',
    )
    assert response.status_code == 200
    assert response.json() == {
        'success': 'ok',
    }

    test_session.refresh(note)
    assert note.is_deleted


def test_delete_foreign_note(
    test_session,
    get_user,
    get_authorized_client,
    get_note
):
    username = 'test'
    password = 'test'
    user = get_user(
        username=username,
        email='test@test.com',
        password=password
    )
    foreign_user = get_user(
        username='other_user',
        email='othertest@test.com',
        password='other_pass'
    )
    note = get_note('older_title', 'older_body', foreign_user.id)
    auth_client = get_authorized_client(user)
    response = auth_client.delete(
        f'/api/notes/{note.id}',
    )
    assert response.status_code == 404
    assert response.json() == {
        'detail': 'Note not found'
    }

    test_session.refresh(note)
    assert not note.is_deleted


def test_get_admin_foreign_note(get_user, get_authorized_client, get_note):
    username = 'test'
    password = 'test'
    user = get_user(
        username=username,
        email='test@test.com',
        password=password,
        is_admin=True
    )
    foreign_user = get_user(
        username='other_user',
        email='othertest@test.com',
        password='other_pass'
    )
    note = get_note('older_title', 'older_body', foreign_user.id)
    auth_client = get_authorized_client(user)
    response = auth_client.get(
        f'/api/notes/{note.id}',
    )
    assert response.status_code == 200
    assert response.json() == {
        'id': note.id,
        'title': note.title,
        'body': note.body,
        'user_id': foreign_user.id
    }


@pytest.mark.parametrize('use_last_user_in_query', [True, False])
def test_admin_notes(
    test_session,
    get_user,
    get_authorized_client,
    get_note,
    use_last_user_in_query
):
    username = 'test'
    password = 'test'
    user = get_user(
        username=username,
        email='test@test.com',
        password=password,
        is_admin=True
    )
    users = [
        get_user(f'test_{i}', f'test_{i}@test.ru', f'test_{i}')
        for i in range(2)
    ]
    last_user = users[-1]
    notes = [
        get_note(
            f'title_{_user.username}',
            f'body_{_user.username}',
            _user.id
        )
        for _user in users
    ]
    auth_client = get_authorized_client(user)
    for note in notes:
        test_session.refresh(note)
    if not use_last_user_in_query:
        response = auth_client.get('/api/notes')
        assert response.status_code == 200
        assert response.json() == [
            note.model_dump(exclude=('is_deleted'))
            for note in notes
        ]
    else:
        response = auth_client.get(
            '/api/notes',
            params={'note_user_id': last_user.id}
        )
        _notes = list(filter(lambda note: note.user_id == last_user.id, notes))
        assert response.status_code == 200
        assert response.json() == [
            note.model_dump(exclude=('is_deleted'))
            for note in _notes
        ]


def test_admin_restore_note(
    test_session,
    get_user,
    get_authorized_client,
    get_note
):
    username = 'test'
    password = 'test'
    user = get_user(
        username=username,
        email='test@test.com',
        password=password,
        is_admin=True
    )
    foreign_user = get_user(
        username='other_user',
        email='othertest@test.com',
        password='other_pass'
    )
    note = get_note(
        'older_title', 'older_body', foreign_user.id, is_deleted=True
    )
    auth_client = get_authorized_client(user)
    response = auth_client.post(
        f'/api/notes/{note.id}/restore',
    )
    assert response.status_code == 200
    assert response.json() == {
        'id': note.id,
        'title': note.title,
        'body': note.body,
        'user_id': foreign_user.id
    }

    test_session.refresh(note)

    assert note.is_deleted is False


def test_user_restore_note(
    test_session,
    get_user,
    get_authorized_client,
    get_note
):
    username = 'test'
    password = 'test'
    user = get_user(
        username=username,
        email='test@test.com',
        password=password,
    )
    foreign_user = get_user(
        username='other_user',
        email='othertest@test.com',
        password='other_pass'
    )
    note = get_note(
        'older_title', 'older_body', foreign_user.id, is_deleted=True
    )
    auth_client = get_authorized_client(user)
    response = auth_client.post(
        f'/api/notes/{note.id}/restore',
    )
    assert response.status_code == 403
    assert response.json() == {
        'detail': HTTPStatus.FORBIDDEN.description,
    }

    test_session.refresh(note)

    assert note.is_deleted is True
