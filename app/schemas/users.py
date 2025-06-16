from pydantic import BaseModel

class User(BaseModel):
    firstname: str
    lastname: str
    mail: str
    id_address: int | None = None

    class Config:
        orm_mode = True
