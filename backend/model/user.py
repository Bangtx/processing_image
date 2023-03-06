from model.base import BaseModel
from peewee import CharField, IntegerField, AnyField

class User(BaseModel):
    code= CharField()
    password = CharField()
    name = CharField()
    class_ids = AnyField()
    role = IntegerField()

    class Meta:
        db_table = 'user'