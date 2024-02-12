import json
import os

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.RequestController import RequestController
from app.database import get_db_session
from app.schemas.schemas import MeasurementsSchema

router = APIRouter()


@router.post("/")
def register_measurement(payload: MeasurementsSchema, db: Session = Depends(get_db_session)):

    controller = RequestController(db=db)
    try:
        response = controller.post('api/data/raw-data', json=payload.model_dump(exclude_none=True))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return Response(content=json.dumps(response.json()), status_code=200, media_type="application/json")

