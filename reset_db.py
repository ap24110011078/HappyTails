import os
import sqlite3

import mysql.connector

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'petpaglus.db')

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'saketh@123',
    'database': 'petpaglus_db'
}


def reset_database():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute('SET FOREIGN_KEY_CHECKS = 0;')
        cursor.execute('TRUNCATE TABLE adoption;')
        cursor.execute('TRUNCATE TABLE adopters;')
        cursor.execute('TRUNCATE TABLE pets;')
        cursor.execute('SET FOREIGN_KEY_CHECKS = 1;')
        conn.commit()
        print('Successfully removed all data! The database is now empty and ready for new data.')
    except mysql.connector.Error:
        conn = sqlite3.connect(DB_PATH)
        conn.execute('PRAGMA foreign_keys = OFF')
        conn.execute('DELETE FROM adoption')
        conn.execute('DELETE FROM adopters')
        conn.execute('DELETE FROM pets')
        conn.commit()
        conn.close()
        print('SQLite database reset successfully.')
    finally:
        if 'conn' in locals() and conn:
            try:
                if hasattr(conn, 'is_connected') and conn.is_connected():
                    conn.close()
                else:
                    conn.close()
            except Exception:
                pass


if __name__ == '__main__':
    reset_database()
