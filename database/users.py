from sqlalchemy import *
from .controller import Session, engine 
from models import User 
import datetime 

def get_user(
    email: str = None, 
    id: int = None,    
    _session = Session
) -> User | None:

    query = select(User)

    if email is not None:
        query = query.where(User.email == str(email)) 

    if id is not None:
        query = query.where(User.id == id)

    try:
        result_user = _session.execute(query).scalars().first()
    except Exception as e: 
        _session.rollback()
        print(f"Error fetching user: {e}") 
        return None # 

    return result_user 

def add_user(
    email: str,
    password: str
) -> User:
    user = User(
        email=email, 
        password=password,
    )

    Session.add(user)
    try:
        Session.commit()
    except Exception as e: 
        Session.rollback()
        print(f"Error adding user: {e}") 
        raise e 

    return user

def __drop_table():
    User.__table__.drop(engine)