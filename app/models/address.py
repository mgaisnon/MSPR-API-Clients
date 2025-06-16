from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base

class Address(Base):
    __tablename__ = "address"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(Integer, nullable=False)
    street = Column(String(100), nullable=False)
    city = Column(String(50), nullable=False)
    postcode = Column(String(20), nullable=False)

    users = relationship("Users", back_populates="address")