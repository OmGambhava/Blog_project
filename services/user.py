from fastapi import HTTPException, status, BackgroundTasks, Depends
from starlette.status import HTTP_404_NOT_FOUND

import schemas, models, database, jwt
import newtoken
import hashing
from newtoken import ALGORITHM,SECRET_KEY
from datetime import datetime, timedelta
from fastapi_mail import MessageSchema
from sqlalchemy.orm import Session
from mail import fm

get_db = database.get_db

def create(request: schemas.User, db: Session):
    """
        This function Creates a new use first take the input of name username emai and password and that save into database.

        Args:
            request (schemas.User): The user data to create a new user.
            db (Session): The database session used for transaction management.

        Returns:
            models.User: The newly created user object.
        """
    new_user= models.User(username = request.username, name = request.name, email = request.email, password = hashing.Hash.bcrypt(request.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def show(id: int, db: Session):
    """
    This function get the user details by their ID from the database.

    Args:
        id (int): The id of the user.
        db (Session): The database session used to interact with the database.

    Returns:
        models.User: The user object containing the user detail.
    """
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=f"User with the id {id} is not available")
    return user

def reset_password(request: schemas.ResetPassword, db: Session, current_user: schemas.ShowUser):
    """
        This function resets the password for the current user first it take the old password and password and confirm password than chack
        old password is same or not in the database if it not same than give error other wish chaeck password and confirm password is same or not.

        Args:
            request (schemas.ResetPassword): The request data containing the old passwords, new password, and confirm password.
            db (Session): The database session used to interact with the database.
            current_user (schemas.ShowUser): The current logged-in user.

        Returns:
            dict: A message indicating the password has been reset successfully.
        """
    user = db.query(models.User).filter(models.User.email == current_user.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User not found.")
    if not hashing.Hash.verify(user.password, request.old_password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Incorrect old Password")
    if request.old_password == request.password == request.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="The new password cannot be the same as the old password. Please choose a different password.")

    if request.password != request.confirm_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Incorrect Password and Confirm Password")
    new_hashed_password = hashing.Hash.bcrypt(request.password)
    user.password = new_hashed_password
    db.commit()
    db.refresh(user)

    return {"message": "Password reset successfully"}

def forgot_password(request: schemas.TokenData, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
        This function generates a password reset token for the user and sends an email with a reset link.

        Args:
            request (schemas.TokenData): The request data containing the user email.
            background_tasks (BackgroundTasks): The background task manager to handle sending the email asynchronously.
            db (Session): The database session used to interact with the database.

        Returns:
            dict: A message indicating the password reset email has been sent successfully.
        """
    user = db.query(models.User).filter(models.User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    token_data = {"sub": user.email, "exp": datetime.utcnow() + timedelta(minutes=10)}
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

    reset_link = f"http://127.0.0.1:8000/user/reset_password/{token}"

    subject = "Password Reset Request"
    message = f"Click the following link to reset your password:\n\n{reset_link}"

    message_schema = MessageSchema(
        subject=subject,
        recipients=[request.email],
        body=message,
        subtype="plain"
    )

    try:
        background_tasks.add_task(fm.send_message, message_schema)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to send email: {str(e)}")

    return {"message": "Password reset email sent successfully.",
            "token": token,}

def forgot_old_password(request: schemas.ForgotPassword, token: str, db: Session):
    """
        This function allows the user to reset their password by providing a valid token and take password and confirm password and check both is same or not.

        Args:
            request (schemas.ForgotPassword): The request data containing the password and confirmation.
            token (str): The token used to verify the user's identity and enable password reset.
            db (Session): The database session used to interact with the database.

        Returns:
            dict: A message indicating the password reset was successful.
        """
    user_email = newtoken.verify_token(token, "Invalid token")
    print("User email : ", user_email)

    if isinstance(user_email, schemas.TokenData):
        user_email = user_email.email
    if not user_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid token....")

    user = db.query(models.User).filter(models.User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found.")

    if request.password != request.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="New password and confirm password do not match.")

    hashed_new_password = hashing.Hash.bcrypt(request.password)
    user.password = hashed_new_password
    db.commit()
    db.refresh(user)

    return {"detail": "Password reset successful."}


def delete(db: Session, current_user: schemas.ShowUser):
    """
      This function deletes the current user from the database.

      Args:
          db (Session): The database session used to interact with the database.
          current_user (schemas.ShowUser): The current logged-in user.

      Returns:
          dict: A message indicating the user has been successfully deleted.
      """
    user = db.query(models.User).filter(models.User.email == current_user.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User not found.")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

