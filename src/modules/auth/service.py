from datetime import datetime
from sqlalchemy.orm import Session
from src.core.security import verify_password
from src.models import Usuario


class AuthService:
    @staticmethod
    def authenticate(db: Session, email: str, password: str):
        user = db.query(Usuario).filter(Usuario.email == email.strip().lower()).first()
        if not user:
            return None
        if not user.activo:
            return "inactivo"
        if not verify_password(password, user.password_hash):
            return None

        user.ultimo_acceso = datetime.utcnow()
        db.commit()
        return user

