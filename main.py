from fastapi import FastAPI
from supabase import create_client
from pydantic import BaseModel
from jose import jwt
from passlib.context import CryptContext

app = FastAPI()
supabase = create_client("https://clrvazgwmvmhbjhohszr.supabase.co", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNscnZhemd3bXZtaGJqaG9oc3pyIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDM0ODQ3OCwiZXhwIjoyMDg1OTI0NDc4fQ.s2iBCg513W6h6GX7bL7HYkXdn33i-ZmSrVAX7GzuqyY")

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

SECRET_KEY = "ufbyezhfbrzhbergfeufbrbgfuerbfzebduyaebfyurebfq567545VRFRCC456YU"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password[72])

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def create_token(usr : user):
    tmp = {
        "email": usr.email,
        "type": usr.type
    }
    return jwt.encode(tmp, SECRET_KEY, algorithm=ALGORITHM)


@app.post("/project")
def add(p : project):
    supabase.table("water").insert(p.model_dump()).execute()

@app.post("/signup")
def add(usr : user):
    usr_db = userdb(
        email=usr.email,
        passhash=hash_password(usr.password),
        type=usr.type
        )
    supabase.table("user").insert(usr_db.model_dump()).execute()

@app.get("/login")
def log(usr: user):
    response = supabase.table("user").select("*").eq("email", usr.email).execute()
    data = response.data

    if not data:
        return {"error": "User not found"}

    user_record = data[0]

    if not verify_password(usr.password, user_record["passhash"]):
        return {"error": "Incorrect password"}

    token = jwt.encode(
        {"email": user_record["email"], "type": user_record["type"]},
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {"access_token": token}