import os
from fastapi import FastAPI, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from prometheus_fastapi_instrumentator import Instrumentator
from dotenv import load_dotenv
from . import crud, models, schemas
from .database import SessionLocal, engine
from .rabbitmq import publish_event
import logging

logging.basicConfig(level=logging.DEBUG)  # Changé à DEBUG pour plus de détails
logger = logging.getLogger(__name__)

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
    customers = crud.get_customers(db, skip=skip, limit=limit)
    try:
        event_data = [
            {key: value for key, value in customer.__dict__.items() if not key.startswith('_')}
            for customer in customers
        ]
        logger.debug(f"Publication de l'événement customers_listed avec {len(event_data)} clients")
        publish_event("customers_listed", {"customers": event_data})
    except Exception as e:
        logger.error(f"Erreur lors de la publication de l'événement customers_listed: {str(e)}")
    return customers

@app.get("/customers/{customer_id}", response_model=schemas.Customer)
def read_customer(customer_id: int, db: Session = Depends(get_db), _ = Depends(verify_api_key)):
    customer = crud.get_customer(db, customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    try:
        event_data = {key: value for key, value in customer.__dict__.items() if not key.startswith('_')}
        logger.debug(f"Publication de l'événement customer_retrieved pour le client ID {customer_id}")
        publish_event("customer_retrieved", event_data)
    except Exception as e:
        logger.error(f"Erreur lors de la publication de l'événement customer_retrieved: {str(e)}")
    return customer

@app.post("/customers/", response_model=schemas.Customer, status_code=status.HTTP_201_CREATED)
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db), _ = Depends(verify_api_key)):
    db_customer = crud.get_customer_by_username(db, username=customer.username)
    if db_customer:
        raise HTTPException(status_code=400, detail="Username already registered")
    new_customer = crud.create_customer(db, customer)
    try:
        event_data = {key: value for key, value in new_customer.__dict__.items() if not key.startswith('_')}
        logger.debug(f"Publication de l'événement customer_created pour le client {new_customer.username}")
        publish_event("customer_created", event_data)
    except Exception as e:
        logger.error(f"Erreur lors de la publication de l'événement customer_created: {str(e)}")
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
        logger.debug(f"Publication de l'événement customer_updated pour le client ID {customer_id}")
        publish_event("customer_updated", event_data)
    except Exception as e:
        logger.error(f"Erreur lors de la publication de l'événement customer_updated: {str(e)}")
    return updated

@app.delete("/customers/{customer_id}")
def delete_customer(customer_id: int, db: Session = Depends(get_db), _ = Depends(verify_api_key)):
    deleted = crud.delete_customer(db, customer_id)
    if deleted is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    try:
        logger.debug(f"Publication de l'événement customer_deleted pour le client ID {customer_id}")
        publish_event("customer_deleted", {"id": customer_id})
    except Exception as e:
        logger.error(f"Erreur lors de la publication de l'événement customer_deleted: {str(e)}")
    return {"detail": "Customer deleted"}