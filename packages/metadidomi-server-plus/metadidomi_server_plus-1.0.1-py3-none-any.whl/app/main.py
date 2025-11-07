import logging
from fastapi import FastAPI, Request, Depends, Body, HTTPException, Path, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from .db import Base, engine, SessionLocal, get_db
from .services.dynamic_routes import reload_routes
from .routers import admin
from sqlalchemy.orm import Session
from app.models import MetadidomiCloudDatabaseData, CloudDatabaseRule
import os
import json, socket
import jwt
from fastapi.templating import Jinja2Templates
import sqlite3
from passlib.hash import bcrypt
from typing import Any, Optional
import shutil
import base64

# Ajout configuration logging selon le mode
mode = os.environ.get('METADIDOMI_SERVER_MODE', 'developpement')
# Charger le domaine personnalisé si mode production
if mode == 'production':
    settings_path = os.path.join(os.path.dirname(__file__), '..', 'cloud_settings.json')
    domain = None
    try:
        with open(settings_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            domain = data.get('domain_name')
    except Exception:
        pass
    if domain:
        allowed_origins = [f"https://{domain}"]
    else:
        allowed_origins = ["https://votre-domaine.com"]
else:
    allowed_origins = ["*"]

# Mode production forcé
logging.basicConfig(level=logging.INFO)
logging.getLogger('uvicorn').setLevel(logging.INFO)
logging.getLogger('fastapi').setLevel(logging.INFO)

# Logger persistant Metadidomi
log_path = os.path.join(os.path.dirname(__file__), '..', 'logs.txt')
log_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
file_handler = logging.FileHandler(log_path, encoding='utf-8')
file_handler.setFormatter(log_formatter)
logger = logging.getLogger('metadidomi')
logger.setLevel(logging.DEBUG if os.environ.get('METADIDOMI_SERVER_MODE','developpement')=='developpement' else logging.INFO)
if not logger.hasHandlers():
    logger.addHandler(file_handler)

else:
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('uvicorn').setLevel(logging.INFO)
    logging.getLogger('fastapi').setLevel(logging.INFO)
    # Avertissement si pas HTTPS
    import sys
    if not any(origin.startswith('https://') for origin in allowed_origins):
        logger.warning("[SECURITE] Le serveur est en mode production sans HTTPS dans CORS. Il est fortement recommandé d'utiliser un reverse proxy HTTPS.")

# Gestion du nom d’hôte personnalisé
SETTINGS_PATH = os.path.join(os.path.dirname(__file__), '..', 'cloud_settings.json')
def get_hostname():
    # Priorité : variable d’environnement > fichier settings > hostname machine
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

Base.metadata.create_all(bind=engine)

from .models import Base
Base.metadata.create_all(bind=engine)

app = FastAPI(title=f"Metadidomi Server+ [{HOSTNAME}]", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin.router)
from .routers import users
app.include_router(users.router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/templates", StaticFiles(directory="app/templates", html=True), name="templates")

SECRET_KEY = "change_this_secret"  # Doit être identique à celui utilisé pour la génération du token

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_username(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail=None)  # Suppression du message 'Non authentifié'
    token = authorization.split(" ", 1)[1]
    return verify_token(token)

@app.get("/hostname")
def api_hostname():
    return {"hostname": HOSTNAME}

@app.post("/set_hostname")
def api_set_hostname(new_hostname: str):
    global HOSTNAME
    os.environ["METADIDOMI_HOSTNAME"] = new_hostname
    # Persistance dans cloud_settings.json
    try:
        with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
            json.dump({'hostname': new_hostname}, f)
    except Exception:
        pass
    HOSTNAME = new_hostname
    return {"hostname": HOSTNAME}

@app.post("/sync_metadidomi_cloud_database")
def sync_metadidomi_cloud_database(data: dict = Body(...), db: Session = Depends(get_db)):
    obj = db.query(MetadidomiCloudDatabaseData).filter(MetadidomiCloudDatabaseData.id == 1).first()
    if obj:
        obj.data = json.dumps(data)
    else:
        obj = MetadidomiCloudDatabaseData(id=1, data=json.dumps(data))
        db.add(obj)
    db.commit()
    return {"status": "ok"}

@app.post("/sync_metadidomi_cloud_rules")
def sync_metadidomi_cloud_rules(rules: list = Body(...), db: Session = Depends(get_db)):
    db.query(CloudDatabaseRule).delete()
    for rule in rules:
        db.add(CloudDatabaseRule(
            collection=rule.get("collection"),
            create=rule.get("create", "Utilisateur connecté"),
            read=rule.get("read", "Utilisateur connecté"),
            write=rule.get("write", "Utilisateur connecté"),
            delete=rule.get("delete", "Utilisateur connecté")
        ))
    db.commit()
    return {"status": "ok"}

@app.get("/get_metadidomi_cloud_database")
def get_metadidomi_cloud_database(db: Session = Depends(get_db)):
    obj = db.query(MetadidomiCloudDatabaseData).filter(MetadidomiCloudDatabaseData.id == 1).first()
    if (obj and obj.data):
        try:
            return json.loads(obj.data)
        except Exception:
            return {"error": "Données corrompues"}
    return {}

@app.get("/", response_class=HTMLResponse)
def main_ui():
    html_path = os.path.join(os.path.dirname(__file__), "templates", "main_ui.html")
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()
        # Remplacement dynamique du hostname
        content = content.replace("{{HOSTNAME}}", HOSTNAME)
    except Exception as exc:
        content = f"<h2>Erreur lors du chargement de la page d'accueil : {exc}</h2>"
    return content

@app.get("/logs", response_class=HTMLResponse)
def show_logs():
    log_path = os.path.join(os.path.dirname(__file__), "..", "logs.txt")
    try:
        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception as exc:
        content = f"Erreur lors de la lecture des logs : {exc}"
    return f"""<html><head><title>Logs Serveur</title><style>body{{font-family:monospace;background:#f7f7fa}}pre{{background:#fff;border-radius:8px;padding:16px;max-width:900px;margin:32px auto;box-shadow:0 2px 8px #0001;white-space:pre-wrap;word-break:break-all}}</style></head><body><h1>Logs du serveur <span style='color:#007bff;font-size:0.7em'>[{HOSTNAME}]</span></h1><pre>{content}</pre><a href='/'>Retour à l'accueil</a></body></html>"""

@app.get("/logs_last20", response_class=HTMLResponse)
def show_last_logs():
    log_path = os.path.join(os.path.dirname(__file__), "..", "logs.txt")
    try:
        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
            last_lines = lines[-20:] if len(lines) >= 20 else lines
            content = "".join(last_lines)
    except Exception as exc:
        content = f"Erreur lors de la lecture des logs : {exc}"
    return f"<html><head><title>Logs Serveur (20 derniers)</title><style>body{{font-family:monospace;background:#f7f7fa}}pre{{background:#fff;border-radius:8px;padding:16px;max-width:900px;margin:32px auto;box-shadow:0 2px 8px #0001;white-space:pre-wrap;word-break:break-all}}</style></head><body><h1>Logs du serveur <span style='color:#007bff;font-size:0.7em'>[{HOSTNAME}]</span></h1><pre>{content}</pre><a href='/'>Retour à l'accueil</a></body></html>"

from fastapi import Request
from fastapi.responses import RedirectResponse

# Fonction utilitaire pour vérifier le token dans le cookie

def get_token_from_cookie(request: Request):
    return None

@app.get("/cloud_database", response_class=HTMLResponse)
def cloud_database_page(request: Request):
    html_path = os.path.join(os.path.dirname(__file__), "templates", "cloud_database.html")
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()
        content = content.replace("{{HOSTNAME}}", HOSTNAME)
    except Exception as exc:
        content = f"<h2>Erreur lors du chargement de la page Cloud Database : {exc}</h2>"
    return content

@app.get("/cloud_drive", response_class=HTMLResponse)
def cloud_drive_page(request: Request):
    html_path = os.path.join(os.path.dirname(__file__), "templates", "cloud_drive.html")
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as exc:
        content = f"<h2>Erreur lors du chargement de la page Cloud Drive : {exc}</h2>"
    return content

@app.get("/admin", response_class=HTMLResponse)
def admin_page(request: Request):
    html_path = os.path.join(os.path.dirname(__file__), "templates", "admin.html")
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as exc:
        content = f"<h2>Erreur lors du chargement de la page Admin : {exc}</h2>"
    return content

@app.get('/login', response_class=HTMLResponse)
def login_page():
    html_path = os.path.join(os.path.dirname(__file__), "templates", "login.html")
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as exc:
        content = f"<h2>Erreur lors du chargement de la page de connexion : {exc}</h2>"
    return content

@app.post('/login', response_class=HTMLResponse)
async def login_post(request: Request):
    import sqlite3, bcrypt, uuid, datetime
    form = await request.form()
    username = form.get('username')
    password = form.get('password')
    db_path = os.path.join(os.path.dirname(__file__), '..', 'users.db')
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT id, name, password FROM users WHERE name=?', (username,))
    user = c.fetchone()
    conn.close()
    if user:
        from fastapi.responses import RedirectResponse
        from starlette.responses import Response
        import jwt
        token = jwt.encode({"sub": username, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)}, SECRET_KEY, algorithm="HS256")
        response = RedirectResponse('/cloud_drive', status_code=302)
        response.set_cookie(key="access_token", value=token, httponly=True, max_age=7200)
        return response
    else:
        html_path = os.path.join(os.path.dirname(__file__), "templates", "login.html")
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()
        error_msg = "<div style='color:red;text-align:center;'>Identifiants invalides</div>"
        content = content.replace("</form>", f"{error_msg}</form>")
        return HTMLResponse(content)

from fastapi.responses import RedirectResponse

templates = Jinja2Templates(directory="app/templates")

@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    reload_routes(app, db)
    db.close()

def get_metadidomi_cloud_database_data(db: Session) -> dict:
    obj = db.query(MetadidomiCloudDatabaseData).filter(MetadidomiCloudDatabaseData.id == 1).first()
    if obj and obj.data:
        try:
            return json.loads(obj.data)
        except Exception:
            raise HTTPException(status_code=500, detail="Données Metadidomi Cloud Database corrompues")
    return {}

def save_metadidomi_cloud_database_data(data: dict, db: Session):
    obj = db.query(MetadidomiCloudDatabaseData).filter(MetadidomiCloudDatabaseData.id == 1).first()
    if obj:
        obj.data = json.dumps(data)
    else:
        obj = MetadidomiCloudDatabaseData(id=1, data=json.dumps(data))
        db.add(obj)
    db.commit()

def get_by_path(data: dict, path: str):
    if not path:
        return data
    keys = path.split('/')
    ref = data
    for k in keys:
        if isinstance(ref, dict) and k in ref:
            ref = ref[k]
        else:
            raise HTTPException(status_code=404, detail=f"Chemin Firestore introuvable: {path}")
    return ref

def set_by_path(data: dict, path: str, value: Any, merge=False):
    keys = path.split('/')
    ref = data
    for k in keys[:-1]:
        if k not in ref or not isinstance(ref[k], dict):
            ref[k] = {}
        ref = ref[k]
    if merge and isinstance(ref.get(keys[-1]), dict) and isinstance(value, dict):
        ref[keys[-1]].update(value)
    else:
        ref[keys[-1]] = value

def delete_by_path(data: dict, path: str):
    keys = path.split('/')
    ref = data
    for k in keys[:-1]:
        if k not in ref or not isinstance(ref[k], dict):
            raise HTTPException(status_code=404, detail=f"Chemin Firestore introuvable: {path}")
        ref = ref[k]
    if keys[-1] in ref:
        del ref[keys[-1]]
    else:
        raise HTTPException(status_code=404, detail=f"Chemin Firestore introuvable: {path}")

def normalize_field_value(field_type, field_value):
    supported_types = ["string","number","boolean","timestamp","map","array","null","reference","geopoint"]
    if field_type not in supported_types:
        raise HTTPException(status_code=400, detail=f"Type non supporté : {field_type}")
    if field_type == "number":
        try:
            field_value = float(field_value)
        except Exception:
            field_value = 0
    elif field_type == "boolean":
        field_value = bool(field_value)
    elif field_type == "null":
        field_value = None
    elif field_type == "map":
        if not isinstance(field_value, dict):
            field_value = {}
    elif field_type == "array":
        if not isinstance(field_value, list):
            field_value = []
    elif field_type == "geopoint":
        if not (isinstance(field_value, dict) and "latitude" in field_value and "longitude" in field_value):
            field_value = {"latitude":0, "longitude":0}
    # Pour string, timestamp, reference : pas de transformation
    return field_value

@app.delete("/metadidomi_cloud_database/{collection}/{doc_id}", tags=["Metadidomi Cloud Database CRUD"], summary="Supprimer un document dans une collection", response_model=dict)
def api_delete_document(collection: str, doc_id: str, db: Session = Depends(get_db)):
    """
    Supprime le document {doc_id} dans la collection {collection}.
    """
    data = get_metadidomi_cloud_database_data(db)
    if collection not in data or doc_id not in data[collection]:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    del data[collection][doc_id]
    save_metadidomi_cloud_database_data(data, db)
    return {"status": "ok"}

@app.delete("/metadidomi_cloud_database/{collection}/{doc_id}/fields/{field_name}", tags=["Metadidomi Cloud Database CRUD"], summary="Supprimer un champ dans un document", response_model=dict)
def api_delete_field(collection: str, doc_id: str, field_name: str, db: Session = Depends(get_db)):
    """
    Supprime le champ {field_name} dans le document {doc_id} de la collection {collection}.
    """
    data = get_metadidomi_cloud_database_data(db)
    if collection not in data or doc_id not in data[collection]:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    fields = data[collection][doc_id].get('fields', {})
    if field_name not in fields:
        raise HTTPException(status_code=404, detail="Champ non trouvé")
    del fields[field_name]
    save_metadidomi_cloud_database_data(data, db)
    return {"status": "ok"}

@app.post("/metadidomi_cloud_database/{collection}/{doc_id}/fields", tags=["Metadidomi Cloud Database CRUD"], summary="Ajouter un champ dans un document", response_model=dict)
def api_add_field(
    collection: str = Path(..., description="Nom de la collection", example="utilisateurs"),
    doc_id: str = Path(..., description="ID du document", example="user_123"),
    field_name: str = Body(..., description="Nom du champ à ajouter (ex: 'nom')", example="nom"),
    field_type: str = Body(..., description="Type du champ à ajouter (ex: 'string', 'number', 'boolean', etc.)", example="string"),
    field_value: Any = Body(..., description="Valeur du champ à ajouter, selon le type choisi", example="Jean"),
    db: Session = Depends(get_db)):
    """
    Ajoute un champ dans le document {doc_id} de la collection {collection}.
    
    ⚠️ Saisie champ par champ :
    - field_name : nom du champ à créer (ex: 'nom')
    - field_type : type du champ ('string', 'number', 'boolean', 'timestamp', 'map', 'array', 'null', 'reference', 'geopoint')
    - field_value : valeur du champ, selon le type
    
    Exemple de Request Body (client HTTP ou HTTPS) :
    {
      "field_name": "nom",
      "field_type": "string",
      "field_value": "Jean"
    }
        """
    data = get_metadidomi_cloud_database_data(db)
    if collection not in data or doc_id not in data[collection]:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    if 'fields' not in data[collection][doc_id]:
        data[collection][doc_id]['fields'] = {}
    if field_name in data[collection][doc_id]['fields']:
        raise HTTPException(status_code=400, detail="Champ déjà existant")
    # Normalisation du type
    field_value = normalize_field_value(field_type, field_value)
    data[collection][doc_id]['fields'][field_name] = {"type": field_type, "value": field_value}
    save_metadidomi_cloud_database_data(data, db)
    return {"status": "ok"}

@app.post("/metadidomi_cloud_database/{collection}", tags=["Metadidomi Cloud Database CRUD"], summary="Ajouter un document dans une collection", response_model=dict)
def api_add_document(
    collection: str = Path(..., description="Nom de la collection", example="utilisateurs"),
    doc_id: str = Body(..., description="ID du document à créer", example="user_123"),
    db: Session = Depends(get_db)):
    """
    Ajoute un document vide (fields={}, subCollections={}) dans la collection {collection} avec l'id {doc_id}.
    """
    data = get_metadidomi_cloud_database_data(db)
    if collection not in data:
        data[collection] = {}
    if doc_id in data[collection]:
        raise HTTPException(status_code=400, detail="Document déjà existant")
    data[collection][doc_id] = {"fields": {}, "subCollections": {}}
    save_metadidomi_cloud_database_data(data, db)
    return {"status": "ok"}

@app.post("/metadidomi_cloud_database/{collection}/{doc_id}/subcollections", tags=["Metadidomi Cloud Database CRUD"], summary="Ajouter une sous-collection à un document", response_model=dict)
def api_add_subcollection(
    collection: str = Path(..., description="Nom de la collection", example="utilisateurs"),
    doc_id: str = Path(..., description="ID du document", example="user_123"),
    subcollection_name: str = Body(..., description="Nom de la sous-collection à ajouter", example="commandes"),
    db: Session = Depends(get_db)):
    """
    Ajoute une sous-collection vide au document {doc_id} dans la collection {collection}.
    """
    data = get_metadidomi_cloud_database_data(db)
    if collection not in data or doc_id not in data[collection]:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    if 'subCollections' not in data[collection][doc_id]:
        data[collection][doc_id]['subCollections'] = {}
    if subcollection_name in data[collection][doc_id]['subCollections']:
        raise HTTPException(status_code=400, detail="Sous-collection déjà existante")
    data[collection][doc_id]['subCollections'][subcollection_name] = {}
    save_metadidomi_cloud_database_data(data, db)
    return {"status": "ok"}

@app.delete("/metadidomi_cloud_database/{collection}/{doc_id}/subcollections/{subcollection_name}", tags=["Metadidomi Cloud Database CRUD"], summary="Supprimer une sous-collection d'un document", response_model=dict)
def api_delete_subcollection(collection: str, doc_id: str, subcollection_name: str, db: Session = Depends(get_db)):
    """
    Supprime la sous-collection {subcollection_name} du document {doc_id} dans la collection {collection}.
    """
    data = get_metadidomi_cloud_database_data(db)
    if collection not in data or doc_id not in data[collection]:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    subcollections = data[collection][doc_id].get('subCollections', {})
    if subcollection_name not in subcollections:
        raise HTTPException(status_code=404, detail="Sous-collection non trouvée")
    del subcollections[subcollection_name]
    save_metadidomi_cloud_database_data(data, db)
    return {"status": "ok"}

@app.post("/metadidomi_cloud_database/{collection}/{doc_id}/subcollections/{subcollection_name}", tags=["Metadidomi Cloud Database CRUD"], summary="Ajouter un document dans une sous-collection", response_model=dict)
def api_add_document_in_subcollection(
    collection: str = Path(..., description="Nom de la collection", example="utilisateurs"),
    doc_id: str = Path(..., description="ID du document", example="user_123"),
    subcollection_name: str = Path(..., description="Nom de la sous-collection", example="commandes"),
    subdoc_id: str = Body(..., description="ID du document à créer dans la sous-collection", example="cmd_001"),
    db: Session = Depends(get_db)):
    """
    Ajoute un document vide dans la sous-collection {subcollection_name} du document {doc_id}.
    """
    data = get_metadidomi_cloud_database_data(db)
    if collection not in data or doc_id not in data[collection]:
        raise HTTPException(status_code=404, detail="Document principal non trouvé")
    subcollections = data[collection][doc_id].setdefault('subCollections', {})
    if subcollection_name not in subcollections:
        subcollections[subcollection_name] = {}
    if subdoc_id in subcollections[subcollection_name]:
        raise HTTPException(status_code=400, detail="Document déjà existant dans la sous-collection")
    subcollections[subcollection_name][subdoc_id] = {"fields": {}, "subCollections": {}}
    save_metadidomi_cloud_database_data(data, db)
    return {"status": "ok"}

@app.post("/metadidomi_cloud_database/{collection}/{doc_id}/subcollections/{subcollection_name}/{subdoc_id}/fields", tags=["Metadidomi Cloud Database CRUD"], summary="Ajouter un champ dans un document de sous-collection", response_model=dict)
def api_add_field_in_subcollection(
    collection: str = Path(..., description="Nom de la collection", example="utilisateurs"),
    doc_id: str = Path(..., description="ID du document", example="user_123"),
    subcollection_name: str = Path(..., description="Nom de la sous-collection", example="commandes"),
    subdoc_id: str = Path(..., description="ID du document de sous-collection", example="cmd_001"),
    field_name: str = Body(..., description="Nom du champ à ajouter (ex: 'nom')", example="montant"),
    field_type: str = Body(..., description="Type du champ à ajouter (ex: 'string', 'number', 'boolean', etc.)", example="number"),
    field_value: Any = Body(..., description="Valeur du champ à ajouter, selon le type choisi", example=99.99),
    db: Session = Depends(get_db)):
    """
    Ajoute un champ dans le document {subdoc_id} de la sous-collection {subcollection_name} du document {doc_id} de la collection {collection}.
    
    ⚠️ Saisie champ par champ :
    - field_name : nom du champ à créer (ex: 'nom')
    - field_type : type du champ ('string', 'number', 'boolean', 'timestamp', 'map', 'array', 'null', 'reference', 'geopoint')
    - field_value : valeur du champ, selon le type
    
    Exemple de Request Body (client HTTP) :
    {
      "field_name": "nom",
      "field_type": "string",
      "field_value": "Jean"
    }
        """
    data = get_metadidomi_cloud_database_data(db)
    # Vérification de l'existence
    if collection not in data or doc_id not in data[collection]:
        raise HTTPException(status_code=404, detail="Document principal non trouvé")
    subcollections = data[collection][doc_id].setdefault('subCollections', {})
    if subcollection_name not in subcollections:
        raise HTTPException(status_code=404, detail="Sous-collection non trouvée")
    if subdoc_id not in subcollections[subcollection_name]:
        raise HTTPException(status_code=404, detail="Document de sous-collection non trouvé")
    subdoc = subcollections[subcollection_name][subdoc_id]
    if 'fields' not in subdoc:
        subdoc['fields'] = {}
    if field_name in subdoc['fields']:
        raise HTTPException(status_code=400, detail="Champ déjà existant")
    # Normalisation du type
    field_value = normalize_field_value(field_type, field_value)
    subdoc['fields'][field_name] = {"type": field_type, "value": field_value}
    save_metadidomi_cloud_database_data(data, db)
    return {"status": "ok"}

@app.put("/metadidomi_cloud_database/{collection}/{doc_id}/fields/{field_name}", tags=["Metadidomi Cloud Database CRUD"], summary="Mettre à jour la valeur d'un champ dans un document", response_model=dict)
def api_update_field(
    collection: str = Path(..., description="Nom de la collection", example="utilisateurs"),
    doc_id: str = Path(..., description="ID du document", example="user_123"),
    field_name: str = Path(..., description="Nom du champ à mettre à jour", example="nom"),
    field_type: str = Body(..., description="Type du champ ('string', 'number', 'boolean', etc.)", example="string"),
    field_value: Any = Body(..., description="Nouvelle valeur du champ, selon le type choisi", example="Jean Dupont"),
    db: Session = Depends(get_db)):
    """
    Met à jour la valeur d'un champ dans le document {doc_id} de la collection {collection}.
    Exemple de Request Body :
    {
      "field_type": "string",
      "field_value": "Jean Dupont"
    }
    """
    data = get_metadidomi_cloud_database_data(db)
    if collection not in data or doc_id not in data[collection]:
        raise HTTPException(status_code=404, detail="Document non trouvé")
    fields = data[collection][doc_id].get('fields', {})
    if field_name not in fields:
        raise HTTPException(status_code=404, detail="Champ non trouvé")
    # Normalisation du type
    field_value = normalize_field_value(field_type, field_value)
    fields[field_name] = {"type": field_type, "value": field_value}
    save_metadidomi_cloud_database_data(data, db)
    return {"status": "ok"}

@app.put("/metadidomi_cloud_database/{collection}/{doc_id}/subcollections/{subcollection_name}/{subdoc_id}/fields/{field_name}", tags=["Metadidomi Cloud Database CRUD"], summary="Mettre à jour la valeur d'un champ dans un document de sous-collection", response_model=dict)
def api_update_field_in_subcollection(
    collection: str = Path(..., description="Nom de la collection", example="utilisateurs"),
    doc_id: str = Path(..., description="ID du document", example="user_123"),
    subcollection_name: str = Path(..., description="Nom de la sous-collection", example="commandes"),
    subdoc_id: str = Path(..., description="ID du document de sous-collection", example="cmd_001"),
    field_name: str = Path(..., description="Nom du champ à mettre à jour", example="montant"),
    field_type: str = Body(..., description="Type du champ ('string', 'number', 'boolean', etc.)", example="number"),
    field_value: Any = Body(..., description="Nouvelle valeur du champ, selon le type choisi", example=149.99),
    db: Session = Depends(get_db)):
    """
    Met à jour la valeur d'un champ dans le document {subdoc_id} de la sous-collection {subcollection_name} du document {doc_id} de la collection {collection}.
    Exemple de Request Body :
    {
      "field_type": "number",
      "field_value": 149.99
    }
    """
    data = get_metadidomi_cloud_database_data(db)
    if collection not in data or doc_id not in data[collection]:
        raise HTTPException(status_code=404, detail="Document principal non trouvé")
    subcollections = data[collection][doc_id].setdefault('subCollections', {})
    if subcollection_name not in subcollections:
        raise HTTPException(status_code=404, detail="Sous-collection non trouvée")
    if subdoc_id not in subcollections[subcollection_name]:
        raise HTTPException(status_code=404, detail="Document de sous-collection non trouvé")
    subdoc = subcollections[subcollection_name][subdoc_id]
    if 'fields' not in subdoc:
        subdoc['fields'] = {}
    if field_name not in subdoc['fields']:
        raise HTTPException(status_code=404, detail="Champ non trouvé")
    # Normalisation du type
    field_value = normalize_field_value(field_type, field_value)
    subdoc['fields'][field_name] = {"type": field_type, "value": field_value}
    save_metadidomi_cloud_database_data(data, db)
    return {"status": "ok"}

@app.get("/rules")
def get_rules(db: Session = Depends(get_db)):
    rules = db.query(CloudDatabaseRule).all()
    result = []
    for rule in rules:
        result.append({
            "collection": rule.collection,
            "create": rule.create,
            "read": rule.read,
            "write": rule.write,
            "delete": rule.delete
        })
    return result

@app.delete("/metadidomi_cloud_database/{collection}", tags=["Metadidomi Cloud Database CRUD"], summary="Supprimer une collection et ses règles associées", response_model=dict)
def api_delete_collection(collection: str, db: Session = Depends(get_db)):
    """
    Supprime la collection {collection} dans la base de données ET toutes les règles associées à cette collection.
    """
    data = get_metadidomi_cloud_database_data(db)
    if collection not in data:
        raise HTTPException(status_code=404, detail="Collection non trouvée")
    del data[collection]
    save_metadidomi_cloud_database_data(data, db)
    # Suppression des règles associées à cette collection
    db.query(CloudDatabaseRule).filter(CloudDatabaseRule.collection == collection).delete()
    db.commit()
    return {"status": "ok"}

def get_db_connection():
    db_path = os.path.join(os.path.dirname(__file__), '..', 'cloud_storage.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    # Création automatique de la table si elle n'existe pas
    conn.execute('''CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        folder_id TEXT,
        user_id TEXT,
        content TEXT,
        type TEXT
    )''')
    conn.commit()
    return conn

# Ajout d'une fonction utilitaire pour loguer les opérations SQLite

def log_sqlite_file_save(file_row):
    # file_row est un dict représentant la ligne insérée ou modifiée
    logger.info(f"[cloud_sync] Sauvegarde fichier dans SQLite: table=files, id={file_row.get('id')}, colonnes={list(file_row.keys())} (destination SQLite)")
    print(f"[cloud_sync] Sauvegarde fichier dans SQLite: table=files, id={file_row.get('id')}, colonnes={list(file_row.keys())} (destination SQLite)")

def get_current_user(authorization: str = Header(None)):
    username = get_current_username(authorization)
    # You can extend this to fetch user info from DB if needed
    return {"username": username}

def get_files(folder_id: Optional[int] = Query(None), user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    if folder_id is None:
        cursor.execute('''
            SELECT * FROM files 
            WHERE user_id = ? AND folder_id IS NULL
            ORDER BY name
        ''', (user['id'],))
    else:
        cursor.execute('''
            SELECT * FROM files 
            WHERE user_id = ? AND folder_id = ?
            ORDER BY name
        ''', (user['id'], folder_id))
    files = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"files": files}

@app.post("/api/cloud_sync")
async def api_cloud_sync(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    action = data.get('action')
    response = { 'success': False }
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'metadidomi_cloud_storage_files', 'Root'))
    os.makedirs(root_dir, exist_ok=True)

    # LOGS DEBUG
    print(f"[cloud_sync] action: {action}")
    print(f"[cloud_sync] payload: {json.dumps(data, ensure_ascii=False, indent=2)}")
    logger.info(f"[cloud_sync] action: {action}")
    logger.info(f"[cloud_sync] payload: {json.dumps(data, ensure_ascii=False, indent=2)}")

    if action == 'push_all':
        files = data.get('files', [])
        folders = data.get('folders', [])
        print(f"[cloud_sync] Folders reçus: {folders}")
        print(f"[cloud_sync] Files reçus: {files}")
        logger.info(f"[cloud_sync] Folders reçus: {folders}")
        logger.info(f"[cloud_sync] Files reçus: {files}")
        # Synchroniser les dossiers
        for folder in folders:
            folder_path = os.path.join(root_dir, folder['name']) if not folder.get('parentId') else os.path.join(root_dir, folder['parentId'], folder['name'])
            print(f"[cloud_sync] Création dossier: {folder_path} (destination)")
            logger.info(f"[cloud_sync] Création dossier: {folder_path} (destination)")
            os.makedirs(folder_path, exist_ok=True)
        # Synchroniser les fichiers
        for file in files:
            folder_path = os.path.join(root_dir, file['folderId']) if file.get('folderId') else root_dir
            file_path = os.path.join(folder_path, file['name'])
            print(f"[cloud_sync] Sauvegarde fichier: {file_path} (destination)")
            logger.info(f"[cloud_sync] Sauvegarde fichier: {file_path} (destination)")
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(file['content'])
                # Ajout dans SQLite
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('''INSERT INTO files (name, folder_id, user_id, content, type) VALUES (?, ?, ?, ?, ?)''',
                               (file['name'], file.get('folderId'), file.get('userId', None), file['content'], file.get('type', 'text/plain')))
                conn.commit()
                file_id = cursor.lastrowid
                cursor.execute('SELECT * FROM files WHERE id = ?', (file_id,))
                file_row = dict(cursor.fetchone())
                log_sqlite_file_save(file_row)
                conn.close()
            except Exception as e:
                print(f"[cloud_sync] ERREUR fichier: {e}")
                logger.error(f"[cloud_sync] ERREUR fichier: {e}")
        response['success'] = True
    elif action == 'create_folder':
        folder = data.get('folder')
        folder_path = os.path.join(root_dir, folder['name']) if not folder.get('parentId') else os.path.join(root_dir, folder['parentId'], folder['name'])
        try:
            os.makedirs(folder_path, exist_ok=False)
            response['success'] = True
        except FileExistsError:
            response['error'] = 'Dossier existe déjà'
    elif action == 'rename_folder':
        folderId = data.get('folderId')
        oldName = data.get('oldName')
        newName = data.get('newName')
        parent_path = os.path.join(root_dir, folderId) if folderId else root_dir
        old_path = os.path.join(parent_path, oldName)
        new_path = os.path.join(parent_path, newName)
        try:
            os.rename(old_path, new_path)
            response['success'] = True
        except Exception as e:
            response['error'] = str(e)
    elif action == 'delete_folder':
        folderId = data.get('folderId')
        folder_path = os.path.join(root_dir, folderId) if folderId else root_dir
        try:
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)
            response['success'] = True
        except Exception as e:
            response['error'] = str(e)
    elif action == 'upload_file':
        file = data.get('file')
        folder_path = os.path.join(root_dir, file['folderId']) if file.get('folderId') else root_dir
        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, file['name'])
        logger.info(f"[cloud_sync] Sauvegarde fichier: {file_path} (destination)")
        print(f"[cloud_sync] Sauvegarde fichier: {file_path} (destination)")
        file_content = file['content']
        # Gestion du contenu binaire ou texte
        if file['type'].startswith('image/') or file['type'].startswith('application/'):
            try:
                file_content = base64.b64decode(file_content)
                with open(file_path, 'wb') as f:
                    f.write(file_content)
            except Exception as e:
                print(f"[cloud_sync] ERREUR fichier: {e}")
                logger.error(f"[cloud_sync] ERREUR fichier: {e}")
        else:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file_content)
        # Ajout ou mise à jour dans SQLite
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            # On supprime l'ancien si même nom/dossier/user
            cursor.execute('''DELETE FROM files WHERE name=? AND folder_id=? AND user_id=?''', (file['name'], file.get('folderId'), file.get('userId', None)))
            cursor.execute('''INSERT INTO files (name, folder_id, user_id, content, type) VALUES (?, ?, ?, ?, ?)''',
                           (file['name'], file.get('folderId'), file.get('userId', None), file['content'], file.get('type', 'application/octet-stream' if file['type'].startswith('image/') or file['type'].startswith('application/') else 'text/plain')))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[cloud_sync] ERREUR SQLite: {e}")
            logger.error(f"[cloud_sync] ERREUR SQLite: {e}")
        response['success'] = True
    elif action == 'rename_file':
        fileId = data.get('fileId')
        oldName = data.get('oldName')
        newName = data.get('newName')
        folder_path = os.path.join(root_dir, fileId) if fileId else root_dir
        old_path = os.path.join(folder_path, oldName)
        new_path = os.path.join(folder_path, newName)
        try:
            os.rename(old_path, new_path)
            response['success'] = True
        except Exception as e:
            response['error'] = str(e)
    elif action == 'delete_file':
        fileId = data.get('fileId')
        fileName = data.get('fileName')
        folder_path = os.path.join(root_dir, fileId) if fileId else root_dir
        file_path = os.path.join(folder_path, fileName)
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            response['success'] = True
        except Exception as e:
            response['error'] = str(e)
    else:
        response['error'] = 'Action inconnue'
    return response

