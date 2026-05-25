import os
from flask import Flask, request, render_template, jsonify, send_from_directory, session, redirect, url_for
from functools import wraps
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
from datetime import datetime
import hashlib
import matplotlib
from app_utils import extract_combined_model_features, load_features_dict, search_similar_images, generate_rp_curve
matplotlib.use('Agg')

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Secret key nécessaire pour la session (remplacer en production)
app.secret_key = os.environ.get('SECRET_KEY', 'dev_secret_key')

# Fichier simple pour stocker les utilisateurs en clair (à remplacer par une DB plus tard)
USERS_FILE = os.path.join(os.path.dirname(__file__), 'users.json')

import json

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2)

def verify_credentials(email, password):
    users = load_users()
    # users stored as {"email": {"password": "...", "name": "..."}}
    user = users.get(email)
    if not user:
        return False
    return user.get('password') == password


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user' in session:
            return f(*args, **kwargs)
        # If GET request, redirect to login page for browser navigation
        if request.method == 'GET':
            return redirect(url_for('login'))
        # For AJAX/POST requests return JSON 401
        return jsonify({'error': 'Authentication required'}), 401
    return wrapper


#preload_models()

# ==========================================================
# Configuration de l'application
# ==========================================================

# Types de fichiers autorisés
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Dossiers de stockage
upload_folder = 'static/uploads'           # Dossier pour les images téléchargées
image_db_folder = 'static/image.orig'      # Dossier contenant les images de la base
features_folder = 'static/features'        # Dossier pour les fichiers de descripteurs
rp_save_dir = 'static/rp_files'            # Dossier pour enregistrer les fichiers et courbes RP

# ==========================================================
# Fonctions utilitaires pour l'upload d'images
# ==========================================================

# Vérifie si le fichier possède une extension autorisée
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Génère un nouveau nom pour l’image reçue côté serveur afin d’éviter les doublons
def new_image_name(extension='jpg'):
    now = datetime.now().strftime("%Y%m%d%H%M%S%f")
    return f"img_req_{now}.{extension}"

# Calcule le hash de l’image pour vérifier son unicité dans le dossier d’upload
def hash_file(file_stream):
    hasher = hashlib.sha256()
    for chunk in iter(lambda: file_stream.read(4096), b""):
        hasher.update(chunk)
    file_stream.seek(0)
    return hasher.hexdigest()

# ==========================================================
# Routes Flask et lancement de l'application
# ==========================================================

from flask import send_from_directory

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico')

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    # POST: vérifier les identifiants
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')

    if not email or not password:
        return jsonify({'success': False, 'message': 'Username and password required'}), 400

    if verify_credentials(email, password):
        session['user'] = email
        # rediriger vers la page principale
        return redirect(url_for('index'))

    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/upload', methods=['POST'])
@login_required
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']

    if file and allowed_file(file.filename):
        file_hash = hash_file(file)
        for existing_file in os.listdir(upload_folder):
            existing_path = os.path.join(upload_folder, existing_file)
            with open(existing_path, 'rb') as f:
                if hashlib.sha256(f.read()).hexdigest() == file_hash:
                    print(f"Duplicate image found: {existing_file}")
                    return jsonify({'filename': existing_file, 'file_path': existing_path})

        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = secure_filename(new_image_name(ext))
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        print(f"Uploaded file saved to {file_path}")
        return jsonify({'filename': filename, 'file_path': file_path})

    return jsonify({'error': 'Invalid file format'})

@app.route('/delete/<filename>', methods=['POST'])
@login_required
def delete_image(filename):
    file_path = os.path.join(upload_folder, filename)

    if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify({'deleted': True})
    return jsonify({'deleted': False})

@app.route('/search', methods=['POST'])
@login_required
def search():
    filename = request.form.get('filename')
    model_names = sorted(request.form.getlist('descriptor[]'))
    dist_metric = request.form.get('similarity')
    specified_class = None if request.form.get('image_class') == "" else int(request.form.get('image_class'))
    topn = int(request.form.get('topn'))
    file_path = os.path.join(upload_folder, filename)

    # Vérifie si l’image existe dans le dossier 'uploads'
    if not os.path.exists(file_path):
        print("[MYAPP] >> File not found error")
        return jsonify({'error': 'File not found'})

    # ------------------------ Affichage pour vérification des données reçues du formulaire ------------------------
    print(f"[MYAPP] >> File Name: {filename}")
    print(f"[MYAPP] >> Models: {model_names}")
    print(f"[MYAPP] >> Distance Metric: {dist_metric}")
    print(f"[MYAPP] >> Class specified by the user: {specified_class}")
    print(f"[MYAPP] >> Requested Top-N: {topn}")
    # --------------------------------------------------------------------------------------------------------------

    # A COMPLETER :

        # Charger les features des images de la base pour les descripteurs sélectionnés
        # Extraire les features de l’image requête à partir des descripteurs sélectionnés
        # Rechercher les images similaires avec la métrique choisie
        # Pour le calcul rappel/précision : utiliser la classe spécifiée par l’utilisateur, sinon, si l’utilisateur n’a rien spécifié, utiliser la classe prédite
        # Générer l’image de la courbe de Rappel/Précision (RP)

    # ------------------------ A REMPLACER PAR LES RESULTATS DE LA RECHERCHE ------------------------
    
    features_target = extract_combined_model_features(file_path, model_names=model_names)
    features_db = load_features_dict(model_names=model_names)

    images_proches, predicted_class = search_similar_images(features_target, features_db, topn=topn, dist_metric=dist_metric)
    rp_img_path = generate_rp_curve(specified_class, predicted_class, images_proches, filename)

    # -----------------------------------------------------------------------------------------------
    # Envoi des résultats au frontend
    return jsonify({
        'filename': os.path.basename(file_path),
        'topn_similar_images': images_proches,
        'rp_curve': rp_img_path,
        'predicted_class': predicted_class,
        'specified_class': specified_class
    })

def deep_update(d, u):
    for k, v in u.items():
        if isinstance(v, dict) and isinstance(d.get(k), dict):
            deep_update(d[k], v)
        else:
            d[k] = v

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
