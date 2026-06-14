import mysql.connector
import bcrypt
import torch
import os
import json
import time

def get_db():
    retries = 10  # Nombre de tentatives maximum
    while retries > 0:
        try:
            connection = mysql.connector.connect(
                host=os.getenv("DB_HOST", "db"),
                user=os.getenv("DB_USER", "appuser"),
                password=os.getenv("DB_PASSWORD", "apppass"),
                database=os.getenv("DB_NAME", "appdb")
            )
            return connection
        except mysql.connector.Error as err:
            retries -= 1
            print(f"[DB] MySQL n'est pas encore prêt ({err}). Nouvelle tentative dans 2 secondes... ({retries} essais restants)")
            time.sleep(2)
            
    raise Exception("Impossible de se connecter à la base de données MySQL après plusieurs tentatives.")

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


def log_search(username, file_hash, models_used, dist_metric,
               class_filter, topn, result_images, predicted_class, execution_time_ms):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO search_history
            (username, file_hash, models_used, dist_metric, class_filter,
             topn, result_images, predicted_class, execution_time_ms)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        username,
        file_hash,
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

def find_search_history(username, file_hash, models_used, dist_metric, class_filter, topn):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT result_images, predicted_class
        FROM search_history
        WHERE username = %s AND file_hash = %s AND models_used = %s AND dist_metric = %s
              AND (class_filter <=> %s) AND topn = %s
        ORDER BY searched_at DESC
        LIMIT 1
    """, (username, file_hash, ",".join(sorted(models_used)), dist_metric, class_filter, topn))
    row = cursor.fetchone()
    cursor.close()
    db.close()
    if row:
        return json.loads(row['result_images']), row['predicted_class']
    return None, None

def get_search_history(username, limit=50):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT id, username, file_hash, models_used, dist_metric, class_filter, topn,
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

def log_image_descriptor(file_hash, model_names, descriptor):
    if hasattr(descriptor, "cpu"):
        descriptor_list = [float(x) for x in descriptor.cpu().numpy().flatten()]
    elif hasattr(descriptor, "astype"):
        descriptor_list = descriptor.astype(float).tolist()
    else:
        descriptor_list = [float(x) for x in descriptor]

    descriptor_json = json.dumps(descriptor_list)

    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("""
        INSERT INTO image_descriptors (file_hash, model_name, descriptor)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
            descriptor = VALUES(descriptor),
            updated_at = CURRENT_TIMESTAMP
    """, (file_hash, ",".join(sorted(model_names)), descriptor_json)) # Plus besoin de doubler le json.dumps ici
    
    db.commit()
    cursor.close()
    db.close()

def get_image_descriptor(file_hash, model_names):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT descriptor
        FROM image_descriptors
        WHERE file_hash = %s AND model_name = %s
    """, (file_hash, ",".join(sorted(model_names))))
    row = cursor.fetchone()
    cursor.close()
    db.close()
    
    if row:
        descriptor_list = json.loads(row['descriptor'])
        return torch.tensor(descriptor_list, dtype=torch.float32)
    return None