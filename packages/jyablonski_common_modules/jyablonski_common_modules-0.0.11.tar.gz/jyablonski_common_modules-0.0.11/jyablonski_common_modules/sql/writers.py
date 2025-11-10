import logging
import uuid

import pandas as pd
from sqlalchemy import exc, text
from sqlalchemy.engine.base import Connection

# logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def write_to_sql_upsert(
    conn: Connection,
    table: str,
    schema: str,
    df: pd.DataFrame,
    primary_keys: list[str],
    update_timestamp_field: str | None = None,
) -> None:
    """
    Upserts a Pandas DataFrame into a SQL Table.

    If the table doesn't exist, a new one will be created.
    Otherwise, existing rows are updated and new rows are inserted.

    Args:
        conn (Connection): SQLAlchemy connection object.

        table (str): Target table name in the database.

        schema (str): Schema of the target table.

        df (DataFrame): DataFrame to be upserted.

        primary_keys (list[str]): Column(s) representing the primary key.

        update_timestamp_field (str | None): Optional column to specify
            what timestamp field to update when a record is updated.

    Returns:
        None, but upserts the DataFrame into the SQL table.

    Example:
        ``` python
        write_to_sql_upsert(
            conn=postgres_conn,
            schema="sales_source",
            table="sales_data",
            df=sales_data,
            primary_keys=["id"],
        )
        ```
    """
    if df.empty:
        logger.info(f"{table} is empty, skipping SQL upsert.")
        return

    if not all(key in df.columns for key in primary_keys):
        raise ValueError("Not all Primary Key Columns are in the DataFrame")

    try:
        # Check if the table exists
        table_exists = conn.execute(
            text(
                f"""SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE 
                        table_schema = '{schema}'
                        AND table_name = '{table}');
                    """
            )
        ).first()[0]

        if not table_exists:
            df.to_sql(
                name=table, con=conn, schema=schema, if_exists="replace", index=False
            )
            logger.info(f"Created new table {table} with {len(df)} records.")

        else:
            temp_table_name = f"temp_{uuid.uuid4().hex[:6]}"
            df.to_sql(name=temp_table_name, con=conn, schema=schema, index=False)

            primary_keys_sql = ", ".join([f'"{col}"' for col in primary_keys])
            headers_sql_txt = ", ".join([f'"{col}"' for col in df.columns.tolist()])
            update_column_stmt = ", ".join(
                [
                    f'"{col}" = EXCLUDED."{col}"'
                    for col in df.columns
                    if col not in primary_keys and (col != update_timestamp_field)
                ]
            )

            if update_timestamp_field:
                update_column_stmt += f', "{update_timestamp_field}" = NOW()'


            upsert_query = f"""
                ALTER TABLE "{schema}"."{table}" 
                DROP CONSTRAINT IF EXISTS unique_constraint_for_upsert_{table},
                ADD CONSTRAINT unique_constraint_for_upsert_{table} UNIQUE ({primary_keys_sql});

                INSERT INTO "{schema}"."{table}" ({headers_sql_txt})
                SELECT {headers_sql_txt} FROM "{schema}"."{temp_table_name}"
                ON CONFLICT ({primary_keys_sql}) 
                DO UPDATE SET {update_column_stmt};

                DROP TABLE "{schema}"."{temp_table_name}";
            """

            # Execute the upsert query
            conn.execute(text(upsert_query))
            logger.info(f"Upserted {len(df)} records into {table}.")

    except exc.SQLAlchemyError as error:
        logger.error(f"SQL Upsert failed for {table}: {error}")
        if "temp_table_name" in locals():
            conn.execute(text(f'DROP TABLE IF EXISTS "{schema}"."{temp_table_name}";'))
        raise error
