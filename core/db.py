# core/db.py
import os
import mysql.connector
from mysql.connector import Error


def get_db():
    """
    Returns a new MySQL database connection.
    Raises RuntimeError if connection fails.
    """
    try:
        connection = mysql.connector.connect(
            host=os.getenv("MYSQLHOST"),
            user=os.getenv("MYSQLUSER"),
            password=os.getenv("MYSQLPASSWORD"),
            database=os.getenv("MYSQLDATABASE"),
            port=int(os.getenv("MYSQLPORT", 3306)),
            charset="utf8mb4",
            autocommit=False
        )

        return connection

    except Error as e:
        # Log once; never expose DB internals to client
        print("❌ Database connection failed:", str(e))
        raise RuntimeError("DATABASE_CONNECTION_FAILED")
