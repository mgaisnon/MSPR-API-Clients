import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from . import crud, schemas, models

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
models.Base.metadata.create_all(bind=engine)


def init_data():
    db = SessionLocal()
    response = requests.get(
        "https://615f5fb4f7254d0017068109.mockapi.io/api/v1/customers"
    )
    data = response.json()
    for item in data:
        existing = (
            db.query(models.Customer)
            .filter(models.Customer.username == item["username"])
            .first()
        )
        if not existing:
            customer_data = schemas.CustomerCreate(
                name=item["name"],
                username=item["username"],
                first_name=item["firstName"],
                last_name=item["lastName"],
                address_postal_code=item["address"]["postalCode"],
                address_city=item["address"]["city"],
                profile_first_name=item["profile"]["firstName"],
                profile_last_name=item["profile"]["lastName"],
                company_name=item["company"]["companyName"],
            )
            crud.create_customer(db, customer_data)
    db.close()


if __name__ == "__main__":
    init_data()
