import uuid
import numpy as np
import pandas as pd

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.dependencies import get_db_session, get_request_strategy, get_current_user
from app.helpers.helper import get_header
from app.schemas.schemas import MeasurementsSchema
from app.models.models import User
from fastapi import Security

router = APIRouter()


@router.post("/raw-data")
async def post_raw_data(payload: MeasurementsSchema,
                        request_strategy=Depends(get_request_strategy),
                        db=Depends(get_db_session),
                        user: User = Security(get_current_user)):
    header = get_header(db=db, user_email=user.email)

    try:
        response = request_strategy.make_request(endpoint="/data/raw-data/",
                                                 method="post",
                                                 data=payload.model_dump(),
                                                 headers=header)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

    return JSONResponse(content=response.json(), status_code=response.status_code)


@router.get("/raw-data/{start_date}/{end_date}/{resource_id}")
async def get_raw_data(start_date: str,
                       end_date: str,
                       resource_id: uuid.UUID,
                       request_strategy=Depends(get_request_strategy),
                       user: User = Security(get_current_user),
                       db=Depends(get_db_session)):
    try:
        header = get_header(db=db, user_email=user.email)
        endpoint = f"data/raw-data/?start_date={start_date}&end_date={end_date}&resource={resource_id}"
        response = request_strategy.make_request(endpoint=endpoint,
                                                 method="get",
                                                 headers=header)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

    return JSONResponse(content=response.json(), status_code=response.status_code)


@router.get("/forecast/{start_date}/{end_date}/{resource_id}")
async def get_forecast(start_date: str,
                       end_date: str,
                       resource_id: uuid.UUID,
                       request_strategy=Depends(get_request_strategy),
                       user: User = Security(get_current_user),
                       db=Depends(get_db_session)):
    try:
        header = get_header(db=db, user_email=user.email)
        response = request_strategy.make_request(endpoint=f"/data/market-forecasts/?"
                                                          f"start_date={start_date}&"
                                                          f"end_date={end_date}&"
                                                          f"resource={resource_id}",
                                                 method="get",
                                                 headers=header)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

    return JSONResponse(content=response.json(), status_code=response.status_code)


@router.get("/available-data/{start_date}/{end_date}/{resource_id}")
async def get_forecast(start_date: str,
                       end_date: str,
                       resource_id: uuid.UUID,
                       request_strategy=Depends(get_request_strategy),
                       user: User = Security(get_current_user),
                       db=Depends(get_db_session)):
    try:
        header = get_header(db=db, user_email=user.email)
        rsp_forecasts = request_strategy.make_request(endpoint=f"/data/market-forecasts/?"
                                                               f"start_date={start_date}&"
                                                               f"end_date={end_date}&"
                                                               f"resource={resource_id}",
                                                      method="get",
                                                      headers=header)

        # Get existing measurements:
        rsp_measurements = request_strategy.make_request(endpoint=f"/data/raw-data/?"
                                                                  f"start_date={start_date}&"
                                                                  f"end_date={end_date}&"
                                                                  f"resource={resource_id}",
                                                         method="get",
                                                         headers=header)

        # Expected_dates
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        start_date = start_date.replace(minute=0, second=0, microsecond=0)
        end_date = end_date.replace(minute=0, second=0, microsecond=0)
        expected_dates = pd.date_range(start_date, end_date, freq="H")
        dataset = pd.DataFrame(index=expected_dates)

        # Convert response timeseries data into dataframes:
        data_forecasts = pd.DataFrame(rsp_forecasts.json()["data"])
        data_measurements = pd.DataFrame(rsp_measurements.json()["data"])

        if not data_forecasts.empty:
            data_forecasts = data_forecasts[["datetime", "value"]].rename(columns={"value": "forecasts"})
            data_forecasts["datetime"] = pd.to_datetime(data_forecasts["datetime"])
            # Drop duplicates (datetime)
            data_forecasts = data_forecasts.drop_duplicates(subset="datetime")
            # Set index:
            data_forecasts.set_index("datetime", inplace=True)
        else:
            data_forecasts = pd.DataFrame(index=expected_dates,
                                          columns=["forecasts"])
            data_forecasts["forecasts"] = None

        if not data_measurements.empty:
            data_measurements = data_measurements[["datetime", "value"]].rename(columns={"value": "measurements"})
            data_measurements["datetime"] = pd.to_datetime(data_measurements["datetime"])
            data_measurements.set_index("datetime", inplace=True)
        else:
            data_measurements = pd.DataFrame(index=expected_dates,
                                             columns=["measurements"])
            data_measurements["measurements"] = None

        # Merge based on datetime:
        dataset = dataset.join(data_forecasts).join(data_measurements)
        # dataset.fillna(0, inplace=True)
        dataset["resource"] = resource_id
        dataset.index.name = "datetime"
        dataset.reset_index(drop=False, inplace=True)
        dataset["datetime"] = dataset["datetime"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        dataset = dataset.replace({np.nan: None})
        # print(dataset.head(5))
        response_json = dataset.to_dict(orient="records")
        # print(response_json)
        # Prepare final response:
        response = {
            "code": 200,
            "data": response_json
        }

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

    return JSONResponse(content=response, status_code=200)
