from fastapi import FastAPI, Depends, Response, status
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session

from typing import List

from sqlalchemy.sql.functions import user

from .schemas import Blog, ShowBlog, User, ShowUser
from .database import engine, SessionLocal
from .hashing import Hash
from . import models

app = FastAPI()

models.Base.metadata.create_all(engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post('/blog', tags=['blog'], status_code=status.HTTP_201_CREATED)
def create(request: Blog, db: Session = Depends(get_db)):
    new_blog = models.Blog(title=request.title, body=request.body, user_id =1)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog

@app.get('/blog', tags=['blog'], response_model=List[ShowBlog])
def get_all_blogs(db: Session = Depends(get_db)):
    blogs = db.query(models.Blog).all()
    return blogs

@app.delete('/blog/{id}', tags=['blog'], status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id, db: Session=Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id)
    if not blog.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=(f'Blog {id} ist not found'))
    
    blog.delete(synchronize_session=False)
    db.commit()
    return 'done'

@app.put('/blog/{id}', tags=['blog'], status_code=status.HTTP_202_ACCEPTED)
def update(id, request: Blog, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id)
    if not blog.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=(f'Blog {id} ist not found'))
    blog.update(request.dict())
    db.commit()
    
    return 'updated'

@app.get('/blog/{id}', tags=['blog'], status_code=200, response_model=ShowBlog)
def show(id, response:Response ,db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id==id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail={'detail': f'{id} is not avalible'})
    
    return blog

@app.post('/user', tags=['users'], response_model=ShowUser)
def create_user(request: User, db: Session = Depends(get_db)):
    
    new_user = models.User(name=request.name, email=request.email, password=Hash.bcrypt(request.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get('/user/{id}', tags=['users'], response_model=ShowUser)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=(f'User {id} ist not found'))
    
    return user