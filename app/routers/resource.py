import json
import os

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.RequestController import RequestController
from app.database import get_db_session
from app.schemas.schemas import ResourceSchema

router = APIRouter()


@router.get("/")
def list_resource(db: Session = Depends(get_db_session)):
    controller = RequestController(db=db)
    try:
        response = controller.get('api/user/resource')
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return Response(content=json.dumps(response.json()), status_code=200, media_type="application/json")


@router.post("/")
def register_resource(payload: ResourceSchema, db: Session = Depends(get_db_session)):

    controller = RequestController(db=db)
    try:
        response = controller.post('api/user/resource',
                                   json=payload.model_dump(exclude_none=True))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return Response(content=json.dumps(response.json()), status_code=200, media_type="application/json")


@router.patch("/{resource_id}")
def patch_resource(payload: ResourceSchema, resource_id: int, db: Session = Depends(get_db_session)):

    controller = RequestController(db=db)
    try:
        response = controller.patch(f'api/user/resource/{resource_id}',
                                    json=payload.model_dump(exclude_none=True))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return Response(content=json.dumps(response.json()), status_code=200, media_type="application/json")


@router.delete("/{resource_id}")
def delete_resource(resource_id: int, db: Session = Depends(get_db_session)):

    controller = RequestController(db=db)
    try:
        response = controller.delete(f'api/user/resource/{resource_id}')
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return Response(content=json.dumps(response.json()), status_code=200, media_type="application/json")
