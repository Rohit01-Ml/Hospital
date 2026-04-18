import uuid
from datetime import datetime, timedelta
from jose import jwt
import bcrypt
from sqlalchemy.orm import Session
from app.dependencies import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


def _hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _verify(password: str, hashed: str) -> bool:
    if hashed.startswith("plain:"):
        return password == hashed[len("plain:"):]
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception:
        return False


def _token(user_id: str) -> str:
    exp = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": user_id, "exp": exp}, SECRET_KEY, algorithm=ALGORITHM)


def _response(user_dict: dict) -> dict:
    safe = {k: v for k, v in user_dict.items() if k != "password_hash"}
    return {"access_token": _token(user_dict["id"]), "token_type": "bearer", "user": safe}


def login_user(email: str, password: str, db: Session):
    from app.models import User
    user = db.query(User).filter(User.email == email).first()
    if not user or not _verify(password, user.password_hash):
        return None
    return _response(user.to_dict())


def register_user(name: str, email: str, password: str, db: Session, role: str = "patient"):
    from app.models import User
    if db.query(User).filter(User.email == email).first():
        return None, "Email already registered"
    user = User(
        id=str(uuid.uuid4())[:12],
        name=name,
        email=email,
        password_hash=_hash(password),
        role=role,
        created_at=datetime.utcnow().isoformat(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _response(user.to_dict()), None


def google_auth(email: str, name: str, db: Session):
    from app.models import User
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            id=str(uuid.uuid4())[:12],
            name=name,
            email=email,
            password_hash=_hash("oauth_no_password"),
            role="patient",
            created_at=datetime.utcnow().isoformat(),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return _response(user.to_dict())
