from fastapi import FastAPI, Request
from app.models import Api
from app import models
from app.db import SessionLocal
import json
import datetime
from time import time

def register_route(app: FastAPI, api: Api):
    async def dynamic_func(request: Request):
        db = SessionLocal()
        try:
            # Vérification du quota
            if api.quota > 0:
                now = datetime.datetime.utcnow()
                if api.quota_period == "hour":
                    start_time = now - datetime.timedelta(hours=1)
                elif api.quota_period == "day":
                    start_time = now - datetime.timedelta(days=1)
                else:  # month
                    start_time = now - datetime.timedelta(days=30)

                calls = db.query(models.ApiLog).filter(
                    models.ApiLog.api_id == api.id,
                    models.ApiLog.timestamp >= start_time
                ).count()

                if calls >= api.quota:
                    return ({"error": f"Quota dépassé: {api.quota} requêtes par {api.quota_period}"}, 429)

            status_code = api.status_code
            response = json.loads(api.response_json)
            start = time()
            # simulate delay if needed
            if api.delay_ms:
                import asyncio
                await asyncio.sleep(api.delay_ms / 1000)
            latency = (time() - start) * 1000
            # Log l'appel dans ApiLog
            log = models.ApiLog(api_id=api.id, timestamp=datetime.datetime.utcnow(), status_code=status_code, ip=request.client.host, latency_ms=latency)
            db.add(log)
            db.commit()
            return (response, status_code)
        finally:
            db.close()
    # remove preexisting conflict
    to_remove = []
    for route in list(app.router.routes):
        if getattr(route, 'path', None) == api.path and api.method in getattr(route, 'methods', set()):
            to_remove.append(route)
    for r in to_remove:
        try:
            app.router.routes.remove(r)
        except Exception:
            pass
    app.add_api_route(api.path, dynamic_func, methods=[api.method])

def reload_routes(app: FastAPI, db):
    apis = db.query(Api).filter(Api.enabled == True).all()
    for api in apis:
        register_route(app, api)
