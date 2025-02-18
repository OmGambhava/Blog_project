from fastapi import APIRouter, Depends, status, BackgroundTasks
from sqlalchemy.orm import Session
import database, schemas
import oauth2
from services import user

router = APIRouter(prefix="/user", tags=["users"])
get_db = database.get_db

@router.post("/", status_code=status.HTTP_201_CREATED)
def create(request: schemas.User, db: Session = Depends(get_db)):
    """Endpoint to create a new User."""
    return user.create(request , db)

@router.get("/{id}", response_model=schemas.ShowUser)
def get_user(id : int, db: Session = Depends(get_db)):
    """Endpoint to get a User by their ID."""
    return user.show(id, db)

@router.patch("/", response_model=dict)
def reset_password(request: schemas.ResetPassword, db: Session = Depends(get_db), current_user: schemas.ShowUser = Depends(
    oauth2.get_current_user)):
    """Endpoint to allow the current user to reset their password."""
    return user.reset_password(request, db, current_user)

@router.post("/forgot_password", status_code=status.HTTP_200_OK)
def forgot_password(request: schemas.TokenData, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Endpoint to initiate a password reset by sending a token."""
    return user.forgot_password(request, background_tasks, db)

@router.post("/reset_password/{token}", status_code=status.HTTP_200_OK)
def reset_password(request: schemas.ForgotPassword, token: str, db: Session = Depends(get_db)):
    """Endpoint to reset a user password using a token."""
    return user.forgot_old_password(request, token, db)

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(db: Session = Depends(get_db), current_user: schemas.ShowUser = Depends(oauth2.get_current_user)):
    """Endpoint to delete the current user account."""
    return user.delete(db, current_user)