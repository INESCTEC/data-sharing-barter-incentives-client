from typing import List
from pydantic import BaseModel, Field
from pydantic import UUID4
from datetime import datetime


class ResourceSchema(BaseModel):
    name: str = Field(..., example="resource-3")
    type: str = Field(..., example="measurements")
    to_forecast: bool = Field(True, example=False)


class ResourceOutputData(BaseModel):
    id: UUID4
    name: str
    type: str
    to_forecast: bool
    registered_at: datetime
    user: UUID4


class ResourceOutputSchemaGET(BaseModel):
    code: int
    data: List[ResourceOutputData]


class ResourceOutputSchema(BaseModel):
    code: int
    data: ResourceOutputData
