from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app import crud, schemas

router = APIRouter(prefix="/connections", tags=["Connections"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 1. Send request
@router.post("/send", response_model=schemas.ConnectionRequestOut)
def send_request(sender_id: int, req: schemas.ConnectionRequestCreate, db: Session = Depends(get_db)):
    if sender_id == req.receiver_id:
        raise HTTPException(status_code=400, detail="You cannot send a request to yourself")
    return crud.send_request(db, sender_id, req.receiver_id)

# 2. Accept request
@router.post("/{request_id}/accept", response_model=schemas.ConnectionRequestOut)
def accept_request(request_id: int, db: Session = Depends(get_db)):
    updated = crud.update_request(db, request_id, schemas.RequestStatus.accepted)
    if not updated:
        raise HTTPException(status_code=404, detail="Request not found")
    return updated

# 3. Reject request
@router.post("/{request_id}/reject", response_model=schemas.ConnectionRequestOut)
def reject_request(request_id: int, db: Session = Depends(get_db)):
    updated = crud.update_request(db, request_id, schemas.RequestStatus.rejected)
    if not updated:
        raise HTTPException(status_code=404, detail="Request not found")
    return updated
