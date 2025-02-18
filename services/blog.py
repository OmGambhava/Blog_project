from fastapi import HTTPException, status, UploadFile
from sqlalchemy.orm import Session
from typing import List
import models, schemas

def get_all(db: Session, skip: int = 0, limit: int = 10):
    """
        get all blog entries from the database with pagination.

        Args:
            db (Session): The database session to query the database.
            skip (int, optional): The number of records to skip.
            limit (int, optional): The maximum number of records to retrieve.

        Returns:
            list: A list of Blog fetched from the database.
        """
    return db.query(models.Blog).offset(skip).limit(limit).all()

def upload_image(image: UploadFile):
    """
        Uploads the image.
        Args:
            image (UploadFile): The image file to be uploaded.
        Returns:
            str: The location of the uploaded file if successful else None.
        """
    try:
        file_location = f"uploads/{image.filename}"
        # Open the file in write-binary mode and save
        with open(file_location, "wb") as file:
            file.write(image.file.read())
        return file_location
    except Exception as e:
        print(f"Error uploading image: {e}")
        return None

def create(title: str, body: str, images: List[UploadFile], db: Session, userData):
    """
    Creates a new blog with title, body, and images, and current user.

    Args:
        title (str): The title of the blog.
        body (str): The body of the blog.
        images (List[UploadFile]): A list of image files.
        db (Session): The database session for database operations.
        userData: The current user data.

    Returns:
        models.Blog: The created blog post.
    """
    #Get the current user
    user = db.query(models.User).filter(models.User.email == userData.email).first()

    image_objects = [] #List for store uploaded image

    for image in images:
        image_url = upload_image(image)
        if image_url:
            image_obj = models.Image(
                image_url=image_url,
                user_id=user.id)
            image_objects.append(image_obj)

    #Create new blog
    new_blog = models.Blog(
        title=title,
        body=body,
        images=image_objects,
        user_id=user.id)

    db.add(new_blog)
    db.add_all(image_objects)
    db.commit()
    db.refresh(new_blog)

    return new_blog


def destroy(id: int, db: Session, current_user_email: str):
    """
        Deletes a blog by its id if the current user is the owner of the blog.

        Args:
            id (int): The id of the blog.
            db (Session): The database session for database operations.
            current_user_email (str): The email of the current user.
        """
    # Get the current user
    user = db.query(models.User).filter(models.User.email == current_user_email.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    #Get blog using provided id
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found.")
    #check that blog is delete by current user or not
    blog = db.query(models.Blog).filter(models.Blog.id == id, models.Blog.user_id == user.id)
    if not blog.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"you do not have permission to delete it.")

    blog.delete(synchronize_session=False)
    db.commit()
    return "Done"

def update(id: int, request : schemas.Blog, db: Session, current_user: str):
    """
       Updates an existing blog in that blog update the title and body if the current user is the owner.

       Args:
           id (int): The ID of the blog to be updated.
           request (schemas.Blog): The updated data for the blog (title and body).
           db (Session): The database session for database operations.
           current_user (str): The email of the current user.

       Returns:
           models.Blog: The updated blog post.
       """
    #Get the current user
    user = db.query(models.User).filter(models.User.email == current_user.email).first()

    #Get the blog using provided id
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"blog with id {id} not found.")

    #Check that owner is update the blog
    if blog.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not allowed to edit this blog.")

    blog.title = request.title
    blog.body = request.body

    db.commit()
    db.refresh(blog)
    return blog

def show(id: int, db: Session):
    """
        Get a blog by its ID.

        Args:
            id (int): The ID of the blog.
            db (Session): The database session for querying the database.

        Returns:
            models.Blog: The blog with the specified ID, or None if not found.
        """
    return db.query(models.Blog).filter(models.Blog.id == id).first()

