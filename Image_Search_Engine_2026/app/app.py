import os
import time
from flask import Flask, request, render_template, jsonify, send_from_directory, session, redirect, url_for
from functools import wraps
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_limiter.errors import RateLimitExceeded
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
from datetime import datetime, timedelta
import hashlib
import matplotlib

from db import init_db, verify_credentials, log_search, get_search_history
from app_utils import extract_combined_model_features, load_features_dict, search_similar_images, generate_rp_curve
matplotlib.use('Agg')

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[],
    storage_uri="memory://"
)

@app.errorhandler(RateLimitExceeded)
def handle_rate_limit(e):
    return jsonify({'error': 'Rate limit exceeded. Please wait before retrying.'}), 429
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['SESSION_PERMANENT'] = True

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)

secret = os.environ.get("SECRET_KEY")

if not secret:
    raise RuntimeError("SECRET_KEY is not set")

app.secret_key = secret

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
MAGIC_BYTES = {
    b'\xff\xd8\xff': 'jpeg',
    b'\x89PNG\r\n\x1a\n': 'png',
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_real_image(file_stream):
    header = file_stream.read(8)
    file_stream.seek(0)
    return any(header[:len(magic)] == magic for magic in MAGIC_BYTES)

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
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    remember = request.form.get('remember') == 'on'

    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password required'}), 400

    if verify_credentials(username, password):
        session.permanent = remember
        session['user'] = username
        # rediriger vers la page principale
        return redirect(url_for('index'))

    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/upload', methods=['POST'])
@login_required
@limiter.limit("10 per minute")
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']

    if file and allowed_file(file.filename) and is_real_image(file):
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
@limiter.limit("10 per minute")
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
    
    t0 = time.time()
    features_target = extract_combined_model_features(file_path, model_names=model_names)
    features_db = load_features_dict(model_names=model_names)

    images_proches, predicted_class = search_similar_images(features_target, features_db, topn=topn, dist_metric=dist_metric)
    rp_img_path = generate_rp_curve(specified_class, predicted_class, images_proches, filename)
    elapsed_ms = int((time.time() - t0) * 1000)

    try:
        log_search(
            username=session['user'],
            filename=filename,
            models_used=model_names,
            dist_metric=dist_metric,
            class_filter=specified_class,
            topn=topn,
            result_images=images_proches,
            predicted_class=predicted_class,
            execution_time_ms=elapsed_ms,
        )
    except Exception as e:
        print(f"[DB] log_search failed: {e}")

    # -----------------------------------------------------------------------------------------------
    # Envoi des résultats au frontend
    return jsonify({
        'filename': os.path.basename(file_path),
        'topn_similar_images': images_proches,
        'rp_curve': rp_img_path,
        'predicted_class': predicted_class,
        'specified_class': specified_class
    })

@app.route('/history', methods=['GET'])
@login_required
def history():
    limit = min(request.args.get('limit', 50, type=int), 200)
    return jsonify(get_search_history(session['user'], limit))


def deep_update(d, u):
    for k, v in u.items():
        if isinstance(v, dict) and isinstance(d.get(k), dict):
            deep_update(d[k], v)
        else:
            d[k] = v

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=8080)
