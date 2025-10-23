import os, sys, json
from fastapi.testclient import TestClient

# Usa a pasta atual como raiz do projeto (executar este script da raiz!)
root = os.path.abspath(os.getcwd())
if root not in sys.path:
    sys.path.insert(0, root)

app = None
errors = []

# Tenta caminho oficial, depois fallback
try:
    from geoobra_backend_v3.app.main import app as _app
    app = _app
except Exception as e:
    errors.append(("geoobra_backend_v3.app.main:app", repr(e)))
    try:
        from app.main import app as _app2
        app = _app2
    except Exception as e2:
        errors.append(("app.main:app", repr(e2)))

if app is None:
    print("IMPORT_ERROR:", errors)
    raise SystemExit(2)

# Lista rotas
try:
    routes = []
    for r in getattr(app, "routes", []):
        path = getattr(r, "path", None) or getattr(r, "path_format", None) or str(r)
        methods = sorted(list(getattr(r, "methods", set())))
        routes.append({"path": path, "methods": methods})
    print("ROUTES:", json.dumps(routes, ensure_ascii=False)[:1500])
except Exception as e:
    print("ROUTES_INSPECT_ERROR:", repr(e))

# Testa endpoints básicos
client = TestClient(app)
candidates = ["/health", "/api/health", "/docs", "/"]
ok = False
for p in candidates:
    try:
        r = client.get(p)
        print(f"TRY {p} -> {r.status_code}")
        if r.status_code < 500:
            print("BODY_PREVIEW:", (r.text or "")[:200].replace("\\n"," "))
            ok = True
    except Exception as e:
        print(f"TRY {p} -> EXC {e!r}")

if not ok:
    raise SystemExit("SMOKE_FAIL: nenhum endpoint básico respondeu (<500)")
print("SMOKE_OK ✅")
