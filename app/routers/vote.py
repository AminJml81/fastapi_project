from fastapi import status, HTTPException, Depends, APIRouter
from .. import models, schemas, oauth2
from ..database import get_db
from sqlalchemy.orm import Session


router = APIRouter(
    prefix="/votes",
    tags=['Vote']
)


@router.post('/', status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Vote, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # user can only like a post once and it will raise an HTTP error for liking it again.

    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id:{vote.post_id} does not exits.")
    vote_query = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id,
                                              models.Vote.user_id == current_user.id)
    found_vote = vote_query.first()
    if vote.dir == 1:
        # if user want to like the post.
        if found_vote:
            # if user wants to like the post which has liked before.
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f'user {current_user.id} has already voted on post {vote.post_id}')
        new_vote = models.Vote(post_id = vote.post_id, user_id = current_user.id)

        db.add(new_vote)
        db.commit()
        return {'message': "successfully added vote"}

    elif vote.dir == 0:
        # if user want to unlike the post.
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Vote does not exist')
        vote_query.delete(synchronize_session = False)
        db.commit()
        return {'message': "successfully deleted vote"}
