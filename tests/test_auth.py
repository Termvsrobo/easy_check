import json
from base64 import b64encode


def test_user_login(get_user, client):
    username = 'test'
    password = 'test'
    user = get_user(
        username=username,
        email='test@test.com',
        password=password
    )
    response = client.post(
        '/api/auth/login',
        data={'username': username, 'password': password}
    )

    payload = {'id': user.id, 'username': user.username}
    subject = b64encode(json.dumps(payload).encode()).decode()
    assert response.status_code == 200
    assert response.json() == {'access_token': subject, 'token_type': 'bearer'}
