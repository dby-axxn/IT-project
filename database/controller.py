from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sys import argv



###### DATABASE ######
local_path = "sqlite:///base.db"
# global_path = config_parser.database_connection_string


def create_local_engine():
    selected_path = local_path
    # if len(argv) > 1 and argv[1] == "--prod":
        # selected_path = global_path

    return create_engine(selected_path)


def create_session(engine):
    session_factory = sessionmaker(bind=engine)
    return scoped_session(session_factory)


engine = create_local_engine()
session_factory = sessionmaker(bind=engine)
MainSession = scoped_session(session_factory)

Session = MainSession()