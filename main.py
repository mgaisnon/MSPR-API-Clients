from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models.users import Users as UserModel
from schemas.users import User
from typing import List

Base.metadata.create_all(bind=engine)

app = FastAPI()

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

@app.get("/users")
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(UserModel).all()
    return users
