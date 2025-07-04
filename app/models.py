# app/models.py
from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    empId: int
    name: str
    address: str
    phone: int

    model_config = {
        "from_attributes": True
    }

class CreateUser(BaseModel):
    name: str
    address: str
    phone: int

class UpdateUser(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[int] = None
