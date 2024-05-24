from peewee import TextField, IntegerField
from ..connect import db, BaseModel


class Users(BaseModel):
    user_id = IntegerField(unique=True)
    interests = TextField(null=True)
    sources = TextField(null=True)  # Хранение источников в виде строки
    message_id = IntegerField(null=True)  # Хранение ID последнего сообщения

db.create_tables([Users])