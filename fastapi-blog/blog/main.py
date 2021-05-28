from fastapi import FastAPI

from .routers import blog, user, login
from .database import engine
from . import models

app = FastAPI()

models.Base.metadata.create_all(engine)

app.include_router(login.router)
app.include_router(blog.router)
app.include_router(user.router)