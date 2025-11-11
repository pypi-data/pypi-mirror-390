from pydantic import BaseModel, Field
from datetime import datetime


class AuthData(BaseModel):
    JWT: str = Field(..., description="JSON Web Token for authentication")
    Username: str = Field(..., description="User's email or username")
    Timestamp: datetime = Field(..., description="Timestamp when the token was issued")


