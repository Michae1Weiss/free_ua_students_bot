import os

from peewee import SqliteDatabase

from logconf import get_logger
from settings import DATABASE
from models import database_proxy, MODELS

logger = get_logger(__name__)


def create_database() -> SqliteDatabase:
    """
    Create database and tables.
    :return: SqliteDatabase object
    """
    database = SqliteDatabase(DATABASE)
    database_proxy.initialize(database)
    database.create_tables(MODELS)
    return database


def get_database():
    if os.path.exists(DATABASE):
        logger.info(f"Database '{DATABASE}' already exist. Returning existing db...")
        database = SqliteDatabase(DATABASE)
        database_proxy.initialize(database)
    else:
        logger.info(f"Database '{DATABASE}' does not exist. Creating database...")
        create_database()
        logger.info(f"Database '{DATABASE}' was successfully created. Returning db...")
    database = SqliteDatabase(DATABASE)
    return database
