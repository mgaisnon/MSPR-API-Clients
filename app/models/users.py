from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from models.address import Address

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    firstname = Column(String(50), nullable=False)
    lastname = Column(String(50), nullable=False)
    mail = Column(String(50), nullable=False)
    id_address = Column(Integer, ForeignKey("address.id"), nullable=True)

    address = relationship("Address", back_populates="users")
