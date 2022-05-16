import app_logger

from sqlalchemy.orm import sessionmaker
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base


SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
meta = MetaData(engine)
Base = declarative_base()


class SQL:
    def __init__(self):
        self.logger = app_logger.get_logger(__name__)

    def add_task(self, username, info):
        tasks_table = Table('tasks', meta, autoload=True)
        try:
            with engine.connect() as con:
                sthm = insert(tasks_table).values(username=username, info=info)
                rs = con.execute(sthm)
            return
        except Exception as ex:
            self.logger.error(str(ex))

    def get_tasks(self):
        tasks_table = Table('tasks', meta, autoload=True)
        try:
            with engine.connect() as con:
                sthm = select([tasks_table.c.username, tasks_table.c.info])
                rs = con.execute(sthm)
                return rs.fetchall()
        except Exception as ex:
            self.logger.error(str(ex))
