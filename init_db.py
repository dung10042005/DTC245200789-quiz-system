
import time
import pymysql
from app import init_db

for attempt in range(10):
    try:
        init_db()
        print("MySQL database initialized successfully", flush=True)
        break
    except pymysql.MySQLError:
        if attempt == 9:
            raise
        print(
            f"MySQL is not ready; retrying ({attempt + 1}/10)",
            flush=True,
        )
        time.sleep(3)
