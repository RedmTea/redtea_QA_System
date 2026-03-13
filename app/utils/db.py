from sqlalchemy import create_engine
from app.config import Config
from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from sqlalchemy.exc import SQLAlchemyError
from app.models import *
from app.models.base import Base

from app.utils.logger import get_logger

logger = get_logger(__name__)


def get_database_url():
    return (
        f"mysql+pymysql://{Config.DB_USER}:{Config.DB_PASSWORD}"
        f"@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}?charset={Config.DB_CHARSET}"
    )


print(f"数据库连接URL: {get_database_url()}")

engine = create_engine(
    get_database_url(),
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,
)

Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)


@contextmanager
def db_session():
    session = Session()
    try:
        yield session
    except Exception as e:
        logger.error(f"数据库会话错误:{e}")
        raise
    finally:
        session.close()


@contextmanager
def db_transaction():
    session = Session()
    try:
        yield session
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"数据库事务错误:{e}")
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"数据库会话错误:{e}")
        raise
    finally:
        session.close()


def init_db():
    try:
        Base.metadata.create_all(engine)
    except Exception as e:
        logger.error(f"初始化数据库失败:{e}")
        raise
