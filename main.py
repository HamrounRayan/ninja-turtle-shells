from fastapi import FastAPI, HTTPException
from supabase import create_client
from pydantic import BaseModel, EmailStr
import jwt
from pwdlib import PasswordHash
from typing import Optional, Literal


app = FastAPI()
supabase = create_client("https://clrvazgwmvmhbjhohszr.supabase.co", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNscnZhemd3bXZtaGJqaG9oc3pyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDM0ODQ3OCwiZXhwIjoyMDg1OTI0NDc4fQ.s2iBCg513W6h6GX7bL7HYkXdn33i-ZmSrVAX7GzuqyY")
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"

class project(BaseModel):
    address: str
    description: str 

class user(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    field_of_interest: str
    education_level: str = "expert"
    motivation: str
    helpful_links: Optional[str] = None
    type: Literal["student", "teacher", "admin"]

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


@app.post("/newproject")
def add(p : project):
    supabase.table("projects").insert(p.model_dump()).execute()

@app.post("/signup")
def add(usr : user):
    usr_db = user(
        full_name= usr.full_name,
        email= usr.email,
        password= hash_password(usr.password),
        field_of_interest= usr.field_of_interest,
        education_level = usr.education_level,
        motivation =  usr.motivation,
        helpful_links =  usr.helpful_links,
        type = usr.type
        )
    supabase.table("user").insert(usr_db.model_dump()).execute()
    tmp = {
        "email": usr.email,
        "type": usr.type
    }
    token = jwt.encode(tmp ,SECRET_KEY,algorithm=ALGORITHM)

    return {"access_token": token}


@app.post("/login")
def log(usr: user):
    response = supabase.table("user").select("*").eq("email", usr.email).single().execute()
    user_record = response.data
    
    if not user_record:
        return {"error": "User not found"}
    
    if not verify_password(usr.password, user_record["passhash"]):
        return {"error": "Incorrect password"}

    tmp = {
        "email": usr.email,
        "type": usr.type
    }
    token = jwt.encode(tmp ,SECRET_KEY,algorithm=ALGORITHM)

    return {"access_token": token}

@app.get("/getAllUsers")
def all_users():
    response = supabase.table("user").select("*").execute()
    return{"users":response}



@app.get("/getUser")
def get_user(email: EmailStr):
    print(email)
    response = (
        supabase.table("user").select("*").eq("email", email).single().execute()
    )
    print(response)
    if not response.data:
        raise HTTPException(status_code=404, detail="User not found")

    return response.data

@app.delete("/deleteUser")
def get_user(email: EmailStr):
    print(email)
    response = (
        supabase.table("user").delete().eq("email", email).execute()
    )
    print(response)
    if not response.data:
        raise HTTPException(status_code=404, detail="User not found")

    return None

