import os
import json
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from models import Dataset, Experiment, User
from routers.auth_routes import get_current_user
from ml.trainer import train_all_models

router = APIRouter()

UPLOAD_DIR = "storage/datasets"


class TrainRequest(BaseModel):
    dataset_id: int
    target_column: str


@router.post("/train")
def train_models(
    request: TrainRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Make sure this dataset belongs to the logged-in user
    dataset = db.query(Dataset).filter(
        Dataset.id == request.dataset_id,
        Dataset.owner_id == current_user.id,
    ).first()

    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    file_path = os.path.join(UPLOAD_DIR, dataset.filename)
    df = pd.read_csv(file_path)

    if request.target_column not in df.columns:
        raise HTTPException(status_code=400, detail=f"Column '{request.target_column}' not found in dataset")

    try:
        results = train_all_models(df, request.target_column)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    new_experiment = Experiment(
        owner_id=current_user.id,
        dataset_id=dataset.id,
        target_column=request.target_column,
        results=json.dumps(results),
    )
    db.add(new_experiment)
    db.commit()
    db.refresh(new_experiment)

    return {
        "experiment_id": new_experiment.id,
        "target_column": request.target_column,
        "results": results,
    }


@router.get("/")
def list_experiments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    experiments = db.query(Experiment).filter(Experiment.owner_id == current_user.id).all()
    return [
        {
            "id": exp.id,
            "dataset_id": exp.dataset_id,
            "target_column": exp.target_column,
            "results": json.loads(exp.results),
            "created_at": exp.created_at,
        }
        for exp in experiments
    ]