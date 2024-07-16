import database

def insert_user(name: str, email: str):
    """Insert a new user into the users table."""
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO users (name, email) VALUES (?, ?)
    ''', (name, email))
    conn.commit()
    conn.close()

def get_users():
    """Retrieve all users from the users table."""
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    rows = cursor.fetchall()
    conn.close()
    return rows