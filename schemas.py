from typing import List, Optional
from pydantic import BaseModel
from fastapi import Form

class Blog(BaseModel):
    title : str
    body : str

    class Config:
        from_attributes = True

class User(BaseModel):
    username: str
    name: str
    email: str
    password: str

class ShowUser(BaseModel):
    name: str
    email: str

    class Config:
        from_attributes=True

class CommentResponse(BaseModel):
    comment : str
    reply_of_comment : Optional[str] = None
    user : ShowUser

    class Config:
        from_attributes = True

class Image(BaseModel):
    image_url: str
    class Config:
        from_attributes = True

class LikeUser(BaseModel):
    name: str
    class Config:
        from_attributes=True

class Like(BaseModel):
    user : LikeUser
    class Config:
        from_attributes = True

class ShowBlog(BaseModel):
    id: int
    title: str
    body: str
    user: ShowUser
    images: Optional[List[Image]] = []
    likes: Optional[List[Like]] = []
    like_count: int
    comment_count: int
    comments_on_blog: Optional[List[CommentResponse]] = []

    class Config:
        from_attributes = True


class Login(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str

class ForgotPassword(BaseModel):
    password: str
    confirm_password: str

class ResetPassword(ForgotPassword):
    old_password: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class comments(BaseModel):
    comment: str

class comments_reply(BaseModel):
    text : str

