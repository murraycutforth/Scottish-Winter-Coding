import datetime
import sqlite3

from src.database_functions import execute_query
from src.utils import database_cache_path

def main():

    date = "2023-01-03"
    location = "southeastern-highlands"

    db_path = database_cache_path()
    assert db_path.exists()

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    execute_query(f"SELECT * FROM mwis WHERE (date='{date}' AND location='{location}')", cursor)

    print(cursor.fetchall()[-1])


if __name__ == "__main__":
    main()