from fastapi import status

@app.post("/api/cloud_drive/create_folder", tags=["Cloud Drive CRUD"], summary="Créer un dossier Cloud Drive", response_model=dict)
def create_folder(folder: dict = Body(...)):
    """
    Crée un dossier Cloud Drive.
    Payload : {"name": str, "parentId": str (optionnel)}
    """
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'metadidomi_cloud_storage_files', 'Root'))
    folder_path = os.path.join(root_dir, folder['name']) if not folder.get('parentId') else os.path.join(root_dir, folder['parentId'], folder['name'])
    try:
        os.makedirs(folder_path, exist_ok=False)
        return {"success": True}
    except FileExistsError:
        return {"error": "Dossier existe déjà"}

@app.put("/api/cloud_drive/rename_folder", tags=["Cloud Drive CRUD"], summary="Renommer un dossier Cloud Drive", response_model=dict)
def rename_folder(data: dict = Body(...)):
    """
    Renomme un dossier Cloud Drive.
    Payload : {"folderId": str, "oldName": str, "newName": str}
    """
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'metadidomi_cloud_storage_files', 'Root'))
    parent_path = os.path.join(root_dir, data['folderId']) if data.get('folderId') else root_dir
    old_path = os.path.join(parent_path, data['oldName'])
    new_path = os.path.join(parent_path, data['newName'])
    try:
        os.rename(old_path, new_path)
        return {"success": True}
    except Exception as e:
        return {"error": str(e)}

