from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship, backref
from sqlalchemy import *
import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    auth_date = Column(String, default=datetime.datetime.utcnow)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)

class Activities(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(String, default=datetime.datetime.utcnow)
    content = Column(String, nullable=False)

class Anomalies(Base):
    __tablename__ = "anomalies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(String, default=datetime.datetime.utcnow)
    content = Column(String, nullable=False)
    level = Column(String, nullable=False)


class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(String, nullable=False)
    level = Column(String, nullable=False)
    date = Column(String, default=datetime.datetime.utcnow)