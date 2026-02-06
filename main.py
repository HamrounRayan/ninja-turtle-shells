from fastapi import FastAPI
from supabase import create_client
from pydantic import BaseModel, EmailStr
import jwt
from pwdlib import PasswordHash
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from app.ai_agent import AiAgent
from typing import Optional, Literal
from typing import List


app = FastAPI()

agent = AiAgent()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
supabase = create_client("https://clrvazgwmvmhbjhohszr.supabase.co", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNscnZhemd3bXZtaGJqaG9oc3pyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDM0ODQ3OCwiZXhwIjoyMDg1OTI0NDc4fQ.s2iBCg513W6h6GX7bL7HYkXdn33i-ZmSrVAX7GzuqyY")
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"

class project(BaseModel):
    name: str
    address: str
    description: str 
    type: str
    skills_required: List[str]

class user(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    field_of_interest: List[str]
    education_level: str = "expert"
    motivation: str
    helpful_links: Optional[str] = None
    type: Literal["student", "teacher", "admin"]

class userdb(BaseModel):
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
    
@app.post("/deleteproject")
def delete(p : project, token: str = Depends(oauth2_scheme)):
    ninja = current_user(token).data
    if ninja["type"] == "admin" :
        supabase.table("projects").delete().eq("name", p.name).execute()
        return {"message": "Project deleted successfully"}
    else :
        return None    
    
@app.get("/")
def home():
    response = supabase.table("projects").select("id", "name").execute()
    projects = response.data
    return {"projects": projects}

@app.get("/project/{project_id}")
def get_project(project_id: int):
    response = supabase.table("projects").select("*").eq("id", project_id).single().execute()
    project = response.data
    return {"project": project}

@app.post("/signup")
def add(usr : user):
    usr.password = hash_password(usr.password)
    supabase.table("user").insert(usr.model_dump()).execute()
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
        "email": user_record["email"],
        "type": user_record["type"]
    }
    token = jwt.encode(tmp ,SECRET_KEY,algorithm=ALGORITHM)

    return {"access_token": token}