@app.delete("/api/cloud_drive/delete_folder", tags=["Cloud Drive CRUD"], summary="Supprimer un dossier Cloud Drive", response_model=dict)
def delete_folder(folderId: str = Body(..., embed=True)):
    """
    Supprime un dossier Cloud Drive.
    Payload : {"folderId": str}
    """
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'metadidomi_cloud_storage_files', 'Root'))
    folder_path = os.path.join(root_dir, folderId) if folderId else root_dir
    try:
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
        return {"success": True}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/cloud_drive/upload_file", tags=["Cloud Drive CRUD"], summary="Uploader un fichier Cloud Drive", response_model=dict)
def upload_file(file: dict = Body(...)):
    """
    Upload un fichier Cloud Drive.
    Payload : {"name": str, "folderId": str (optionnel), "content": str, "type": str}
    """
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'metadidomi_cloud_storage_files', 'Root'))
    folder_path = os.path.join(root_dir, file['folderId']) if file.get('folderId') else root_dir
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, file['name'])
    file_content = file['content']
    if file['type'].startswith('image/') or file['type'].startswith('application/'):
        try:
            file_content = base64.b64decode(file_content)
            with open(file_path, 'wb') as f:
                f.write(file_content)
        except Exception as e:
            return {"error": str(e)}
    else:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(file_content)
    return {"success": True}

