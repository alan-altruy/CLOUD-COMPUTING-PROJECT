import mysql.connector
import bcrypt
import os
import json

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


def log_search(username, filename, models_used, dist_metric,
               class_filter, topn, result_images, predicted_class, execution_time_ms):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO search_history
            (username, filename, models_used, dist_metric, class_filter,
             topn, result_images, predicted_class, execution_time_ms)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        username,
        filename,
        ",".join(sorted(models_used)),
        dist_metric,
        class_filter,
        topn,
        json.dumps(result_images),
        predicted_class,
        execution_time_ms,
    ))
    db.commit()
    cursor.close()
    db.close()


CLASS_NAMES = ["Africa", "Beach", "Buildings", "Buses", "Dinosaurs",
               "Elephants", "Flowers", "Horses", "Mountains", "Food"]

def get_search_history(username, limit=50):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT id, username, filename, models_used, dist_metric, class_filter, topn,
               result_images, predicted_class, execution_time_ms, searched_at
        FROM search_history
        WHERE username = %s
        ORDER BY searched_at DESC
        LIMIT %s
    """, (username, limit))
    rows = cursor.fetchall()
    cursor.close()
    db.close()
    for row in rows:
        row['searched_at'] = row['searched_at'].isoformat()
        row['result_images'] = json.loads(row['result_images'])
        cf = row['class_filter']
        pc = row['predicted_class']
        row['class_filter_name'] = CLASS_NAMES[cf] if cf is not None else None
        row['predicted_class_name'] = CLASS_NAMES[pc] if pc is not None else None
    return rows