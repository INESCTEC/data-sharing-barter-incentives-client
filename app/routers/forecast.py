import json
from datetime import datetime
import urllib.parse
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.RequestController import RequestController
from app.database import get_db_session

router = APIRouter()


@router.get("/{start_date}/{end_date}/{resource_id}")
def list_forecast(start_date: datetime, end_date: datetime, resource_id: int, db: Session = Depends(get_db_session)):
    controller = RequestController(db=db)
    # Format the datetime objects to ISO 8601 format with 'Z' notation for UTC
    formatted_start_date = start_date.isoformat().replace("+00:00", "Z")
    formatted_end_date = end_date.isoformat().replace("+00:00", "Z")
    # URL encode the parameters
    start_date_encoded = urllib.parse.quote(formatted_start_date)
    end_date_encoded = urllib.parse.quote(formatted_end_date)
    try:
        response = controller.get(f'api/data/market-forecasts?'
                                  f'start_date={start_date_encoded}&end_date={end_date_encoded}&resource={resource_id}')

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return Response(content=json.dumps(response.json()), status_code=200, media_type="application/json")
