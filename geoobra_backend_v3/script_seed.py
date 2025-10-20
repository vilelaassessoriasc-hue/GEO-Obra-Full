from app.db import SessionLocal
from app.models import User, Job
from app.utils.security import hash_password

db = SessionLocal()
try:
    emp = db.query(User).filter(User.email=="empresa@geoobra.com").first()
    if not emp:
        emp = User(email="empresa@geoobra.com", name="Construtora X", role="company",
                   password_hash=hash_password("senha123"), lat=-27.5969, lng=-48.5495)
        db.add(emp); db.commit(); db.refresh(emp)

    pro = db.query(User).filter(User.email=="pro@geoobra.com").first()
    if not pro:
        pro = User(email="pro@geoobra.com", name="Prof Geo", role="professional",
                   password_hash=hash_password("senha123"), lat=-27.5969, lng=-48.5495)
        db.add(pro); db.commit()

    if not db.query(Job).first():
        db.add(Job(title="Pedreiro", description="Alvenaria",
                   company_id=emp.id, lat=-27.5969, lng=-48.5495, radius_km=20))
        db.commit()
finally:
    db.close()
print("Seed OK")
