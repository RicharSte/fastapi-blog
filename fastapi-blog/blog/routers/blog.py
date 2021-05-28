from typing import List

from fastapi import APIRouter, Depends, status, Response
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session 

from ..schemas import ShowBlog, Blog
from .. import models
from ..database import get_db

router = APIRouter(
    prefix='/blog',
    tags=['Blogs']
)

@router.get('/', response_model=List[ShowBlog])
def get_all_blogs(db: Session = Depends(get_db)):
    blogs = db.query(models.Blog).all()
    return blogs

@router.post('/', status_code=status.HTTP_201_CREATED)
def create(request: Blog, db: Session = Depends(get_db)):
    new_blog = models.Blog(title=request.title, body=request.body, user_id =1)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog

@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id, db: Session=Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id)
    if not blog.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=(f'Blog {id} ist not found'))
    
    blog.delete(synchronize_session=False)
    db.commit()
    return 'done'

@router.put('/{id}', status_code=status.HTTP_202_ACCEPTED)
def update(id, request: Blog, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id)
    if not blog.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=(f'Blog {id} ist not found'))
    blog.update(request.dict())
    db.commit()
    
    return 'updated'

@router.get('/{id}', status_code=200, response_model=ShowBlog)
def show(id, response:Response ,db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id==id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail={'detail': f'{id} is not avalible'})
    
    return blog