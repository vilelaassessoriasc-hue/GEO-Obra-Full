from fastapi import APIRouter
from sqlalchemy import text, inspect
from geoobra_backend_v3.app.db.session import engine

router = APIRouter(prefix="/_debug", tags=["_debug"])

@router.get("/tables")
def list_tables():
    insp = inspect(engine)
    url = str(engine.url)
    if "@" in url:
        url = url.replace("//", "//***hidden***@", 1)
    return {
        "url": url,
        "dialect": engine.dialect.name,
        "tables": sorted(insp.get_table_names()),
    }

@router.get("/ping")
def ping_db():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"db": "ok"}

from typing import List, Dict
from fastapi import Query

@router.get("/columns")
def columns(table: str = Query(..., description="Nome da tabela")):
    from sqlalchemy import inspect
    insp = inspect(engine)
    if table not in insp.get_table_names():
        return {"table": table, "exists": False, "columns": []}
    cols = []
    for c in insp.get_columns(table):
        cols.append({
            "name": c.get("name"),
            "type": str(c.get("type")),
            "nullable": c.get("nullable"),
            "default": str(c.get("default")),
            "primary_key": bool(c.get("primary_key")),
        })
    return {"table": table, "exists": True, "columns": cols}

@router.get("/schema")
def schema():
    from sqlalchemy import inspect
    insp = inspect(engine)
    out: Dict[str, List[dict]] = {}
    for t in sorted(insp.get_table_names()):
        cols = []
        for c in insp.get_columns(t):
            cols.append({
                "name": c.get("name"),
                "type": str(c.get("type")),
                "nullable": c.get("nullable"),
                "default": str(c.get("default")),
                "primary_key": bool(c.get("primary_key")),
            })
        out[t] = cols
    return {"dialect": engine.dialect.name, "url": str(engine.url), "tables": out}
