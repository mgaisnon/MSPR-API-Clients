from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from .database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    address_postal_code = Column(String)
    address_city = Column(String)
    profile_first_name = Column(String)
    profile_last_name = Column(String)
    company_name = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
