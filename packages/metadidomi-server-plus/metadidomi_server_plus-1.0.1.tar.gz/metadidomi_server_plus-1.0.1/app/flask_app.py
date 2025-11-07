from flask import Flask, render_template, send_from_directory, jsonify, request, redirect, url_for, g, session, make_response
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import socket, os, json, logging, time, threading, sqlite3
import urllib.parse
from datetime import datetime, timedelta
import bcrypt
import uuid
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Configuration logging pour la production
mode = 'production'
logging.basicConfig(level=logging.INFO)
logging.getLogger('flask.app').setLevel(logging.INFO)

# Logger persistant Metadidomi
log_path = os.path.join(os.path.dirname(__file__), '..', 'logs.txt')
log_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
file_handler = logging.FileHandler(log_path, encoding='utf-8')
file_handler.setFormatter(log_formatter)
logger = logging.getLogger('metadidomi')
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    logger.addHandler(file_handler)

SETTINGS_PATH = os.path.join(os.path.dirname(__file__), '..', 'cloud_settings.json')

# CORS strict pour la production
cors_origins = ["https://votre-domaine.com"]
CORS(app, origins=cors_origins, supports_credentials=True)

UPLOADS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'web_uploads'))
DOWNLOAD_LOG = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'download_history.txt'))
os.makedirs(UPLOADS_DIR, exist_ok=True)

connected_users = {}
USERS_LOCK = threading.Lock()

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'file_stats.db')