def like_blog(blog_id: int, db: Session, current_user: str):
    """
        Allows a user to like a blog, if user has not already liked the blog else give an error message.

        Args:
            blog_id (int): The ID of the blog to be liked.
            db (Session): The database session for database operations.
            current_user (str): The email of the current user.

        Returns:
            dict: A message confirming the blog has been liked.
        """
    #Get the current user
    user = db.query(models.User).filter(models.User.email == current_user.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    #Get the blog using provided id
    blog = db.query(models.Blog).filter(models.Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found.")
    #Check user is already like or not
    existing_like = db.query(models.Like).filter(models.Like.blog_id == blog.id, models.Like.user_id == user.id).first()
    #If user already like than give error message
    if existing_like:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have already liked this blog.")

    like = models.Like(user_id=user.id, blog_id=blog.id)
    db.add(like)
    db.commit()

    return {"message": "Blog liked successfully"}

def dislike_blog(blog_id: int, db: Session, current_user: str):
    """
        Allows a user to remove their like from a blog, if they have liked it.

        Args:
            blog_id (int): The id of the blog.
            db (Session): The database session for database operations.
            current_user (str): The email of the current user.

        Returns:
            dict: A message confirming the blog has been disliked.
        """
    #Get the current user
    user = user = db.query(models.User).filter(models.User.email == current_user.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    #Get the blog using provided id
    blog = db.query(models.Blog).filter(models.Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found.")
    # Check if the user has already liked the blog
    existing_like = db.query(models.Like).filter(models.Like.blog_id == blog.id, models.Like.user_id == user.id).first()
    # If the user has not liked the blog, raise an error
    if not existing_like:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have not liked this blog yet.")
    db.delete(existing_like)
    db.commit()
    return {"message": "Blog disliked successfully"}

def comment_blog(blog_id: int,  request: schemas.comments, db: Session, current_user: str):
    """
        Allows a user to comment on a blog post.

        Args:
            blog_id (int): The ID of the blog to be commented on.
            request (schemas.comments): The comment content from the user.
            db (Session): The database session for database operations.
            current_user (str): The email of the current user commenting on the blog.

        Returns:
            dict: A message confirming the blog has been commented on.
        """

    user = db.query(models.User).filter(models.User.email == current_user.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    blog = db.query(models.Blog).filter(models.Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found.")

    comment_blog = models.Comment(
        comment = request.comment,
        user_id=user.id,
        blog_id=blog.id
    )
    db.add(comment_blog)
    db.commit()
    db.refresh(comment_blog)

    return {"Comment": "Blog commented successfully"}


def reply_comment(blog_id: int, comment_id: int, request: schemas.comments_reply, db: Session, current_user: str):
    """
        Allows a user to reply to a specific comment on a blog post.

        Args:
            blog_id (int): The ID of the blog.
            comment_id (int): The ID of the comment in which user wants to reply.
            request (schemas.comments_reply): The reply provided by the user.
            db (Session): The database session for database operations.
            current_user (str): The email of the current user.

        Returns:
            dict: A message confirming the comment has been replied to.
    """
    user = db.query(models.User).filter(models.User.email == current_user.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    blog = db.query(models.Blog).filter(models.Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found.")

    comment = db.query(models.Comment).filter(models.Comment.id == comment_id, models.Comment.blog_id == blog.id).first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found.")

    if comment.reply_of_comment == None:
        comment.reply_of_comment = request.text
    else:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="You can only reply to one comment.")
    db.commit()
    db.refresh(comment)

    return {"Comment": "Blog comment reply successfully"}

def delete_comment(blog_id: int, comment_id: int, db: Session, current_user: str):
    """
            Allows a user to delete a specific comment from a blog post.

            Args:
                blog_id (int): The ID of the blog.
                comment_id (int): The ID of the comment to be deleted.
                db (Session): The database session for database operations.
                current_user (str): The email of the current user.

            Returns:
                dict: A message confirming the comment has been deleted."""
    user = db.query(models.User).filter(models.User.email == current_user.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    blog = db.query(models.Blog).filter(models.Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found.")
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id, models.Comment.blog_id == blog.id).first()

    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found.")

    if blog.user_id != user.id and comment.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not allowed to delete comments on this blog.")

    db.delete(comment)
    db.commit()
    return {"Comment": "Blog comment delete successfully"}


def delete_image(image_id, db: Session, current_user: str):
    """
            Allows a user to delete a specific Image using its ID.

            Args:
                image_id (int): The ID of the image to be deleted.
                db (Session): The database session for database operations.
                current_user (str): The email of the current user.

            Returns:
                dict: A message confirming the comment has been deleted."""
    user = db.query(models.User).filter(models.User.email == current_user.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    image = db.query(models.Image).filter(models.Image.id == image_id).first()
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found.")

    image_can_not_delete = db.query(models.Image).filter(models.Image.id == image_id, models.Image.user_id == user.id).first()
    if not image_can_not_delete:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="You can not delete this image.")

    db.delete(image)
    db.commit()
    return {"message": "Image deleted successfully"}

def add_images(blog_id: int, images: List[UploadFile], db: Session, current_user: str):
    """
            Allows a user to add images to a specific blog.

            Args:
                blog_id (int): The ID of the blog.
                images (List[UploadFile]): A list of image files to be uploaded.
                db (Session): The database session for database operations.
                current_user (str): The email of the current user.

            Returns:dict: A message confirming the number of images added."""

    user = db.query(models.User).filter(models.User.email == current_user.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    blog = db.query(models.Blog).filter(models.Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found.")

    #Check the user is add image or not
    user_not_add_image = db.query(models.Blog).filter(models.Blog.id == blog_id, models.Blog.user_id == user.id).first()
    if not user_not_add_image:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="You can not add images to this blog.")

    image_objects = []

    for image in images:
        image_url = upload_image(image)
        if image_url:
            image_obj = models.Image(
                image_url=image_url,
                user_id=user.id,
                blog_id=blog_id
            )
            image_objects.append(image_obj)

    if not image_objects:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="No images provided.")
    db.add_all(image_objects)
    db.commit()
    for image in image_objects:
        db.refresh(image)

    return {"message": f"{len(image_objects)} image(s) added successfully"}