@app.put("/api/cloud_drive/rename_file", tags=["Cloud Drive CRUD"], summary="Renommer un fichier Cloud Drive", response_model=dict)
def rename_file(data: dict = Body(...)):
    """
    Renomme un fichier Cloud Drive.
    Payload : {"fileId": str, "oldName": str, "newName": str}
    """
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'metadidomi_cloud_storage_files', 'Root'))
    folder_path = os.path.join(root_dir, data['fileId']) if data.get('fileId') else root_dir
    old_path = os.path.join(folder_path, data['oldName'])
    new_path = os.path.join(folder_path, data['newName'])
    try:
        os.rename(old_path, new_path)
        return {"success": True}
    except Exception as e:
        return {"error": str(e)}

@app.delete("/api/cloud_drive/delete_file", tags=["Cloud Drive CRUD"], summary="Supprimer un fichier Cloud Drive", response_model=dict)
def delete_file(fileId: str = Body(..., embed=True), fileName: str = Body(..., embed=True)):
    """
    Supprime un fichier Cloud Drive.
    Payload : {"fileId": str, "fileName": str}
    """
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'metadidomi_cloud_storage_files', 'Root'))
    folder_path = os.path.join(root_dir, fileId) if fileId else root_dir
    file_path = os.path.join(folder_path, fileName)
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
        return {"success": True}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/cloud_drive/list_folders", tags=["Cloud Drive CRUD"], summary="Lister les dossiers Cloud Drive", response_model=dict)
