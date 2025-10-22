import os, sys, pathlib, sqlite3, traceback
from datetime import datetime

print("=== GEO OBRA: DIAGNÓSTICO + SEED ===")

# 1) Mostrar diretório atual
print("CWD:", os.getcwd())

# 2) Tentar carregar settings da app (DATABASE_URL)
try:
    from geoobra_backend_v3.app.core.config import settings
    db_url = settings.DATABASE_URL
    print("DATABASE_URL (settings):", db_url)
except Exception as e:
    print("!! Não consegui importar app.core.config.settings. Tentando .env manualmente...")
    db_url = None

# 3) Se não veio do settings, tenta ler .env manualmente
if not db_url:
    # fallback: tenta carregar de .env (opcional)
    # se você usa pydantic_settings com env_file, rodando daqui já deveria bastar.
    # então só lemos variável de ambiente se existir:
    db_url = os.environ.get("DATABASE_URL", ""sqlite:///./dev.db"")
    print("DATABASE_URL (fallback):", db_url)

# 4) Resolver caminho do SQLite (se for sqlite:///./arquivo.db)
sqlite_path = None
if db_url.startswith("sqlite:///"):
    raw = db_url.replace("sqlite:///", "", 1)
    sqlite_path = pathlib.Path(raw).resolve()
    print("SQLite path absoluto:", sqlite_path)
    print("Existe antes de conectar? ", sqlite_path.exists())

# 5) Garantir metadata e abrir sessão
try:
    from geoobra_backend_v3.app.db import Base, engine, SessionLocal
    print("Importei Base/engine/SessionLocal.")
except Exception as e:
    print("ERRO import app.db:", e)
    traceback.print_exc()
    sys.exit(1)

# create_all para garantir tabelas
try:
    Base.metadata.create_all(bind=engine)
    print("create_all() OK")
except Exception as e:
    print("ERRO create_all:", e)
    traceback.print_exc()
    sys.exit(1)

# 6) Inserir dados (empresa, pro, vaga)
try:
    from geoobra_backend_v3.app.models import User, Job
    from geoobra_backend_v3.app.utils.security import hash_password
    db = SessionLocal()
    try:
        emp = db.query(User).filter(User.email=="empresa@geoobra.com").first()
        if not emp:
            emp = User(
                email="empresa@geoobra.com", name="Construtora X", role="company",
                password_hash=hash_password("senha123"), lat=-27.5969, lng=-48.5495,
                created_at=datetime.utcnow(),
            )
            db.add(emp); db.commit(); db.refresh(emp)
            print("Empresa criada:", emp.id, emp.email)
        else:
            print("Empresa já existia:", emp.id, emp.email)

        pro = db.query(User).filter(User.email=="pro@geoobra.com").first()
        if not pro:
            pro = User(
                email="pro@geoobra.com", name="Prof Geo", role="professional",
                password_hash=hash_password("senha123"), lat=-27.5969, lng=-48.5495,
                created_at=datetime.utcnow(),
            )
            db.add(pro); db.commit(); db.refresh(pro)
            print("Profissional criado:", pro.id, pro.email)
        else:
            print("Profissional já existia:", pro.id, pro.email)

        j = db.query(Job).first()
        if not j:
            j = Job(
                title="Pedreiro", description="Alvenaria", company_id=emp.id,
                lat=-27.5969, lng=-48.5495, radius_km=20, created_at=datetime.utcnow(),
            )
            db.add(j); db.commit(); db.refresh(j)
            print("Vaga criada:", j.id, j.title)
        else:
            print("Já havia vaga:", j.id, j.title)
    finally:
        db.close()
    print("Seed concluído.")
except Exception as e:
    print("ERRO no seed:", e)
    traceback.print_exc()
    sys.exit(1)

# 7) Conferir conteúdo do banco via sqlite3 (apenas se for sqlite)
if sqlite_path:
    try:
        con = sqlite3.connect(str(sqlite_path))
        cur = con.cursor()
        users = list(cur.execute("SELECT id,email,role,length(password_hash) FROM users"))
        jobs  = list(cur.execute("SELECT id,title,company_id FROM jobs"))
        print("USERS:", users)
        print("JOBS:", jobs)
    except Exception as e:
        print("ERRO lendo sqlite direto:", e)
    finally:
        try: con.close()
        except: pass

print("=== FIM ===")


