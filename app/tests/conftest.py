from app.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, Base
import pytest
from app.oauth2 import create_access_token
from app import models


SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@' \
                          f'{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test'
engine = create_engine(SQLALCHEMY_DATABASE_URL)
Test_SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)


@pytest.fixture
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = Test_SessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_db():
    db = Test_SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(session):
    #
    # def override_get_db():
    #     try:
    #         yield session
    #     finally:
    #         session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


@pytest.fixture
def add_user1(client):
    user_data = {'email': 'aminjml@gmail.com', 'password': '123'}
    response = client.post('/users/', json=user_data)
    assert response.status_code == 201
    new_user = response.json()
    new_user['password'] = user_data['password']
    return new_user


@pytest.fixture
def add_user2(client):
    user_data = {'email': 'setali7@gmail.com', 'password': '456'}
    response = client.post('/users/', json=user_data)
    assert response.status_code == 201
    new_user = response.json()
    new_user['password'] = user_data['password']
    return new_user


@pytest.fixture
def token(add_user1):
    return create_access_token(data={'user_id': add_user1["id"]})


@pytest.fixture
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    return client


@pytest.fixture
def add_posts(add_user1, add_user2, session):
    posts = [
        {'title': '1st title', 'content': '1st content', "user_id": add_user1['id']},
        {'title': '2nd title', 'content': '2nd content', "user_id": add_user1['id']},
        {'title': '3rd title', 'content': '3rd content', "user_id": add_user2['id']},
        {'title': '4th title', 'content': '4th content', "user_id": add_user2['id']}
    ]

    post_models = map(lambda post: models.Post(**post), posts)

    session.add_all(list(post_models))
    session.commit()

    return session.query(models.Post).all()
