import mysql.connector
import bcrypt
import os

def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "db"),
        user=os.getenv("DB_USER", "appuser"),
        password=os.getenv("DB_PASSWORD", "apppass"),
        database=os.getenv("DB_NAME", "appdb")
    )

def init_db():

    db = get_db()
    cursor = db.cursor()

    admin_username = os.getenv("ADMIN_USERNAME")
    admin_password = os.getenv("ADMIN_PASSWORD")

    if not admin_username or not admin_password:
        raise RuntimeError("ADMIN_USERNAME and ADMIN_PASSWORD must be set in environment variables")
        
    # hash du nouveau password à chaque start
    password_hash = bcrypt.hashpw(
        admin_password.encode(),
        bcrypt.gensalt()
    ).decode()

    cursor.execute("""
        INSERT INTO users (username, password_hash, role)
        VALUES (%s, %s, 'admin')
        ON DUPLICATE KEY UPDATE
            password_hash = VALUES(password_hash),
            role = 'admin'
    """, (admin_username, password_hash))

    db.commit()
    cursor.close()
    db.close()

    print("Admin password overridden")

def verify_credentials(username, password):

    print(f"Verifying credentials for user: {username}, password: {password}")
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
    user = cursor.fetchone()
    cursor.close()
    db.close()
    
    if not user:
        return False
    
    return bcrypt.checkpw(
        password.encode(),
        user["password_hash"].encode()
    )