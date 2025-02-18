from fastapi import APIRouter, Depends, status, File, Form, UploadFile
import schemas, database
import oauth2
from sqlalchemy.orm import Session
from typing import List
from services import blog
router = APIRouter(prefix = "/blog", tags = ["blogs"])
get_db = database.get_db

@router.get("/", response_model=List[schemas.ShowBlog])
def all(db: Session = Depends(get_db), skip: int = 0, limit: int = 10):
    """Endpoint to get a list of blogs with pagination."""
    blogs = blog.get_all(db, skip, limit)
    return blogs

@router.post("/", status_code = status.HTTP_201_CREATED)
def create(
    title: str = Form(...),
    body: str = Form(...),
    images: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(oauth2.get_current_user)
):
    """Endpoint to create a new blog with optional images."""

    images = images if images is not None else []
    return blog.create(title, body, images, db, current_user)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def destroy(id, db: Session = Depends(get_db), current_user: schemas.ShowUser = Depends(oauth2.get_current_user)):
    """Endpoint to delete a blog by its ID."""
    return blog.destroy(id, db, current_user)

@router.put("/{id}", status_code = status.HTTP_202_ACCEPTED)
def update(id : int, request: schemas.Blog, db: Session = Depends(get_db), current_user: schemas.ShowUser = Depends(
    oauth2.get_current_user)):
    """Endpoint to update a blog by its ID."""
    return blog.update(id, request, db, current_user)

@router.get("/{id}", status_code = 200, response_model = schemas.ShowBlog)
def get_blog(id : int, db: Session = Depends(get_db), current_user: schemas.ShowUser = Depends(oauth2.get_current_user)):
    """Endpoint to get a single blog by its ID."""
    return blog.show(id, db)

@router.post("/{blog_id}/like", status_code=status.HTTP_200_OK)
def like_blog(
    blog_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(oauth2.get_current_user)
):
    """Endpoint to like a blog by its ID."""
    return blog.like_blog(blog_id, db, current_user)

@router.post("/{blog_id}/dislike", status_code = status.HTTP_200_OK)
def dislike_blog(
        blog_id: int,
        db: Session = Depends(get_db),
        current_user: str = Depends(oauth2.get_current_user)
):
    """Endpoint to dislike a blog by its ID."""
    return blog.dislike_blog(blog_id, db, current_user)

@router.post("/{blog_id}/comment", status_code = status.HTTP_200_OK)
def comment_blog(
    blog_id: int,
    request: schemas.comments,
    db: Session = Depends(get_db),
    current_user: str = Depends(oauth2.get_current_user)
):
    """Endpoint to comment a blog by its ID."""
    return blog.comment_blog(blog_id, request, db, current_user)

@router.post("/{blog_id}/comment/{comment_id}/reply", status_code = status.HTTP_200_OK)
def reply_comment(blog_id: int, comment_id: int, request: schemas.comments_reply, db: Session = Depends(get_db), current_user: str = Depends(
    oauth2.get_current_user)):
    """Endpoint to reply to a comment by its ID."""
    return blog.reply_comment(blog_id, comment_id, request, db, current_user)

@router.delete("/{blog_id}/comment/{comment_id}", status_code=status.HTTP_200_OK)
def delete_comment(
    blog_id: int,
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(oauth2.get_current_user)
):
    """Endpoint to delete a comment by its ID."""
    return blog.delete_comment(blog_id, comment_id, db, current_user)

@router.delete("/image/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_image(image_id: int, db: Session = Depends(get_db), current_user: schemas.ShowUser = Depends(
    oauth2.get_current_user)):
    """Endpoint to delete an image by its ID."""
    return blog.delete_image(image_id, db, current_user)

@router.post("/{blog_id}/add_image/", status_code=status.HTTP_200_OK)
def add_images(blog_id : int, images: List[UploadFile] = File(...), db: Session = Depends(get_db), current_user: schemas.ShowUser = Depends(
    oauth2.get_current_user)):
    """Endpoint to add images to a blog by its ID."""
    return blog.add_images(blog_id, images, db, current_user)
