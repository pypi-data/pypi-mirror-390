from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi.responses import HTMLResponse
from ..db import get_db
from app import models, schemas
from ..services.dynamic_routes import register_route, reload_routes
import json
from fastapi.templating import Jinja2Templates
from fastapi import Request

templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

@router.get("/admin", response_class=HTMLResponse)
def admin_ui(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})

@router.get("/admin/apis")
def list_apis(db: Session = Depends(get_db)):
    return db.query(models.Api).all()

@router.post("/admin/apis")
def create_api(api: schemas.ApiCreate, db: Session = Depends(get_db), request: Request = None):
    api_dict = api.dict()
    api_dict["response_json"] = json.dumps(api_dict["response_json"])  # Conversion dict -> str
    db_api = models.Api(**api_dict)
    db.add(db_api)
    db.commit()
    db.refresh(db_api)
    register_route(request.app, db_api)
    return db_api

@router.delete("/admin/apis/{api_id}")
def delete_api(api_id: int, db: Session = Depends(get_db)):
    obj = db.query(models.Api).filter(models.Api.id == api_id).first()
    if not obj: return {"deleted": 0}
    db.delete(obj)
    db.commit()
    return {"deleted": 1}

@router.post("/admin/reload")
def reload_all(db: Session = Depends(get_db), request: Request = None):
    reload_routes(request.app, db)
    return {"reloaded": "ok"}

@router.post("/admin/apis/{api_id}/enabled")
async def set_api_enabled(api_id: int, db: Session = Depends(get_db), request: Request = None):
    try:
        body = await request.json()
    except Exception:
        try:
            body = json.loads(await request.body())
        except Exception:
            body = {}
    enabled = body.get('enabled')
    api = db.query(models.Api).filter(models.Api.id == api_id).first()
    if not api:
        return {"updated": 0}
    api.enabled = bool(enabled)
    db.commit()
    return {"updated": 1, "enabled": api.enabled}

@router.get("/admin/apis/{api_id}/stats", response_class=HTMLResponse)
def api_stats(api_id: int, db: Session = Depends(get_db), request: Request = None):
    api = db.query(models.Api).filter(models.Api.id == api_id).first()
    if not api:
        return templates.TemplateResponse("api_stats.html", {"request": request, "api": None, "api_id": api_id})
    logs = db.query(models.ApiLog).filter(models.ApiLog.api_id == api_id).order_by(models.ApiLog.timestamp.desc()).limit(10).all()
    total = db.query(models.ApiLog).filter(models.ApiLog.api_id == api_id).count()
    success = db.query(models.ApiLog).filter(models.ApiLog.api_id == api_id, models.ApiLog.status_code >= 200, models.ApiLog.status_code < 300).count()
    failed = db.query(models.ApiLog).filter(models.ApiLog.api_id == api_id, models.ApiLog.status_code >= 400).count()
    avg_latency = db.query(func.avg(models.ApiLog.latency_ms)).filter(models.ApiLog.api_id == api_id).scalar() or 0
    return templates.TemplateResponse("api_stats.html", {
        "request": request,
        "api": api,
        "logs": logs,
        "total": total,
        "success": success,
        "failed": failed,
        "avg_latency": f"{avg_latency:.1f}",
        "api_id": api_id
    })

@router.post("/admin/projects")
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    db_project = models.Project(name=project.name, description=project.description)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.get("/admin/projects")
def list_projects(db: Session = Depends(get_db)):
    return db.query(models.Project).all()

@router.post("/admin/projects/{project_id}/apis/{api_id}")
def add_api_to_project(project_id: int, api_id: int, db: Session = Depends(get_db)):
    api = db.query(models.Api).filter(models.Api.id == api_id).first()
    if not api:
        return {"error": "API non trouvée"}
    api.project_id = project_id
    db.commit()
    return {"added": True}

@router.delete("/admin/projects/{project_id}/apis/{api_id}")
def remove_api_from_project(project_id: int, api_id: int, db: Session = Depends(get_db)):
    api = db.query(models.Api).filter(models.Api.id == api_id, models.Api.project_id == project_id).first()
    if not api:
        return {"error": "API non trouvée dans le projet"}
    api.project_id = None
    db.commit()
    return {"removed": True}

@router.delete("/admin/projects/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        return {"deleted": 0}
    # Dissocier toutes les APIs du projet
    apis = db.query(models.Api).filter(models.Api.project_id == project_id).all()
    for api in apis:
        api.project_id = None
    db.delete(project)
    db.commit()
    return {"deleted": 1}