from schemas.base import BaseSchemas

class User(BaseSchemas):
    id: int
    code: str 
    name: str 
    password: str 
    class_ids: list 
    role: int 

class UserCreate(BaseSchemas):
    code: str 
    name: str 
    password: str 
    class_ids: list 
    role: int 