from typing import Optional, Literal
from pydantic import BaseModel, EmailStr
from datetime import datetime

# Schemas for Users :
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime


# Schemas for Posts :
class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True

class PostCreate(PostBase):
    pass

class Post(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserOut

class PostOut(BaseModel):
    Post: Post
    votes: int


# Schemas for Authentication :
class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[int] = None

# Schemas for Voting
class Vote(BaseModel):
    post_id: int
    dir: Literal[0, 1]
