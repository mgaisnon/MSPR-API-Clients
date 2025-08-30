from pydantic import BaseModel
from datetime import datetime


class CustomerBase(BaseModel):
    name: str
    username: str
    first_name: str
    last_name: str
    address_postal_code: str
    address_city: str
    profile_first_name: str
    profile_last_name: str
    company_name: str


class CustomerCreate(CustomerBase):
    pass


class Customer(CustomerBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
