from fastapi import status, Response, HTTPException, Depends, APIRouter
from .. import models, schemas, oauth2
from sqlalchemy.orm import Session
from ..database import get_db
from typing import List, Optional
from sqlalchemy import func


router = APIRouter(
    prefix="/posts",
    tags=['Post']
)


@router.get('/', response_model=List[schemas.PostOut])
def get_posts(db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user), limit: int = 10,
              skip: int = 0, search: Optional[str] = ""):
    # RAW SQL
    # cursor.execute("""SELECT * FROM posts1 """)
    # posts = cursor.fetchall()

    # SQLALCHEMY
    posts = db.query(models.Post, func.count(models.Vote.post_id).label("Votes")).\
        join(models.Vote, models.Post.id == models.Vote.post_id, isouter=True).group_by(models.Post.id).\
        filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()

    return posts


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_posts(post: schemas.PostBase, db: Session = Depends(get_db),
                 current_user=Depends(oauth2.get_current_user)):
    # RAW SQL
    # cursor.execute("""INSERT INTO posts(title, content , published) VALUES(%s, %s, %s) RETURNING * """,
    #                (post.title, post.content, post.published))
    #
    # new_post = cursor.fetchone()
    # conn.commit()

    # SQLALCHEMY
    # new_post = models.Post(title=post.title, content=post.content, published=post.published)

    new_post = models.Post(user_id=current_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/{id}", response_model=schemas.PostOut)
def get_post(id: int, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user),
             search: Optional[str] = ""):
    # RAW SQL
    # cursor.execute("""SELECT * FROM POSTS WHERE id=%s;""", (str(id)))
    # post = cursor.fetchone()

    # SQLALCHEMY
    post = db.query(models.Post, func.count(models.Vote.post_id).label("Votes")). \
        join(models.Vote, models.Post.id == models.Vote.post_id, isouter=True).group_by(models.Post.id). \
        filter(models.Post.id == id).first()
    if post:
        return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id:{id} was not found')


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    # RAW SQL
    # cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *;""", (str(id)))
    # deleted_post = cursor.fetchone()

    # SQLALCHEMY
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post:
        # conn.commit()
        if post.user_id == current_user.id:
            post_query.delete(synchronize_session=False)
            db.commit()
            return Response(status_code=status.HTTP_204_NO_CONTENT)

        # if the post's owner is not the one who is going to delete the post.
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'Not authorized to perform requested action.')

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id:{id} was not found')


@router.put('/{id}', response_model=schemas.PostResponse)
def update_post(id: int, updated_post: schemas.PostBase, db: Session = Depends(get_db),
                current_user=Depends(oauth2.get_current_user)):
    # RAW SQL
    # cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *; """,
    #                (post.title, post.content, post.published, str(id)))
    # updated_post = cursor.fetchone()

    # SQLALCHEMY
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post:
        # conn.commit()
        if post.user_id == current_user.id:
            post_query.update(updated_post.dict(), synchronize_session=False)
            db.commit()
            return post_query.first()

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f'Not authorized to perform requested action.')

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id: {id} was not found')

