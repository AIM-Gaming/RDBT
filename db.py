import mysql.connector
from log import debug_print

DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'SQL0202Otown--!',
    'database': 'bible_trivia'
}


def get_db_connection(dictionary=False):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if dictionary:
            return conn, conn.cursor(dictionary=True)
        return conn, conn.cursor()
    except mysql.connector.Error as e:
        debug_print(f"Database connection error: {e}")
        return None, None
