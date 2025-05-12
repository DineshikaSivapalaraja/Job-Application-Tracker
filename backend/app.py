from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, SecretStr, EmailStr, validator
from fastapi.middleware.cors import CORSMiddleware
import re
import pymysql
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from typing import Dict
from dotenv import load_dotenv
import os

app = FastAPI()

# @app.get("/")
# async def get():
#     return "welcome to the website"

# @app.post("/post")
# async def post():
#     id = 12
#     return id

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  #["*"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#database configuration  -->venv\Scripts\activate-->pip install fastapi uvicorn pymysql  
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "job_tracker"
}

def get_db():
    conn = pymysql.connect(**db_config)
    try:
        yield conn
    finally:
        conn.close()
        
#JWT settings
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")  #secure secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

#password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")        

#OAuth2 scheme for JWT
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# Test the db connection
@app.get("/test-db")
async def test_db(db: pymysql.connections.Connection = Depends(get_db)):
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            return {"message": "Database connection successful", "result": result[0]}
    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

###---> (1)handling signup form functionalities
signup_data = []

# Pydantic model for form data
class UserDataForm(BaseModel):
    name: str
    email: EmailStr #built in Pydantic type for email validation
    password: SecretStr
    cpassword: SecretStr
    
    @validator("password")
    def validate_password(cls, v: SecretStr):
        password = v.get_secret_value()
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.match(r"^(?=.*[a-zA-Z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]+$", password):
            raise ValueError(
                "Password must contain at least one letter, one number, and one symbol (@$!%*?&)"
            )
        return v

    @validator("cpassword")
    def passwords_match(cls, v: SecretStr, values):
        if "password" in values and v.get_secret_value() != values["password"].get_secret_value():
            raise ValueError("Passwords do not match")
        return v
    
class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str
    
class LoginForm(BaseModel):
    email: EmailStr
    password: SecretStr

#JWT authentication
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        role: str = payload.get("role")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"user_id": user_id, "role": role}

# endpoints to ensure the authentication
@app.post("/signup", response_model=UserResponse)
async def signup(data: UserDataForm, db: pymysql.connections.Connection = Depends(get_db)):
    try:
        with db.cursor() as cursor:
            hashed_password = pwd_context.hash(data.password.get_secret_value())
            cursor.execute(
                "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
                (data.name, data.email, hashed_password, "applicant")
            )
            db.commit()
            cursor.execute("SELECT LAST_INSERT_ID()")
            user_id = cursor.fetchone()[0]
        return {"id": user_id, "name": data.name, "email": data.email, "role": "applicant"}
    except pymysql.err.IntegrityError:
        raise HTTPException(status_code=400, detail="Email already exists")
    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post("/login")
async def login(data: LoginForm, db: pymysql.connections.Connection = Depends(get_db)):
    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT id, name, email, password, role FROM users WHERE email = %s", (data.email,))
            user = cursor.fetchone()
            if not user or not pwd_context.verify(data.password.get_secret_value(), user["password"]):
                raise HTTPException(status_code=401, detail="Invalid credentials")
            access_token = create_access_token({"sub": user["id"], "role": user["role"]})
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": {"id": user["id"], "name": user["name"], "email": user["email"], "role": user["role"]}
            }
    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
# POST endpoint to receive signup form data
@app.post("/submit")
async def submit_form(data: UserDataForm):
    try:
        signup_data.append(data)
        return {"message": "Data received", "data": data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    # signup_data.append(data)
    # return {"message": "Data received", "data": data}

# GET endpoint to retrieve all signup form data
@app.get("/data")
async def get_data():
    return signup_data

###--> (2) application form data handling
application_data = []

# Pydantic model for form data
class ApplicationForm(BaseModel):
    name: str
    email: EmailStr #built in Pydantic type for email validation
    mobile: int
    # file: cv file?
    job: str
    
# POST endpoint to receive form data
@app.post("/application-submit")
async def submit_form(data: ApplicationForm):
    try:
        application_data.append(data)
        return {"message": "Data received", "data": data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    # signup_data.append(data)
    # return {"message": "Data received", "data": data}

# GET endpoint to retrieve all form data
@app.get("/application-data")
async def get_data():
    return application_data

