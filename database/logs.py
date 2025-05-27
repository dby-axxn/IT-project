from sqlalchemy import *
from .controller import Session, engine
from models import Log, Base
import time

def get_logs(
    content : str = None,
    levels : list = None,
    from_timestamp: int = None,
    to_timstamp: int = None
) -> list:

    logs = select(Log)

    if levels is not None:
        logs = logs.where(Log.level in levels)


    return list(Session.scalars(logs))


def add_log(content : str, level : str):
    """
    content : str
    level : [WARNING, INFO, ERROR, DEBUG, SOMETHING CUSTOM]
    """

    log = Log(
        content = content,
        level = level,
    )

    print(content)

    Session.add(log)
    Session.commit()

    return log

Base.metadata.create_all(engine)