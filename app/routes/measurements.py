from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.dependencies import get_db_session, get_request_strategy
from app.helpers.helper import get_header
from app.schemas.schemas import MeasurementsSchema

router = APIRouter()


@router.post("/raw-data")
async def post_raw_data(payload: MeasurementsSchema,
                        request_strategy=Depends(get_request_strategy)):

    with get_db_session() as db:
        header = get_header(db=db)

        try:
            response = request_strategy.make_request(endpoint="/data/raw-data/",
                                                     method="post",
                                                     data=payload.model_dump(),
                                                     headers=header)
        except Exception as e:
            return JSONResponse(content={"error": str(e)}, status_code=500)

        return JSONResponse(content=response.json(), status_code=response.status_code)


@router.get("/forecast/{start_date}/{end_date}/{resource_id}")
async def get_forecast(start_date: str,
                       end_date: str,
                       resource_id: int,
                       request_strategy=Depends(get_request_strategy)):

    with get_db_session() as db:
        header = get_header(db=db)

        "data/market-forecasts/?start_date=2323432&end_date=432423423&resource=2"

        try:
            response = request_strategy.make_request(endpoint=f"/data/market-forecasts/?"
                                                              f"start_date={start_date}&"
                                                              f"end_date={end_date}&"
                                                              f"resource={resource_id}",
                                                     method="get",
                                                     headers=header)
        except Exception as e:
            return JSONResponse(content={"error": str(e)}, status_code=500)

        return JSONResponse(content=response.json(), status_code=response.status_code)