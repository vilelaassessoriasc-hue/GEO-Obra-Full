from pathlib import Path
from fastapi.encoders import jsonable_encoder
from fastapi.openapi.utils import get_openapi

# Importa o app FastAPI
try:
    from app.main import app
except Exception as e:
    raise SystemExit(f"Erro ao importar app.main: {e}")

out_dir = Path("openapi_export")
out_dir.mkdir(parents=True, exist_ok=True)

schema = get_openapi(
    title=app.title if hasattr(app, "title") else "Geo Obra API",
    version="1.0.0",
    routes=app.routes,
    description=getattr(app, "description", "API Geo-Obra")
)

openapi_path = out_dir / "openapi.json"
openapi_path.write_text(app.json_dumps(jsonable_encoder(schema), indent=2), encoding="utf-8")

# Redoc estático simples (sem dependência externa)
html = f\"\"\"<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>Geo Obra API — Redoc</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>body,html,#redoc{{height:100%;margin:0;padding:0;}} </style>
  <script src="https://cdn.jsdelivr.net/npm/redoc/bundles/redoc.standalone.min.js"></script>
</head>
<body>
  <div id="redoc"></div>
  <script>
    Redoc.init('./openapi.json', {{}}, document.getElementById('redoc'));
  </script>
</body>
</html>\"\"\"
(out_dir / "redoc.html").write_text(html, encoding="utf-8")

print(f"✔ OpenAPI exportado em {openapi_path}")
print(f"✔ Redoc gerado em {out_dir/'redoc.html'}")