def list_folders(parentId: str = Query(None, description="ID du dossier parent (optionnel)")):
    """
    Liste les dossiers Cloud Drive.
    API : /api/cloud_drive/list_folders
    Paramètre : parentId (optionnel)
    """
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'metadidomi_cloud_storage_files', 'Root'))
    base_path = os.path.join(root_dir, parentId) if parentId else root_dir
    try:
        folders = [name for name in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, name))]
        return {"folders": folders}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/cloud_drive/list_files", tags=["Cloud Drive CRUD"], summary="Lister les fichiers Cloud Drive", response_model=dict)
def list_files(folderId: str = Query(None, description="ID du dossier (optionnel)")):
    """
    Liste les fichiers Cloud Drive.
    API : /api/cloud_drive/list_files
    Paramètre : folderId (optionnel)
    """
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'metadidomi_cloud_storage_files', 'Root'))
    base_path = os.path.join(root_dir, folderId) if folderId else root_dir
    try:
        files = [name for name in os.listdir(base_path) if os.path.isfile(os.path.join(base_path, name))]
        return {"files": files}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/cloud_drive/login", tags=["Cloud Drive CRUD"], summary="Connexion utilisateur Cloud Drive", response_model=dict)
def cloud_drive_login(username: str = Body(...), password: str = Body(...)):
    """
    Authentifie un utilisateur Cloud Drive et retourne un token de session.
    API : /api/cloud_drive/login (port 5000)
    Payload : {"username": str, "password": str}
    """
    # Exemple simple, à adapter selon la gestion réelle des utilisateurs
    # Ici, on suppose que le mot de passe est stocké hashé dans la base
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE name=?', (username,))
    user = cursor.fetchone()
    conn.close()
    if user and bcrypt.verify(password, user['password']):
        import jwt, datetime
        token = jwt.encode({"sub": username, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)}, SECRET_KEY, algorithm="HS256")
        return {"success": True, "token": token}
    return {"success": False, "error": "Identifiants invalides"}

import socket

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'

def run_server(host="0.0.0.0", port=8000):
    """Fonction principale pour démarrer le serveur"""
    import uvicorn
    import socket
    
    def get_local_ip():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return '127.0.0.1'
    
    local_ip = get_local_ip()
    print("\n--- Serveur démarré ! URLs accessibles : ---")
    print(f"  → https://127.0.0.1:{port}/")
    print(f"  → https://{local_ip}:{port}/")
    print("------------------------------------------\n")
    
    # Recherche des certificats SSL
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    cert_file = os.path.join(current_dir, '..', 'cert.pem')
    key_file = os.path.join(current_dir, '..', 'key.pem')
    
    if os.path.exists(cert_file) and os.path.exists(key_file):
        uvicorn.run(app, host=host, port=port, ssl_certfile=cert_file, ssl_keyfile=key_file)
    else:
        print("⚠️ Certificats SSL non trouvés, démarrage en mode non sécurisé")
        uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    run_server()
