from pydantic import BaseModel

class Address(BaseModel):
    number: int
    street: str
    city: str
    postcode: str

    class Config:
        orm_mode = True
