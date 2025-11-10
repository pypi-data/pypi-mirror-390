import pandas as pd
from sqlalchemy.engine.base import Connection


def get_feature_flags(connection: Connection, schema: str):
    flags = pd.read_sql_query(
        sql=f"select * from {schema}.feature_flags;", con=connection
    )

    print(f"Retrieving {len(flags)} Feature Flags")
    return flags


def check_feature_flag(flag: str, flags_df: pd.DataFrame) -> bool:
    flags_df = flags_df.query(f"flag == '{flag}'")

    if len(flags_df) > 0 and flags_df["is_enabled"].iloc[0] == 1:
        return True
    else:
        return False
