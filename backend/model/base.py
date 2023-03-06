from peewee import Model
from sql_app.database import db


class BaseModel(Model):
    
    class Meta:
        database = db