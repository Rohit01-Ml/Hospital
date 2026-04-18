from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.database import get_db

SECRET_KEY = "hospital-super-secret-key-2024"
ALGORITHM  = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> dict:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id:
            raise ValueError
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    from app.models import User
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user.to_dict()


def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db),
):
    if not credentials:
        return None
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            return None
        from app.models import User
        user = db.query(User).filter(User.id == user_id).first()
        return user.to_dict() if user else None
    except Exception:
        return None


def require_admin(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


def require_patient(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "patient":
        raise HTTPException(status_code=403, detail="Patient access required")
    return current_user


def require_doctor(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "doctor":
        raise HTTPException(status_code=403, detail="Doctor access required")
    return current_user


def require_doctor_or_admin(current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ("doctor", "admin"):
        raise HTTPException(status_code=403, detail="Doctor or Admin access required")
    return current_user


def require_receptionist(current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ("receptionist", "admin"):
        raise HTTPException(status_code=403, detail="Receptionist access required")
    return current_user


def require_staff(current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ("admin", "doctor", "receptionist"):
        raise HTTPException(status_code=403, detail="Staff access required")
    return current_user
