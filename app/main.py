import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from models.users import Users as UserModel
from schemas.users import User
from typing import List
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="PayeTonKawa - API Clients")
Instrumentator().instrument(app).expose(app)
Base.metadata.create_all(bind=engine)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/users")
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(UserModel).all()
    return users

@app.get("/users/{id}")
def get_user_by_id(id:int, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == id).first()
    return user

# Créer un utilisateur
@app.post("/users/", response_model=User)
def create_user(user: User, db: Session = Depends(get_db)):
    db_user = UserModel(
        firstname=user.firstname,
        lastname=user.lastname,
        mail=user.mail,
        id_address=user.id_address
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.put("/user/{id}", response_model=User)
def modify_user(id: int, user:User,db: Session = Depends(get_db)):
    user_to_update=db.query(UserModel).filter(UserModel.id==id).first()
    user_to_update.firstname=user.firstname
    user_to_update.lastname=user.lastname
    user_to_update.mail=user.mail
    user_to_update.id_address=user.id_address

    db.commit()
    return user_to_update

@app.delete("/user/{id}", response_model=User)
def delete_user(id: int, user:User,db: Session = Depends(get_db)):
    user_to_delete=db.query(UserModel).filter(UserModel.id==id).first()
    db.delete(user_to_delete)
    db.commit()
    return user_to_delete