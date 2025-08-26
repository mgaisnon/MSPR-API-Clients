import os
from fastapi import FastAPI, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from prometheus_fastapi_instrumentator import Instrumentator
from dotenv import load_dotenv
from . import crud, models, schemas
from .database import SessionLocal, engine
from .rabbitmq import publish_event

load_dotenv()

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
Instrumentator().instrument(app).expose(app)

API_KEY = os.getenv("API_KEY") 

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")

@app.get("/customers/", response_model=list[schemas.Customer])
def read_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), _ = Depends(verify_api_key)):
    return crud.get_customers(db, skip=skip, limit=limit)

@app.get("/customers/{customer_id}", response_model=schemas.Customer)
def read_customer(customer_id: int, db: Session = Depends(get_db), _ = Depends(verify_api_key)):
    customer = crud.get_customer(db, customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@app.post("/customers/", response_model=schemas.Customer, status_code=status.HTTP_201_CREATED)
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db), _ = Depends(verify_api_key)):
    db_customer = crud.get_customer_by_username(db, username=customer.username)
    if db_customer:
        raise HTTPException(status_code=400, detail="Username already registered")
    new_customer = crud.create_customer(db, customer)
    try:
        event_data = {key: value for key, value in new_customer.__dict__.items() if not key.startswith('_')}
        publish_event("customer_created", event_data)
    except Exception as e:
        pass
    return new_customer

@app.put("/customers/{customer_id}", response_model=schemas.Customer)
def update_customer(customer_id: int, customer: schemas.CustomerCreate, db: Session = Depends(get_db), _ = Depends(verify_api_key)):
    db_customer = crud.get_customer(db, customer_id)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    if customer.username != db_customer.username:
        existing_customer = crud.get_customer_by_username(db, username=customer.username)
        if existing_customer and existing_customer.id != customer_id:
            raise HTTPException(status_code=400, detail="Username already registered")
    
    updated = crud.update_customer(db, customer_id, customer)
    try:
        event_data = {key: value for key, value in updated.__dict__.items() if not key.startswith('_')}
        publish_event("customer_updated", event_data)
    except Exception as e:
        pass
    return updated

@app.delete("/customers/{customer_id}")
def delete_customer(customer_id: int, db: Session = Depends(get_db), _ = Depends(verify_api_key)):
    deleted = crud.delete_customer(db, customer_id)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    try:
        publish_event("customer_deleted", {"id": customer_id})
    except Exception as e:
        pass
    return {"detail": "Customer deleted"}