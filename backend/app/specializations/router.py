import uuid
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.specializations.schemas import SpecializationCreate, SpecializationUpdate
from app.database import get_db
from app.models import Specialization
from app.dependencies import require_admin

router = APIRouter(prefix="/specializations", tags=["Specializations"])


@router.get("/")
def list_specializations(db: Session = Depends(get_db)):
    return [s.to_dict() for s in db.query(Specialization).all()]


@router.get("/{spec_id}")
def get_specialization(spec_id: str, db: Session = Depends(get_db)):
    s = db.query(Specialization).filter(Specialization.id == spec_id).first()
    if not s:
        raise HTTPException(404, "Specialization not found")
    return s.to_dict()


@router.post("/", dependencies=[Depends(require_admin)])
def create_specialization(req: SpecializationCreate, db: Session = Depends(get_db)):
    s = Specialization(id=str(uuid.uuid4())[:10], **req.model_dump())
    db.add(s)
    db.commit()
    db.refresh(s)
    return s.to_dict()


@router.put("/{spec_id}", dependencies=[Depends(require_admin)])
def update_specialization(spec_id: str, req: SpecializationUpdate, db: Session = Depends(get_db)):
    s = db.query(Specialization).filter(Specialization.id == spec_id).first()
    if not s:
        raise HTTPException(404, "Specialization not found")
    for k, v in req.model_dump(exclude_none=True).items():
        setattr(s, k, v)
    db.commit()
    db.refresh(s)
    return s.to_dict()


@router.delete("/{spec_id}", dependencies=[Depends(require_admin)])
def delete_specialization(spec_id: str, db: Session = Depends(get_db)):
    s = db.query(Specialization).filter(Specialization.id == spec_id).first()
    if not s:
        raise HTTPException(404, "Specialization not found")
    db.delete(s)
    db.commit()
    return {"message": "Deleted"}
