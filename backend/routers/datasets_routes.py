import os
import pandas as pd
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Dataset, User
from routers.auth_routes import get_current_user

router = APIRouter()

UPLOAD_DIR = "storage/datasets"

@router.post("/upload")
def upload_dataset(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Save the file with a unique name to avoid collisions
    safe_filename = f"{current_user.id}_{datetime.utcnow().timestamp()}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(file.file.read())

    # Try parsing it with pandas to make sure it's a real CSV
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not parse CSV: {str(e)}")

    # Save metadata to the database
    new_dataset = Dataset(
        owner_id=current_user.id,
        filename=safe_filename,
        upload_date=datetime.utcnow(),
    )
    db.add(new_dataset)
    db.commit()
    db.refresh(new_dataset)

    return {
        "id": new_dataset.id,
        "filename": new_dataset.filename,
        "rows": len(df),
        "columns": list(df.columns),
        "missing_values": df.isnull().sum().to_dict(),
    }


@router.get("/")
def list_datasets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    datasets = db.query(Dataset).filter(Dataset.owner_id == current_user.id).all()
    return datasets