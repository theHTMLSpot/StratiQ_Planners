import sqlite3

def get_db_connection():
    """Establish a connection to the SQLite database and return the connection object."""
    conn = sqlite3.connect('database.db')
    return conn