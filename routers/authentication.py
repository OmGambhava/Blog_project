from fastapi import Depends, status, APIRouter, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import database, models
import newtoken
from hashing import Hash


router = APIRouter(tags=["Authentication"])

@router.post("/login")
def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    #This function allows a user to log in by verifying their username and password, and then generating an access token.
    user = db.query(models.User).filter(models.User.username == request.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found.")

    if not Hash.verify(user.password, request.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Incorrect Password")

    access_token = newtoken.create_access_token(data={"sub": user.email})

    return {"access_token": access_token, "token_type": "bearer"}
