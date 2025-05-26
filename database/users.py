from sqlalchemy import *
from .controller import Session, engine
from models import User
import time
import datetime

def get_user(
    username : str = None,
    id : str = None,
    _session = Session) -> User | None:

    users = select(User)

    if username is not None:
        users = users.where(User.username == str(username))

    if id is not None:
        users = users.where(User.id == id)

    try:
        result = list(_session.scalars(users))
    except:
        Session.rollback()
        result = list(_session.scalars(users))

    if len(result) == 0:
        return None

    return result[0]

def add_user(
    username : str,
    password : str
) -> User:
    user = User(
        username = username,
        password = password,
    )

    Session.add(user)
    Session.commit()


    return user

def __drop_table():
    User.__table__.drop(engine)