def ensure_db():
    if not os.path.exists(DB_PATH):
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS file_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT,
                action TEXT,
                ip TEXT,
                duration REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_id TEXT
            )''')
            conn.execute('''CREATE TABLE IF NOT EXISTS file_user_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT,
                action TEXT,
                user_id TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(filename, action, user_id)
            )''')
            conn.commit()
ensure_db()

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DB_PATH)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Ajout du champ user_id à la table
with sqlite3.connect(DB_PATH) as conn:
    try:
        conn.execute('ALTER TABLE file_stats ADD COLUMN user_id TEXT')
    except Exception:
        pass
    conn.commit()

def cleanup_users():
    while True:
        now = time.time()
        with USERS_LOCK:
            to_remove = [ip for ip, last in connected_users.items() if now - last > 60]
            for ip in to_remove:
                del connected_users[ip]
        socketio.emit('users_update', list(connected_users.keys()))
        time.sleep(30)

threading.Thread(target=cleanup_users, daemon=True).start()

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return '127.0.0.1'

def get_hostname():
    env = os.environ.get('METADIDOMI_HOSTNAME')
    if env: return env
    try:
        with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if 'hostname' in data and data['hostname']:
                return data['hostname']
    except Exception:
        pass
    return socket.gethostname()

HOSTNAME = get_hostname()

@app.route("/hostname")
def api_hostname():
    return {"hostname": HOSTNAME}

@app.route("/set_hostname", methods=["POST"])
def api_set_hostname():
    new_hostname = request.get_json(force=True)
    global HOSTNAME
    os.environ["METADIDOMI_HOSTNAME"] = new_hostname
    try:
        with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
            json.dump({'hostname': new_hostname}, f)
    except Exception:
        pass
    HOSTNAME = new_hostname
    return {"hostname": HOSTNAME}

@app.route("/")
def index():
    ip = get_local_ip()
    # Liste les fichiers du dossier web_uploads
    try:
        files = []
        for fname in os.listdir(UPLOADS_DIR):
            fpath = os.path.join(UPLOADS_DIR, fname)
            if os.path.isfile(fpath):
                files.append(fname)
    except Exception:
        files = []
    file_links = ''
    for f in files:
        file_links += f"<li><a href='/download/{f}' target='_blank'>{f}</a></li>"
    return f"""
    <html><head><title>Metadidomi Server Plus</title></head><body>
    <h1>Bienvenue dans Metadidomi Server Plus <span style='color:#007bff;font-size:0.7em'></span></h1>
    </body></html>"""

@app.route('/files', methods=['GET', 'POST'])
def files_list():
    import datetime
    if request.method == 'POST':
        f = request.files.get('file')
        if f and f.filename:
            save_path = os.path.join(UPLOADS_DIR, f.filename)
            f.save(save_path)
            socketio.emit('files_update', get_files_list())
            return redirect(url_for('files_list'))
    files = []
    for fname in os.listdir(UPLOADS_DIR):
        fpath = os.path.join(UPLOADS_DIR, fname)
        if os.path.isfile(fpath):
            stat = os.stat(fpath)
            files.append({
                'name': fname,
                'size': stat.st_size,
                'mtime': datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%d/%m/%Y %H:%M')
            })
    ip = get_local_ip()
    return render_template('cloud_files.html', files=files, hostname=HOSTNAME, ip=ip)

# Ajoute une route API pour obtenir la liste des fichiers (JSON)
@app.route('/api/files')
def api_files():
    import datetime
    folder = request.args.get('folder')
    # Si folder est None ou 'Root', on liste le dossier racine
    if not folder or folder == 'Root':
        base_dir = UPLOADS_DIR
    else:
        # On construit le chemin absolu à partir de UPLOADS_DIR
        base_dir = os.path.join(UPLOADS_DIR, folder)
        if not os.path.isdir(base_dir):
            return jsonify({'files': []})
    files = []
    db = get_db()
    for fname in os.listdir(base_dir):
        fpath = os.path.join(base_dir, fname)
        if os.path.isfile(fpath):
            stat = os.stat(fpath)
            cur = db.execute('SELECT COUNT(*) FROM file_user_actions WHERE filename=? AND action="view"', (fname,))
            views = cur.fetchone()[0]
            cur = db.execute('SELECT COUNT(*) FROM file_user_actions WHERE filename=? AND action="download"', (fname,))
            downloads = cur.fetchone()[0]
            cur = db.execute('SELECT COUNT(*) FROM file_user_actions WHERE filename=? AND action="play"', (fname,))
            plays = cur.fetchone()[0]
            files.append({
                'name': fname,
                'size': stat.st_size,
                'mtime': datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%d/%m/%Y %H:%M'),
                'views': views,
                'downloads': downloads,
                'plays': plays
            })
    return jsonify({'files': files})

def get_files_list():
    import datetime
    try:
        files = []
        for fname in os.listdir(UPLOADS_DIR):
            fpath = os.path.join(UPLOADS_DIR, fname)
            if os.path.isfile(fpath):
                stat = os.stat(fpath)
                files.append({
                    'name': fname,
                    'size': stat.st_size,
                    'mtime': datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%d/%m/%Y %H:%M')
                })
    except Exception:
        files = []
    return files

@app.route('/files/<filename>')
def download_file(filename):
    if '..' in filename or filename.startswith('/') or filename.startswith('\\'):
        return jsonify({'error': 'Nom de fichier invalide'}), 400
    file_path = os.path.join(UPLOADS_DIR, filename)
    if not os.path.isfile(file_path):
        return jsonify({'error': 'Fichier non trouvé'}), 404
    ip = request.remote_addr
    log_download(ip, filename)
    socketio.emit('download_event', {'ip': ip, 'filename': filename, 'time': time.strftime('%d/%m/%Y %H:%M:%S')})
    return send_from_directory(UPLOADS_DIR, filename, as_attachment=True)

@app.route('/download/<path:filename>')
def download_file_compat(filename):
    safe_name = os.path.basename(urllib.parse.unquote(filename))
    file_path = os.path.join(UPLOADS_DIR, safe_name)
    if not os.path.isfile(file_path):
        return jsonify({'error': 'Fichier non trouvé'}), 404
    ip = request.remote_addr
    log_download(ip, safe_name)
    socketio.emit('download_event', {'ip': ip, 'filename': safe_name, 'time': time.strftime('%d/%m/%Y %H:%M:%S')})
    return send_from_directory(UPLOADS_DIR, safe_name, as_attachment=True)

def log_download(ip, filename):
    entry = f"{time.strftime('%d/%m/%Y %H:%M:%S')} | {ip} | {filename}"
    with open(DOWNLOAD_LOG, 'a', encoding='utf-8') as f:
        f.write(entry + '\n')

@app.route('/api/download_history')
def api_download_history():
    if not os.path.exists(DOWNLOAD_LOG):
        return jsonify({'history': []})
    with open(DOWNLOAD_LOG, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    return jsonify({'history': [line.strip() for line in lines[-100:]]})

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    import sqlite3
    safe_name = os.path.basename(urllib.parse.unquote(filename))
    fpath = os.path.join(UPLOADS_DIR, safe_name)
    if os.path.isfile(fpath):
        os.remove(fpath)
        with sqlite3.connect(DB_PATH) as conn:
            tables = [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
            for table in tables:
                cols_info = conn.execute(f"PRAGMA table_info({table})").fetchall()
                text_cols = [col[1] for col in cols_info if col[2] in ('TEXT', 'VARCHAR', 'CHAR')]
                for col in text_cols:
                    try:
                        conn.execute(f"DELETE FROM {table} WHERE {col} LIKE ?", (f"%{safe_name}%",))
                    except Exception:
                        pass
            conn.commit()
        socketio.emit('files_update', get_files_list())
    return redirect(url_for('files_list'))

@socketio.on('connect')
def handle_connect():
    ip = request.remote_addr
    with USERS_LOCK:
        connected_users[ip] = time.time()
    emit('users_update', list(connected_users.keys()), broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    ip = request.remote_addr
    with USERS_LOCK:
        if ip in connected_users:
            del connected_users[ip]
    emit('users_update', list(connected_users.keys()), broadcast=True)

@socketio.on('ping_user')
def handle_ping():
    ip = request.remote_addr
    with USERS_LOCK:
        connected_users[ip] = time.time()
    emit('users_update', list(connected_users.keys()), broadcast=True)

# Ajout d'une fonction utilitaire pour identifier l'utilisateur (par IP + cookie simple)
def get_user_id():
    return request.remote_addr

@app.route('/api/increment_view', methods=['POST'])
def api_increment_view():
    data = request.get_json(force=True)
    name = data.get('name')
    type_ = data.get('type')
    duration = float(data.get('duration', 0))
    user_id = get_user_id()
    if not name or not type_:
        return jsonify({'error': 'missing name/type'}), 400
    db = get_db()
    # Détermine l'action
    if type_ == 'download':
        action = 'download'
    elif type_ == 'play' or type_ == 'audio':
        action = 'play'
    else:
        action = 'view'
    # Vérifie si ce user a déjà fait cette action sur ce fichier
    cur = db.execute('SELECT COUNT(*) FROM file_user_actions WHERE filename=? AND action=? AND user_id=?',
                     (name, action, user_id))
    already = cur.fetchone()[0]
    if already == 0:
        db.execute('INSERT INTO file_user_actions (filename, action, user_id) VALUES (?, ?, ?)', (name, action, user_id))
        db.execute('INSERT INTO file_stats (filename, action, ip, duration, user_id) VALUES (?, ?, ?, ?, ?)', (name, action, request.remote_addr, duration, user_id))
        db.commit()
    # Compteurs
    cur = db.execute('SELECT COUNT(*) FROM file_user_actions WHERE filename=? AND action="view"', (name,))
    views = cur.fetchone()[0]
    cur = db.execute('SELECT COUNT(*) FROM file_user_actions WHERE filename=? AND action="download"', (name,))
    downloads = cur.fetchone()[0]
    cur = db.execute('SELECT COUNT(*) FROM file_user_actions WHERE filename=? AND action="play"', (name,))
    plays = cur.fetchone()[0]
    return jsonify({'ok': True, 'views': views, 'downloads': downloads, 'plays': plays})

# Route pour servir l'interface Cloud Drive
@app.route('/cloud_drive')
def cloud_drive():
    return render_template('cloud_drive.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    return render_template('login.html', error=error)

@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/users_list')
def users_list():
    return render_template('usersList.html')

@app.route('/wikipedia')
def wikipedia_summary():
    from az import wikipedia_search
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'summary': "Aucun mot-clé fourni."}), 400
    result = wikipedia_search(query)
    if not result:
        return jsonify({'summary': "Aucun résumé trouvé ou erreur Wikipedia."})
    # Si result est une liste, on joint les phrases
    if isinstance(result, list):
        summary = ". ".join(result)
    else:
        summary = str(result)
    return jsonify({'summary': summary})

@app.route('/az_search')
def az_search():
    # Sert le template de recherche AZ avec des variables factices pour éviter l'erreur Jinja2
    class FakeStats:
        unique_terms = 0
        total_size = 0
    class FakeIndexer:
        doc_count = 0
        stats = FakeStats()
    return render_template(
        'search_template.html',
        q='',
        wiki_results=[],
        results=[],
        total=0,
        page=1,
        per_page=20,
        suggestions=[],
        indexer=FakeIndexer()
    )

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Données JSON manquantes'}), 400
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'error': 'Email et mot de passe requis'}), 400
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), '..', 'users.db'))
    c = conn.cursor()
    try:
        c.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = c.fetchone()
        if not user:
            return jsonify({'error': 'Email ou mot de passe incorrect'}), 401
        user_dict = {
            'id': user[0],
            'name': user[1],
            'email': user[2],
            'password': user[3],
            'created_at': user[4],
            'last_login': user[5],
            'is_active': bool(user[6]),
            'login_count': user[7]
        }
        if not user_dict['is_active']:
            return jsonify({'error': 'Ce compte est désactivé'}), 401
        if not bcrypt.checkpw(password.encode('utf-8'), user_dict['password'].encode('utf-8')):
            return jsonify({'error': 'Email ou mot de passe incorrect'}), 401
        # Mettre à jour last_login et login_count
        last_login = datetime.now().isoformat()
        login_count = user_dict['login_count'] + 1
        c.execute('UPDATE users SET last_login = ?, login_count = ? WHERE id = ?', (last_login, login_count, user_dict['id']))
        conn.commit()
        session['user_id'] = user_dict['id']
        session.permanent = True
        user_dict.pop('password')
        user_dict['last_login'] = last_login
        user_dict['login_count'] = login_count
        return jsonify({'message': 'Connexion réussie', 'user': user_dict})
    except Exception as e:
        return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500
    finally:
        conn.close()

from app.routes import bp
app.register_blueprint(bp)

if __name__ == "__main__":
    ip = get_local_ip()
    print(f"Serveur démarré sur : https://{ip}:5000")
    socketio.run(app, host="0.0.0.0", port=5000, ssl_context=("cert.pem", "key.pem"), allow_unsafe_werkzeug=True)
