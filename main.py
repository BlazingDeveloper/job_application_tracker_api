from dotenv import load_dotenv
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlmodel import Session
from sqlmodel import select
from sqlmodel import SQLModel,Field
from passlib.context import CryptContext
from jose import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

load_dotenv()
SECRET_KEY =os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

#route ->function->return data

app = FastAPI()
@app.get("/")
def read_root():
    return {"Hello": "World"}

# user table->hasing->register->login->protect routes

class User(SQLModel,table=True):
        id:int|None=Field(default=None,primary_key=True)
        email:str
        password:str

class ApplicationCreate(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    company: str
    role: str
    user_id: int | None = None

pwd_context = CryptContext(schemes=["bcrypt"])

from sqlmodel import create_engine
engine=create_engine("sqlite:///database.db")
SQLModel.metadata.create_all(engine)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
    except:
        raise HTTPException(status_code=401, detail="Invalid token")
    with Session(engine) as session:
        statement = select(User).where(User.email == email)
        user = session.exec(statement).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user

@app.post("/register")
def register(user: User):
    hashed_password = pwd_context.hash(user.password)
    user.password = hashed_password
    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

@app.post("/login")
def login(user: User):
    with Session(engine) as session:
        statement = select(User).where(User.email == user.email)
        db_user = session.exec(statement).first()
        if not db_user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        if not pwd_context.verify(user.password, db_user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        token = jwt.encode({"sub": db_user.email}, SECRET_KEY, algorithm=ALGORITHM)
        return {"access_token": token, "token_type": "bearer"}

@app.post("/applications")
def create_application(new_application: ApplicationCreate, current_user: User = Depends(get_current_user)):
    new_application.user_id = current_user.id
    with Session(engine) as session:
        session.add(new_application)
        session.commit()
        session.refresh(new_application)
        return new_application

@app.get("/applications")
def list_applications(current_user: User = Depends(get_current_user)):
    with Session(engine) as session:
        statement = select(ApplicationCreate).where(ApplicationCreate.user_id == current_user.id)
        results = session.exec(statement).all()
        return results

@app.get("/applications/{app_id}")
def get_application(app_id:int,current_user:User=Depends(get_current_user)):
    with Session(engine) as session:
        result=session.get(ApplicationCreate,app_id)
        if result and result.user_id == current_user.id:
            return result
        raise HTTPException(status_code=404,detail="application not found")

@app.delete("/applications/{app_id}")
def delete_app(app_id:int,current_user: User = Depends(get_current_user)):
    with Session(engine) as session:
        result=session.get(ApplicationCreate,app_id)
        if result and result.user_id == current_user.id:
            session.delete(result)
            session.commit()
            return{"message":"deleted"}
        raise HTTPException(status_code=404,detail="application not found")

@app.put("/applications/{app_id}")
def update_app(app_id:int,update:ApplicationCreate,current_user: User = Depends(get_current_user)):
    with Session(engine) as session:
        result=session.get(ApplicationCreate,app_id)
        if result and result.user_id == current_user.id:
            result.company=update.company
            result.role=update.role
            session.add(result)
            session.commit()
            return result
        raise HTTPException(status_code=404,detail="application not found")    

