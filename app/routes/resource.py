import json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, Security
from sqlalchemy.orm import Session

from app.apis.RequestStrategy import RequestContext
from app.dependencies import get_db_session, get_request_strategy, get_current_user
from app.helpers.helper import get_header
from app.models.models import User
from app.schemas.resources.schema import ResourceSchema, ResourceOutputSchemaGET, ResourceOutputSchema

router = APIRouter()


@router.get("/", response_model=ResourceOutputSchemaGET)
def list_resource(request_strategy: RequestContext = Depends(get_request_strategy),
                  db: Session = Depends(get_db_session),
                  user: User = Security(get_current_user)):
    try:
        header = get_header(db=db)
        response = request_strategy.make_request(endpoint='/user/resource/',
                                                 method='get',
                                                 headers=header)

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return Response(content=json.dumps(response.json()),
                    status_code=200,
                    media_type="application/json")


@router.post("/", response_model=ResourceOutputSchema)
def register_resource(payload: ResourceSchema,
                      request_strategy: RequestContext = Depends(get_request_strategy),
                      user: User = Security(get_current_user),
                      db: Session = Depends(get_db_session)):
    try:
        header = get_header(db=db)
        response = request_strategy.make_request(endpoint='/user/resource/',
                                                 method='post',
                                                 headers=header,
                                                 data=payload.model_dump(exclude_none=True))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return Response(content=json.dumps(response.json()), status_code=200, media_type="application/json")


@router.patch("/{resource_id}", response_model=ResourceOutputSchema)
def patch_resource(payload: ResourceSchema,
                   resource_id: UUID,
                   request_strategy: RequestContext = Depends(get_request_strategy),
                   user: User = Security(get_current_user),
                   db: Session = Depends(get_db_session)):
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
def delete_resource(resource_id: UUID,
                    request_strategy: RequestContext = Depends(get_request_strategy),
                    user: User = Security(get_current_user),
                    db: Session = Depends(get_db_session)):
    try:
        header = get_header(db=db)
        response = request_strategy.make_request(endpoint=f'/user/resource/{resource_id}',
                                                 method='delete',
                                                 headers=header)
        
        return Response(content=json.dumps(response.json()), status_code=200, media_type="application/json")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
