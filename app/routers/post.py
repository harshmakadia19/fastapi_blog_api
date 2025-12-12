from fastapi import HTTPException, status, Response, APIRouter, Depends
from .. import models, schemas, oauth2
from ..models import SessionDep
from sqlmodel import select
from typing import List, Annotated
from sqlalchemy import func

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)

# @router.get("/", response_model=List[schemas.Post])
@router.get("/", response_model=List[schemas.PostOut])
def get_posts(session: SessionDep, current_user: Annotated[int, Depends(oauth2.get_current_user)],
              limit: int = 10):
    # cur.execute("SELECT * FROM posts")
    # posts = cur.fetchall()
    # posts = session.exec(select(models.Post).limit(limit)).all()

    posts = session.exec(
        select(models.Post, func.count(models.Vote.post_id).label("votes"))
        .join(models.Vote, models.Post.id == models.Vote.post_id, isouter=True)
        .group_by(models.Post.id)
        .order_by(models.Post.id)
        .limit(limit)
    ).all()

    return posts

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostCreate, session: SessionDep, current_user: Annotated[models.User, Depends(oauth2.get_current_user)]):
    # cur.execute("""
    #     INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *;
    #     """, (post.title, post.content, post.published))
    # new_post = cur.fetchall()
    # conn.commit()

    new_post = models.Post(owner_id=current_user.id, **post.model_dump())
    session.add(new_post)
    session.commit()
    session.refresh(new_post)
    return new_post


@router.get("/{id}", response_model=schemas.PostOut)
def get_post(id: int, session: SessionDep, current_user: Annotated[int, Depends(oauth2.get_current_user)]):
    # cur.execute("SELECT * FROM posts WHERE id = %s", (id,))
    # text_post = cur.fetchone()

    # new_post = session.get(models.Post, id)

    new_post = session.exec(
        select(models.Post, func.count(models.Vote.post_id).label("votes"))
        .join(models.Vote, models.Post.id == models.Vote.post_id, isouter=True)
        .group_by(models.Post.id)
    ).first()

    if not new_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {id} not found")

    return new_post

@router.put("/{id}", response_model=schemas.Post)
def update_post(id: int, post: schemas.PostCreate, session: SessionDep, current_user: Annotated[int, Depends(oauth2.get_current_user)]):
    # cur.execute("""
    #     UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *
    #     """, (post.title, post.content, post.published, id))
    # updated_post = cur.fetchone()
    # conn.commit()

    new_post = session.get(models.Post, id)
    if new_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {id} not found")

    if new_post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"You are not authorized to edit this post")

    new_post.title = post.title
    new_post.content = post.content
    new_post.published = post.published

    session.add(new_post)
    session.commit()
    session.refresh(new_post)
    return new_post

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, session: SessionDep, current_user: Annotated[int, Depends(oauth2.get_current_user)]):
    # cur.execute("DELETE FROM posts WHERE id = %s RETURNING *", (id,))
    # deleted_post = cur.fetchone()
    # conn.commit()

    new_post = session.get(models.Post, id)
    if new_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {id} not found")

    if new_post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"You are not authorized to edit this post")

    session.delete(new_post)
    session.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)

