from pydantic import Field, BaseModel
from typing import Generic, TypeVar, Optional

T = TypeVar("T")

class WebServiceResponse(BaseModel, Generic[T]):
    success: bool = Field(..., description="Indicates if the request was successful")
    msg: str = Field(..., description="Optional message from the API")
    data: Optional[T] = Field(None, description="Container for typed response data")
    time: Optional[float] = Field(None, description="Processing time in milliseconds or seconds")
    executionTime: Optional[float] = Field(None, description="Processing time in milliseconds or seconds")