import logging
import os

from sqlalchemy import exc, create_engine
from sqlalchemy.engine.base import Engine

logger = logging.getLogger(__name__)


def create_sql_engine(
    schema: str,
    user: str = os.environ.get("RDS_USER", "postgres"),
    password: str = os.environ.get("RDS_PW", "postgres"),
    host: str = os.environ.get("IP", "postgres"),
    database: str = os.environ.get("RDS_DB", "postgres"),
    port: int = os.environ.get("RDS_PORT", 5432),
) -> Engine:
    """
    SQLAlchemy function to define the SQL Driver + connection
    variables needed to connect to the DB.

    This doesn't actually make the connection, use engine.connect()
    or engine.begin() in a context manager to create 1 re-usable connection

    Args:
        schema (str): The Schema in the DB to connect to.

        user (str): The User to connect to the DB with.

        password (str): The Password to connect to the DB with.

        host (str): The Hostname of the DB.

        database (str): The Database to connect to.

        port (int): The Port to connect to the DB with.

    Returns:
        SQL Engine to a specified schema in my PostgreSQL DB

    Example:
        To use this function, do the following:

        ```python

        engine = create_sql_engine("my_schema")
        with engine.begin() as conn:
            result = conn.execute("SELECT * FROM my_table")
            for row in result:
                print(row)
        ```

    """
    db_url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
    try:
        engine = create_engine(
            url=db_url,
            connect_args={
                "options": f"-csearch_path={schema}",
            },
            echo=False,
        )
        logger.info("SQL Engine created")
        return engine
    except exc.SQLAlchemyError as e:
        logger.error(f"SQL Engine failed, {e}")
        raise e
