import pytest
from app import schemas


def test_get_all_posts(authorized_client, add_posts):
    response = authorized_client.get('/posts/')
    assert len(response.json()) == len(add_posts)
    map(lambda post: schemas.PostOut(**post), response.json())
    assert response.status_code == 200


def test_unauthorized_user_get_all_posts(client, add_posts):
    response = client.get('/posts/')
    assert response.status_code == 401


@pytest.mark.parametrize('id', [1, 2, 3, 4])
def test_unauthorized_user_get_one_post(client, add_posts, id):
    response = client.get(f'/posts/{id}')
    assert response.status_code == 401


def test_user_get_unavailable_post(authorized_client, add_posts):
    response = authorized_client.get('/posts/404')
    assert response.status_code == 404


def test_unauthorized_user_get_unavailable_post(client, add_posts):
    response = client.get('/posts/404')
    assert response.status_code == 401


@pytest.mark.parametrize('id', [1, 2, 3, 4])
def test_user_get_post(authorized_client, add_posts, id):
    response = authorized_client.get(f'/posts/{id}')
    post = schemas.PostOut(**response.json())
    assert response.status_code == 200
    assert post.Post.id == add_posts[id-1].id
    assert post.Post.content == add_posts[id-1].content
    assert post.Post.user.id == add_posts[id-1].user_id


@pytest.mark.parametrize('title, content, published', [
    ('first_test_title', 'first_test_content', True),
    ('second_test_title', 'second_test_content', False),
    ('third_test_title', 'third_test_content', True)
])
def test_create_post(authorized_client, add_user1, title, content, published):
    response = authorized_client.post('/posts/', json={'title': title, 'content': content, "published": published})
    assert response.status_code == 201

    post = schemas.PostResponse(**response.json())
    assert post.title == title
    assert post.content == content
    assert post.published == published
    assert post.user_id == add_user1['id']


def test_create_post_default_published_true(authorized_client, add_user1):
    data = {'title': 'title1', 'content': 'content'}
    response = authorized_client.post('/posts/', json=data)
    assert response.status_code == 201

    post = schemas.PostResponse(**response.json())
    assert post.title == data["title"]
    assert post.content == data["content"]
    assert post.published == True
    assert post.user_id == add_user1['id']


def test_unauthorized_user_delete_post(client, add_posts):
    response = client.delete('/posts/1')
    assert response.status_code == 401


@pytest.mark.parametrize('id', [1, 2])
def test_user_delete_post(authorized_client, add_posts, add_user1, id):
    response = authorized_client.delete(f'/posts/{id}')
    assert response.status_code == 204


def test_user_delete_post_unavailable_post(authorized_client, add_posts, add_user1):
    response = authorized_client.delete(f'/posts/{404}')
    assert response.status_code == 404


def test_user_delete_other_user_post(authorized_client, add_posts, add_user1):
    response = authorized_client.delete('/posts/4')
    assert response.status_code == 403


def test_unauthorized_user_update_post(client, add_posts):
    response = client.put('/posts/1')
    assert response.status_code == 401


def test_user_update_post(authorized_client, add_posts, add_user1):
    data = {
        'title': 'updated title',
        'content': 'updated content',
        'id': add_posts[0].id
    }

    response = authorized_client.put(f'/posts/{add_posts[0].id}', json=data)
    updated_post = schemas.PostResponse(**response.json())
    assert response.status_code == 200
    assert updated_post.title == data['title']
    assert updated_post.content == data['content']


def test_user_update_unavailable_post(authorized_client, add_posts, add_user1):
    data = {
        'title': 'updated title',
        'content': 'updated content',
        'id': 404
    }

    response = authorized_client.put('/posts/404', json=data)
    assert response.status_code == 404


def test_user_update_other_user_post(authorized_client, add_posts, add_user1):
    data = {
        'title': 'updated title',
        'content': 'updated content',
        'id': add_posts[3].id
    }

    response = authorized_client.put(f'/posts/{add_posts[3].id}', json=data)
    assert response.status_code == 403

