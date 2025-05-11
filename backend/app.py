from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, SecretStr, EmailStr, validator
from fastapi.middleware.cors import CORSMiddleware
import re
import pymysql

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
class DataForm(BaseModel):
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
    
# POST endpoint to receive signup form data
@app.post("/submit")
async def submit_form(data: DataForm):
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

