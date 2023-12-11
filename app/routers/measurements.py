from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.schemas import MeasurementsSchema
from src.AgentManager import AgentManager
from src.controller.exception.APIException import *

router = APIRouter()

ag = AgentManager()
ag.load_available_users()


@router.post("/send_measurements/")
def send_measurements(measurements: MeasurementsSchema):
    user = ag.get_user_by_email(email=measurements.email)
    # make sure the file is up-to-date
    ag.load_available_users()
    if not user:
        return JSONResponse(content={"message": f"User {measurements.email} not found"}, status_code=400)
    try:
        ag.send_measurements(user=user, data=measurements)
    except PostMeasurementsException as e:
        return JSONResponse(content={"message": f"Error sending measurements: {str(e)}"}, status_code=400)
    return JSONResponse({"message": f"Sent measurements for the resource {measurements.resource_name} sent!"})

