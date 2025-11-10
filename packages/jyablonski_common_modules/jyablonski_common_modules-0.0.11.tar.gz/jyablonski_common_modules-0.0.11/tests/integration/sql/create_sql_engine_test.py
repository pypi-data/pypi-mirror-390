from sqlalchemy.engine.base import Engine

from jyablonski_common_modules.sql import create_sql_engine

def test_create_sql_engine_success():
    conn = create_sql_engine(
        database="postgres",
        schema="sales_source",
        user="postgres",
        password="postgres",
        host="postgres",
    )

    expected_url = "postgresql+psycopg2://postgres:***@postgres:5432/postgres"
    
    assert str(conn.url) == expected_url
