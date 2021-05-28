from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session

from ..schemas import ShowUser, User
from ..hashing import Hash
from ..database import get_db
from .. import models


router = APIRouter(
    prefix='/user',
    tags=['Users']
)

@router.post('/', response_model=ShowUser)
def create_user(request: User, db: Session = Depends(get_db)):
    
    new_user = models.User(name=request.name, email=request.email, password=Hash.bcrypt(request.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get('/{id}', response_model=ShowUser)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=(f'User {id} ist not found'))
    
    return user