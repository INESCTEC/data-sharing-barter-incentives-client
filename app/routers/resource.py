from fastapi import APIRouter
from pydantic import EmailStr
from fastapi.responses import JSONResponse

from app.schemas import ResourceSchema
from src.AgentManager import AgentManager

router = APIRouter()

ag = AgentManager()
ag.load_available_users()


@router.post("/register_resource/")
def register_resource(resource_data: ResourceSchema):
    ag.load_available_users()
    user = ag.get_user_by_email(email=resource_data.email)
    if not user:
        return JSONResponse(content={"message": f"User {resource_data.email} not found"}, status_code=400)
    try:
        response = ag.register_resource(user=user, resource_data=resource_data)
        wallet_user_list = ag.get_wallet_user_list()
        for wallet_user in wallet_user_list:
            if wallet_user['email'] == user['email']:
                if 'resources' not in wallet_user:
                    wallet_user['resources'] = []
                wallet_user['resources'].append({'name': resource_data.name, 'id':response['id']})
                ag.save_data_to_file(wallet_user_list)

        return JSONResponse({"message": response})
    except Exception as e:
        return JSONResponse(content={"message": f"Error registering resource: {repr(e)}"}, status_code=400)


@router.get("/list_resource/")
def list_resources():
    try:
        return JSONResponse({"resources": ag.get_resource()})
    except Exception as e:
        return JSONResponse(content={"message": f"Error listing resources: {repr(e)}"}, status_code=400)


# @router.delete("/delete_resource/")
# def delete_resource(email: EmailStr, resource_id: int):
#     try:
#         user = ag.get_user_by_email(email=email)
#         if not user:
#             return JSONResponse(content={"message": f"User {email} not found"}, status_code=400)
#         ag.login(user=user)
#         response = ag.delete_resource(resource_id=resource_id)
#         return JSONResponse({"message": response})
#     except Exception as e:
#         return JSONResponse(content={"message": f"Error deleting resource: {str(e)}"}, status_code=400)
