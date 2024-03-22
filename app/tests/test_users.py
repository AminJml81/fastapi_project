from fastapi.testclient import TestClient
from app.main import app
from app import schemas
import pytest
from jose import jwt
from app.config import settings


def test_root(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == {"message": 'Welcome'}


def test_create_user(client):
    response = client.post('/users/', json={'email': 'aminjml@gmail.com', 'password': '123'})
    new_user = schemas.UserResponse(**response.json())
    assert response.status_code == 201


def test_login_user(client, add_user1):
    data = {'username': add_user1['email'], 'password': add_user1['password']}
    response = client.post('/login/', data=data)
    login_response = schemas.Token(**response.json())
    payload = jwt.decode(login_response.access_token, settings.secret_key, algorithms=[settings.algorithm])
    id: str = payload['user_id']
    assert response.status_code == 200
    assert login_response.token_type == 'bearer'
    assert id == add_user1['id']


@pytest.mark.parametrize('email, password, status_code', [
    ('wrongemail@gmail.com', '123', 403),
    ('aminjml@gmail.com', 'wrong_password', 403),
    ('wrongemail@gmail.com', 'wrong_password', 403),
    (None, '123', 422),
    ("aminjml@gmail.com", None, 422)
])
def test_incorrect_login(client, email, password, status_code):
    response = client.post('/login', data={'username': email, 'password': password})
    assert response.status_code == status_code

