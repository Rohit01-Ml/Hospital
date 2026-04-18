from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.auth.schemas import RegisterRequest, LoginRequest, GoogleAuthRequest
from app.auth.service import login_user, register_user, google_auth
from app.dependencies import get_current_user, get_db

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    result, error = register_user(req.name, req.email, req.password, db, req.role)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return result


@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    result = login_user(req.email, req.password, db)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return result


@router.post("/google")
def google_login(req: GoogleAuthRequest, db: Session = Depends(get_db)):
    email = req.email or "google_user@gmail.com"
    name  = req.name  or "Google User"
    return google_auth(email, name, db)


@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    return {k: v for k, v in current_user.items() if k != "password_hash"}
