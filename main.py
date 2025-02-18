from routers import blog, user, authentication
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from database import engine
import models
app = FastAPI()
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

models.Base.metadata.create_all(engine)
app.include_router(authentication.router)
app.include_router(blog.router)
app.include_router(user.router)