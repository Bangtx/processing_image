from fastapi import APIRouter
from model.user import User
from schemas import user as userschemas
from typing import List
from playhouse.shortcuts import model_to_dict
from schemas.login import Login

router = APIRouter()

@router.get('/read', response_model=List[userschemas.User])
def get_account():
    return list(User.select())

@router.post('/create')
def create_account(user:userschemas.UserCreate):
    return model_to_dict(User.create(**user.dict()))

@router.post('/login')
def sign_in(user:Login):
    """User login"""
    user = user.dict()
    query = User.select().where(
        (User.code == user['code']) & (User.password == user['password'])).dicts()
    query_len = list(query)
    if len(query_len):
        return {"code": 200, "data": query_len}
    else:
        return {"code": 400, "data": query_len}
