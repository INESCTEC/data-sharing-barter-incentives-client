import json

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.apis.RequestStrategy import RequestContext
from app.dependencies import get_db_session, get_request_strategy
from app.helpers.helper import get_header
from app.schemas.schemas import ResourceSchema

router = APIRouter()


@router.get("/")
def list_resource(db: Session = Depends(get_db_session),
                  request_strategy: RequestContext = Depends(get_request_strategy)):
    try:
        header = get_header(db=db)
        response = request_strategy.make_request(endpoint='/user/resource/',
                                                 method='get',
                                                 headers=header)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return Response(content=json.dumps(response.json()), status_code=200, media_type="application/json")


@router.post("/")
def register_resource(payload: ResourceSchema,
                      db: Session = Depends(get_db_session),
                      request_strategy: RequestContext = Depends(get_request_strategy)):
    try:
        header = get_header(db=db)
        response = request_strategy.make_request(endpoint='/user/resource/',
                                                 method='post',
                                                 headers=header,
                                                 data=payload.model_dump(exclude_none=True))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return Response(content=json.dumps(response.json()), status_code=200, media_type="application/json")


@router.patch("/{resource_id}")
def patch_resource(payload: ResourceSchema,
                   resource_id: int,
                   db: Session = Depends(get_db_session),
                   request_strategy: RequestContext = Depends(get_request_strategy)):

    try:
        header = get_header(db=db)
        response = request_strategy.make_request(endpoint=f'/user/resource/{resource_id}',
                                                 method='patch',
                                                 headers=header,
                                                 data=payload.model_dump(exclude_none=True))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return Response(content=json.dumps(response.json()), status_code=200, media_type="application/json")


@router.delete("/{resource_id}")
def delete_resource(resource_id: int,
                    db: Session = Depends(get_db_session),
                    request_strategy: RequestContext = Depends(get_request_strategy)):

    try:
        header = get_header(db=db)
        response = request_strategy.make_request(endpoint=f'/user/resource/{resource_id}',
                                                 method='delete',
                                                 headers=header)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return Response(content=json.dumps(response.json()), status_code=200, media_type="application/json")
