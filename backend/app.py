from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel, SecretStr, EmailStr, validator
from fastapi.middleware.cors import CORSMiddleware
import re
import pymysql
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
# from typing import Dict
from dotenv import load_dotenv
import os
import shutil
import uuid
import logging

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
    "database": "job_tracker",
    "charset": "utf8mb4"
}

#local storage for pdf
PDF_DIR = "D:\\job-tracker-resumes"
os.makedirs(PDF_DIR, exist_ok=True)

#database connection
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

# Pydantic model for Signup form 
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
    
#pydantic model for Signup form response
class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str

#pydantic model for Login form
class LoginForm(BaseModel):
    email: EmailStr
    password: SecretStr
    
#pydantic model for Application form
class ApplicationForm(BaseModel):
    name: str
    email: EmailStr 
    mobile: str
    # file: cv file?
    job: str
    
    # @validator("mobile")
    # def validate_mobile(cls, v: str):
    #     if not re.match(r"^\+?\d{9,15}$", v):
    #         raise ValueError("Mobile must be a valid phone number (e.g., +9478709709)")
    #     return v

#pydantic model for Application form response
class ApplicationResponse(BaseModel):
    id: int
    user_id: int
    name: str
    email: EmailStr 
    mobile: str
    cv_path: str
    job: str
    status: str
    
#pydantic model for Application list response
class ApplicationListResponse(BaseModel):
    applications: list[ApplicationResponse]
    
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
###---> (1)handling Signup form 
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

###---> (2)handling Login form --endpoints to ensure the authentication
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
    
###---> (3)handling Application form 
@app.post("/application-submit", response_model=ApplicationResponse)
async def submit_application(
    name: str = Form(...),
    # email: str = Form(...),
    email: EmailStr = Form(...),
    mobile: str = Form(...),
    job: str = Form(...),
    cv: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: pymysql.connections.Connection = Depends(get_db)
    
):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info(f"Received token: {current_user}")
    logger.info(f"Received form data: name={name}, email={email}, mobile={mobile}, job={job}")
    logger.info(f"File: {cv.filename}, Content-Type: {cv.content_type}")

    #to validate the pdf
    if cv.content_type != "application/pdf":
        logger.error("Non-PDF file uploaded")
        raise HTTPException(status_code=400, detail="CV must be a PDF")
    
    #validate form data with pydantic 
    try:
        form_data = ApplicationForm(name=name, email=email, mobile=mobile, job=job)
    except ValueError as e:
        logger.error(f"Form validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    #generate unique filename for CV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    cv_name = f"{timestamp}_{unique_id}.pdf"
    cv_path = os.path.join(PDF_DIR, cv_name)
    
    #save pdf 
    with open(cv_path, "wb") as f:
        shutil.copyfileobj(cv.file, f)
    
    #store in database
    try:
        with db.cursor() as cursor:
            cursor.execute(
                "INSERT INTO applications (user_id, name, email, mobile, cv_path, job, status) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (current_user["user_id"], form_data.name, form_data.email, form_data.mobile, cv_path, form_data.job, "Applied")
            )
            db.commit()
            cursor.execute("SELECT LAST_INSERT_ID()")
            app_id = cursor.fetchone()[0]
            
        return ApplicationResponse(
            id=app_id,
            user_id=current_user["user_id"],
            name=form_data.name,
            email=form_data.email,
            mobile=form_data.mobile,
            cv_path=cv_path,
            job=form_data.job,
            status="Applied"
        )
    except pymysql.MySQLError as e:
        logger.error(f"Database error: {e}")
        # clean up file if database fails
        if os.path.exists(cv_path):
            os.remove(cv_path)
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/applications", response_model=ApplicationListResponse)
async def get_applications(current_user: dict = Depends(get_current_user), db: pymysql.connections.Connection = Depends(get_db)):
    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(
                "SELECT id, user_id, name, email, mobile, cv_path, job, status FROM applications WHERE user_id = %s",
                (current_user["user_id"],)
            )
            applications = cursor.fetchall()
            if not applications:
                raise HTTPException(status_code=404, detail="No applications found")
            return ApplicationListResponse(applications=[ApplicationResponse(**app) for app in applications])
    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
