import pytest
from app import models


@pytest.fixture
def add_vote_post1(add_posts, session, add_user1):
    new_vote = models.Vote(post_id=add_posts[0].id, user_id=add_user1['id'])
    session.add(new_vote)
    session.commit()


@pytest.fixture
def add_vote_post3(add_posts, session, add_user1):
    new_vote = models.Vote(post_id=3, user_id=add_user1['id'])
    session.add(new_vote)
    session.commit()


def test_user_vote_on_its_own_post(authorized_client, add_posts):
    response = authorized_client.post('/votes/', json={'post_id': add_posts[0].id, 'dir': 1})
    assert response.status_code == 201


def test_user_vote_on_its_own_post_twice(authorized_client, add_posts, add_vote_post1):
    response = authorized_client.post('/votes/', json={'post_id': 1, 'dir': 1})
    assert response.status_code == 409


def test_user_delete_vote_on_its_own_post(authorized_client, add_posts, add_vote_post1):
    response2 = authorized_client.post('/votes/', json={'post_id': 1, 'dir': 0})
    assert response2.status_code == 201


def test_user_delete_vote_on_its_own_post_which_did_not_vote_before(authorized_client, add_posts, add_vote_post1):
    response = authorized_client.post('/votes/', json={'post_id': 2, 'dir': 0})
    assert response.status_code == 404


def test_user_vote_on_others_post(authorized_client, add_posts):
    response = authorized_client.post('/votes/', json={'post_id': 3, 'dir': 1})
    assert response.status_code == 201


def test_user_vote_on_others_post_twice(authorized_client, add_posts, add_vote_post3):
    response2 = authorized_client.post('/votes/', json={'post_id': 3, 'dir': 1})
    assert response2.status_code == 409


def test_user_delete_vote_on_others_post(authorized_client, add_posts, add_vote_post3):
    response2 = authorized_client.post('/votes/', json={'post_id': 3, 'dir': 0})
    assert response2.status_code == 201


def test_user_delete_vote_on_others_post_which_did_not_vote_before(authorized_client, add_posts):
    response = authorized_client.post('/votes/', json={'post_id': 3, 'dir': 0})
    assert response.status_code == 404


def test_user_on_unavailable_post(authorized_client, add_posts):
    response = authorized_client.post('/votes/', json={'post_id': 404, 'dir': 1})
    assert response.status_code == 404


def test_unauthorized_user_vote_on_its_own_post(client, add_posts):
    response = client.post('/votes/', json={'post_id': 1, 'dir': 1})
    assert response.status_code == 401


def test_unauthorized_user_delete_vote_on_its_own_post(client, add_posts):
    response = client.post('/votes/', json={'post_id': 1, 'dir': 0})
    assert response.status_code == 401


def test_unauthorized_user_vote_on_others_post(client, add_posts):
    response = client.post('/votes/', json={'post_id': 3, 'dir': 1})
    assert response.status_code == 401


def test_unauthorized_user_delete_vote_on_others_post(client, add_posts):
    response = client.post('/votes/', json={'post_id': 3, 'dir': 0})
    assert response.status_code == 401