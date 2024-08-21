from typing import List

from pydantic import BaseModel
from pydantic import Field


class TimeSeriesItem(BaseModel):
    datetime: str = Field(..., examples=["2020-01-01 00:00:00"])
    value: float = Field(..., examples=[1.0])


class MeasurementsSchema(BaseModel):
    resource_name: str = Field(..., examples=["resource-3"])
    time_interval: int = Field(..., examples=[60])
    aggregation_type: str = Field(..., examples=["avg"])
    units: str = Field(..., examples=["kw"])
    timeseries: List[TimeSeriesItem]

    # @field_validator('resource_name')
    # def validate_resource_name(cls, resource_name, values):
    #
    #     user_file_dir = os.environ["USERS_FILE_DIR"]
    #     with open(os.path.join(user_file_dir, 'users.json'), "r") as f:
    #         users = json.load(f)
    #
    #     for user in users:
    #         if user['email'] == values.data.get('email'):
    #             valid_resources = [resource['name'] for resource in user['resources']]
    #             if resource_name in valid_resources:
    #                 return resource_name
    #             else:
    #                 raise ValueError("Invalid resource name.")
    #     raise ValueError(f"Invalid email.")
