from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException
from models import User
from sqlalchemy.exc import SQLAlchemyError
from connection import SessionLocal

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)


def signupfunction(form_data, db: Session):
    hashed_pw = hash_password(form_data.password)
    try:
        user = db.query(User).filter(User.email == form_data.email).first()
        if user:
            raise HTTPException(status_code=400, detail="Email already registered")

        new_user = User(
            firstName=form_data.fname,
            lastName=form_data.lname,
            email=form_data.email,
            password=hashed_pw,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {
            "message": "User registered successfully",
            "user": new_user,
            "status_code": 200,
        }
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))
