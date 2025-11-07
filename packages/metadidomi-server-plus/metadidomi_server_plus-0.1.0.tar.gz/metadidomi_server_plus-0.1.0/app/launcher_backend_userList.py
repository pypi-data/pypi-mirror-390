from flask import Flask, request, jsonify, session, send_from_directory, render_template
import sqlite3
import bcrypt
import uuid
from datetime import datetime, timedelta
import secrets
import os
from flask_socketio import SocketIO, emit

app = Flask(__name__, static_folder='.', static_url_path='')
# Clé secrète toujours définie, même si déjà présente
app.secret_key = os.environ.get('FLASK_SECRET_KEY') or secrets.token_hex(32)
app.config['SESSION_TYPE'] = 'filesystem'
app.permanent_session_lifetime = timedelta(hours=1)

if os.environ.get('HTTPS', 'off').lower() == 'on':
    app.config['SESSION_COOKIE_SAMESITE'] = 'None'
    app.config['SESSION_COOKIE_SECURE'] = True
else:
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_SECURE'] = False

socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# Initialisation de la base de données
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT NOT NULL,
            last_login TEXT,
            is_active BOOLEAN DEFAULT 1,
            login_count INTEGER DEFAULT 0
        )
    ''')
    
    # Créer un utilisateur admin par défaut si la table est vide
    c.execute('SELECT COUNT(*) FROM users')
    if c.fetchone()[0] == 0:
        user_id = str(uuid.uuid4())
        hashed_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        created_at = datetime.now().isoformat()
        
        c.execute('''
            INSERT INTO users (id, name, email, password, created_at, is_active, login_count)
            VALUES (?, ?, ?, ?, ?, 1, 0)
        ''', (user_id, 'Administrateur', 'admin@example.com', hashed_password, created_at))
        print("Utilisateur admin créé: admin@example.com / admin123")
    
    conn.commit()
    conn.close()

# Hash du mot de passe
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Vérification du mot de passe
def verify_password(password, hashed):
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except Exception as e:
        print(f"Erreur de vérification du mot de passe: {e}")
        return False

# Servir la page principale
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

# Routes API
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Données JSON manquantes'}), 400
        
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    
    if not name or not email or not password:
        return jsonify({'error': 'Tous les champs sont requis'}), 400
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    try:
        # Vérifier si l'email existe déjà
        c.execute('SELECT id FROM users WHERE email = ?', (email,))
        if c.fetchone():
            return jsonify({'error': 'Un compte avec cet email existe déjà'}), 400
        
        # Créer l'utilisateur
        user_id = str(uuid.uuid4())
        hashed_password = hash_password(password)
        created_at = datetime.now().isoformat()
        
        c.execute('''
            INSERT INTO users (id, name, email, password, created_at, is_active, login_count)
            VALUES (?, ?, ?, ?, ?, 1, 0)
        ''', (user_id, name, email, hashed_password, created_at))
        
        conn.commit()
        
        return jsonify({'message': 'Compte créé avec succès', 'user_id': user_id}), 201
        
    except Exception as e:
        conn.rollback()
        return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500
    finally:
        conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Données JSON manquantes'}), 400
        
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email et mot de passe requis'}), 400
    
    conn = sqlite3.connect('users.db')
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
        
        # Correction : s'assurer que le hash est bien en bytes
        hashed = user_dict['password']
        if isinstance(hashed, str):
            hashed = hashed.encode('utf-8')
        
        if not bcrypt.checkpw(password.encode('utf-8'), hashed):
            return jsonify({'error': 'Email ou mot de passe incorrect'}), 401
        
        # Mettre à jour last_login et login_count
        last_login = datetime.now().isoformat()
        login_count = user_dict['login_count'] + 1
        
        c.execute('UPDATE users SET last_login = ?, login_count = ? WHERE id = ?', 
                  (last_login, login_count, user_dict['id']))
        
        conn.commit()
        
        # Stocker l'ID utilisateur dans la session
        session['user_id'] = user_dict['id']
        session.permanent = True
        
        user_dict.pop('password')  # Ne pas renvoyer le mot de passe
        user_dict['last_login'] = last_login
        user_dict['login_count'] = login_count
        
        return jsonify({'message': 'Connexion réussie', 'user': user_dict})
        
    except Exception as e:
        import traceback
        print('Erreur /api/login:', traceback.format_exc())
        return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500
    finally:
        conn.close()

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Déconnexion réussie'})

@app.route('/api/users', methods=['GET'])
def get_users():
    if 'user_id' not in session:
        return jsonify({'error': 'Non autorisé'}), 401
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    try:
        c.execute('SELECT id, name, email, created_at, last_login, is_active, login_count FROM users')
        users = []
        
        for user in c.fetchall():
            users.append({
                'id': user[0],
                'name': user[1],
                'email': user[2],
                'created_at': user[3],
                'last_login': user[4],
                'is_active': bool(user[5]),
                'login_count': user[6]
            })
        
        return jsonify(users)
    except Exception as e:
        return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500
    finally:
        conn.close()

@app.route('/api/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Non autorisé'}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Données JSON manquantes'}), 400
        
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    try:
        # Vérifier que l'utilisateur existe
        c.execute('SELECT id FROM users WHERE id = ?', (user_id,))
        if not c.fetchone():
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        # Mettre à jour les champs
        updates = []
        params = []
        
        if 'name' in data:
            updates.append('name = ?')
            params.append(data['name'])
        
        if 'email' in data:
            # Vérifier que l'email n'est pas déjà utilisé par un autre utilisateur
            c.execute('SELECT id FROM users WHERE email = ? AND id != ?', (data['email'], user_id))
            if c.fetchone():
                return jsonify({'error': 'Cet email est déjà utilisé'}), 400
            
            updates.append('email = ?')
            params.append(data['email'])
        
        if 'password' in data and data['password']:
            updates.append('password = ?')
            params.append(hash_password(data['password']))
        
        if 'is_active' in data:
            updates.append('is_active = ?')
            params.append(1 if data['is_active'] else 0)
        
        if updates:
            query = f'UPDATE users SET {", ".join(updates)} WHERE id = ?'
            params.append(user_id)
            c.execute(query, params)
        
        conn.commit()
        return jsonify({'message': 'Utilisateur mis à jour avec succès'})
        
    except Exception as e:
        conn.rollback()
        return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500
    finally:
        conn.close()

@app.route('/api/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Non autorisé'}), 401
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    try:
        c.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        return jsonify({'message': 'Utilisateur supprimé avec succès'})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500
    finally:
        conn.close()

@app.route('/api/me', methods=['GET'])
def get_current_user():
    if 'user_id' not in session:
        return jsonify({'error': 'Non autorisé'}), 401
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    try:
        c.execute('SELECT id, name, email, created_at, last_login, is_active, login_count FROM users WHERE id = ?', 
                  (session['user_id'],))
        user = c.fetchone()
        
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        
        user_dict = {
            'id': user[0],
            'name': user[1],
            'email': user[2],
            'created_at': user[3],
            'last_login': user[4],
            'is_active': bool(user[5]),
            'login_count': user[6]
        }
        
        return jsonify(user_dict)
    except Exception as e:
        return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500
    finally:
        conn.close()

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'OK', 'message': 'Serveur en fonctionnement'})

@app.route('/api/session_status', methods=['GET'])
def session_status():
    # Vérifie si la session utilisateur est active
    if 'user_id' in session:
        return jsonify({'active': True, 'user_id': session['user_id']}), 200
    else:
        return jsonify({'active': False}), 401

@app.route('/users_list')
def users_list():
    return render_template('usersList.html')

# Exemple d'événement Socket.IO
def socketio_events():
    @socketio.on('connect')
    def handle_connect():
        print('Client connecté')
        emit('message', {'data': 'Connexion établie avec le serveur Flask-SocketIO'})

socketio_events()

if __name__ == '__main__':
    print("Initialisation de la base de données...")
    init_db()
    print("Base de données initialisée")
    print("Lancement du serveur sur https://localhost:5004")
    print("Utilisateur de test: admin@example.com / admin123")
    socketio.run(app, host="0.0.0.0", port=5004, ssl_context=("cert.pem", "key.pem"))
