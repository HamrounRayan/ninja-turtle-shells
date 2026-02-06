from fastapi import FastAPI
from supabase import create_client
from pydantic import BaseModel
import jwt
from pwdlib import PasswordHash
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated


app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
supabase = create_client("https://clrvazgwmvmhbjhohszr.supabase.co", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNscnZhemd3bXZtaGJqaG9oc3pyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDM0ODQ3OCwiZXhwIjoyMDg1OTI0NDc4fQ.s2iBCg513W6h6GX7bL7HYkXdn33i-ZmSrVAX7GzuqyY")
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"

class project(BaseModel):
    address: str
    description: str 

class user(BaseModel):
    email: str
    password: str
    type:str

class userdb(BaseModel):
    email: str
    passhash: str
    type: str

def hash_password(password):
    return PasswordHash.recommended().hash(password)

def verify_password(plain_password, hashed_password):
    return PasswordHash.recommended().verify(plain_password, hashed_password)

def create_token(usr : user):
    tmp = {
        "email": usr.email,
        "type": usr.type
    }
    return jwt.encode(tmp, SECRET_KEY, algorithm=ALGORITHM)

def current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    tmp = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username = tmp.get("email")
    if not username:
        return None
    
    return supabase.table("user").select("*").eq("email", username).single().execute()



@app.post("/newproject")
def add(p : project, token: str = Depends(oauth2_scheme)):
    ninja = current_user(token).data
    if ninja["type"] == "admin" :
        supabase.table("projects").insert(p.model_dump()).execute()
        return {"message": "Project created successfully"}
    else :
        return None    

@app.post("/signup")
def add(usr : user):
    usr_db = userdb(
        email=usr.email,
        passhash=hash_password(usr.password),
        type=usr.type
        )
    supabase.table("user").insert(usr_db.model_dump()).execute()

@app.post("/login")
def log(usr: user):
    response = supabase.table("user").select("*").eq("email", usr.email).single().execute()
    user_record = response.data

    if not user_record:
        return {"error": "User not found"}
    
    if not verify_password(usr.password, user_record["passhash"]):
        return {"error": "Incorrect password"}
    
    tmp = {
        "email": user_record["email"],
        "type": user_record["type"]
    }
    token = jwt.encode(tmp ,SECRET_KEY,algorithm=ALGORITHM)

    return {"access_token": token}