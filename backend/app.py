from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel, SecretStr, EmailStr, validator
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
import re
import pymysql
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import shutil
import uuid
import logging

app = FastAPI()

# In-memory token blacklist
blacklisted_tokens = set()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  #["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "job_tracker",
    "charset": "utf8mb4"
}

# Local storage for PDFs
PDF_DIR = "D:\\job-tracker-resumes"
os.makedirs(PDF_DIR, exist_ok=True)

# Database connection
def get_db():
    conn = pymysql.connect(**db_config)
    try:
        yield conn
    finally:
        conn.close()

# JWT settings
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not define in the .env file.")
ADMIN_CODE = os.getenv("ADMIN_CODE")
if not ADMIN_CODE:
    raise ValueError("ADMIN_CODE environment variable is not define in the .env file.")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for JWT
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# to extract original email
def extract_original_email(stored_email: str) -> str:
    local, domain = stored_email.rsplit('@', 1)
    if '+' in local:
        local = local.split('+')[0]
    return f"{local}@{domain}"

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

# Pydantic models
# Pydantic model for Signup form 
class UserDataForm(BaseModel):
    name: str
    email: EmailStr
    password: SecretStr
    cpassword: SecretStr
    
    @validator("password")
    def validate_password(cls, v: SecretStr):
        password = v.get_secret_value()
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.match(r"^(?=.*[a-zA-Z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]+$", password):
            raise ValueError(
                "Password must contain at least one letter, one number, and one symbol (@$!%*?&#)"
            )
        return v

    @validator("cpassword")
    def passwords_match(cls, v: SecretStr, values):
        if "password" in values and v.get_secret_value() != values["password"].get_secret_value():
            raise ValueError("Passwords do not match")
        return v

#pydantic model for admin signup form
class AdminSignupForm(UserDataForm):
    admin_code: str

#pydantic model for Signup form response
class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str

#pydantic model for Profile update form
class ProfileUpdateForm(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    password: SecretStr | None = None
    
    @validator("password", always=True)
    def validate_password(cls, v: SecretStr | None, values):
        if v is None:
            return v
        password = v.get_secret_value()
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.match(r"^(?=.*[a-zA-Z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]+$", password):
            raise ValueError("Password must contain at least one letter, one number, and one symbol (@$!%*?&#)")
        return v

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
    
    @validator("mobile")
    def validate_mobile(cls, v: str):
        if not re.match(r"^\+?\d{9,15}$", v):
            raise ValueError("Mobile must be a valid phone number (e.g., +9478709709)")
        return v

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

#pydantic model for application status
class UpdateApplicationStatus(BaseModel):
    status: str
    
    @validator("status")
    def validate_status(cls, v:str):
        valid_statuses = {"Applied", "Viewed", "Resume Downloaded","Interview Scheduled", "Rejected", "Offered"}
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of {valid_statuses}")
        return v

#pydantic model for Application edit form
class ApplicationEditForm(BaseModel):
    name: str
    email: EmailStr
    mobile: str
    job: str
    
    @validator("mobile")
    def validate_mobile(cls, v: str):
        if not re.match(r"^\+?\d{9,15}$", v):
            raise ValueError("Mobile must be a valid phone number (e.g., +9478709709)")
        return v

# JWT authentication
def create_access_token(user_id: int, role: str):
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": str(user_id),  
        "role": role,
        "exp": expire
    }
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("auth")
    
    if token in blacklisted_tokens:
        logger.warning("Token is blacklisted")
        raise HTTPException(status_code=401, detail="Invalid token")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        role = payload.get("role")

        if user_id is None or role is None:
            logger.error("Missing user_id or role in token")
            raise HTTPException(status_code=401, detail="Invalid token")

        logger.info(f"Token valid for user_id={user_id}, role={role}")
        return {"user_id": int(user_id), "role": role}

    except jwt.ExpiredSignatureError:
        logger.error("Token has expired")
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid token: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_admin(token: str = Depends(oauth2_scheme)):
    user = await get_current_user(token)
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

# api endpoints 
###---> (1)handling Signup form  --> working
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

###---> (5)handling Admin Signup --> working
@app.post("/admin-signup", response_model=UserResponse)
async def admin_signup(data: AdminSignupForm, db: pymysql.connections.Connection = Depends(get_db)):
    if data.admin_code != ADMIN_CODE:
        raise HTTPException(status_code=403, detail="Invalid admin code")
    
    try:
        with db.cursor() as cursor:
            hashed_password = pwd_context.hash(data.password.get_secret_value())
            cursor.execute(
                "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
                (data.name, data.email, hashed_password, "admin")
            )
            db.commit()
            cursor.execute("SELECT LAST_INSERT_ID()")
            user_id = cursor.fetchone()[0]
        return {"id": user_id, "name": data.name, "email": data.email, "role": "admin"}
    except pymysql.err.IntegrityError:
        raise HTTPException(status_code=400, detail="Email already exists")
    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

###---> (2)handling Login form --endpoints to ensure the authentication--> working for admin/applicant  
@app.post("/login")
async def login(data: LoginForm, db: pymysql.connections.Connection = Depends(get_db)):
    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT id, name, email, password, role FROM users WHERE email = %s", (data.email,))
            user = cursor.fetchone()

            if not user or not pwd_context.verify(data.password.get_secret_value(), user["password"]):
                raise HTTPException(status_code=401, detail="Invalid credentials")

            access_token = create_access_token(user_id=user["id"], role=user["role"])

            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "id": user["id"],
                    "name": user["name"],  
                    "email": user["email"],
                    "role": user["role"]
                }
            }
    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

##added
@app.options("/application-submit")
async def options_application_submit():
    return Response(status_code=200, headers={
        # "Access-Control-Allow-Origin": "http://localhost:5173",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST",
        "Access-Control-Allow-Headers": "Authorization, Content-Type"
    })

###---> (3)handling Application form -->working
@app.post("/application-submit", response_model=ApplicationResponse)
async def submit_application(
    name: str = Form(...),
    email: EmailStr = Form(...),
    mobile: str = Form(...),
    job: str = Form(...),
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: pymysql.connections.Connection = Depends(get_db)
):
    logger.info(f"Received submission: name={name}, email={email}, mobile={mobile}, job={job}, file={file.filename}")

    # verify email matches profile
    try:
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT email FROM users WHERE id = %s",
                (current_user["user_id"],)
            )
            user = cursor.fetchone()
            if not user or user[0] != email:
                logger.error(f"Submitted email {email} does not match user profile email")
                raise HTTPException(status_code=400, detail="Submitted email must match your profile email")
    except pymysql.MySQLError as e:
        logger.error(f"Database error checking user email: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    try:
        form_data = ApplicationForm(name=name, email=email, mobile=mobile, job=job)
    except ValueError as e:
        logger.error(f"Form validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    if file.content_type != "application/pdf":
        logger.error("Non-PDF file uploaded")
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # check for existing application with same email and job
    try:
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM applications WHERE email = %s AND job = %s",
                (email, job)
            )
            if cursor.fetchone():
                logger.warning(f"Duplicate application for email={email}, job={job}")
                raise HTTPException(status_code=400, detail="You have already applied for this job with this email.")
    except pymysql.MySQLError as e:
        logger.error(f"Database error checking duplicate: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    unique_filename = f"{uuid.uuid4()}.pdf"
    file_path = os.path.join(PDF_DIR, unique_filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logger.error(f"File save error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save CV: {str(e)}")

    try:
        with db.cursor() as cursor:
            cursor.execute(
                "INSERT INTO applications (user_id, name, email, mobile, cv_path, job, status) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (current_user["user_id"], form_data.name, form_data.email, form_data.mobile, file_path, form_data.job, "Applied")
            )
            db.commit()
            cursor.execute("SELECT LAST_INSERT_ID()")
            app_id = cursor.fetchone()[0]

            cursor.execute(
                "SELECT id, user_id, name, email, mobile, cv_path, job, status FROM applications WHERE id = %s",
                (app_id,)
            )
            app = cursor.fetchone()
            return ApplicationResponse(
                id=app[0],
                user_id=app[1],
                name=app[2],
                email=app[3],  # use original/registered email directly
                mobile=app[4],
                cv_path=app[5],
                job=app[6],
                status=app[7]
            )
    except pymysql.MySQLError as e:
        logger.error(f"Database error during insertion: {e}")
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

###---> (4)listing the applications(applicant can view their own applications) --> working
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
            # convert stored email to original email
            for app in applications:
                app["email"] = extract_original_email(app["email"])
            return ApplicationListResponse(applications=[ApplicationResponse(**app) for app in applications])
    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

###---> (7)admin view of all applications --> working with admin access
@app.get("/admin/applications", response_model=ApplicationListResponse)
async def get_all_applications(current_user: dict = Depends(get_current_admin), db: pymysql.connections.Connection = Depends(get_db)):
    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(
                "SELECT id, user_id, name, email, mobile, cv_path, job, status FROM applications"
            )
            applications = cursor.fetchall()
            if not applications:
                raise HTTPException(status_code=404, detail="No applications found")
            # convert stored email to original email
            for app in applications:
                app["email"] = extract_original_email(app["email"])
            return ApplicationListResponse(applications=[ApplicationResponse(**app) for app in applications])
    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

###---> (6)admin updates applications status --> working with admin access 
@app.put("/applications/{app_id}", response_model=ApplicationResponse)
async def update_application_status(
    app_id: int,
    update_data: UpdateApplicationStatus,
    current_user: dict = Depends(get_current_admin),
    db: pymysql.connections.Connection = Depends(get_db)
):
    try:
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT user_id, status FROM applications WHERE id = %s",
                (app_id,)
            )
            application = cursor.fetchone()
            if not application:
                raise HTTPException(status_code=404, detail="Application not found")

            cursor.execute(
                "UPDATE applications SET status = %s WHERE id = %s",
                (update_data.status, app_id)
            )
            if cursor.rowcount == 0:
                raise HTTPException(status_code=500, detail="Failed to update application")
            db.commit()

            cursor.execute(
                "SELECT id, user_id, name, email, mobile, cv_path, job, status FROM applications WHERE id = %s",
                (app_id,)
            )
            updated_app = cursor.fetchone()
            return ApplicationResponse(
                id=updated_app[0],
                user_id=updated_app[1],
                name=updated_app[2],
                email=extract_original_email(updated_app[3]),
                mobile=updated_app[4],
                cv_path=updated_app[5],
                job=updated_app[6],
                status=updated_app[7]
            )
    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

###---> (10) Applicant can edit the application  --> working
@app.put("/edit-applications/{app_id}", response_model=ApplicationResponse)
async def edit_application(
    app_id: int,
    name: str = Form(...),
    email: EmailStr = Form(...),
    mobile: str = Form(...),
    job: str = Form(...),
    file: UploadFile = File(...),  # CV is required
    current_user: dict = Depends(get_current_user),
    db: pymysql.connections.Connection = Depends(get_db)
):
    logger.info(f"Editing application {app_id}: name={name}, email={email}, mobile={mobile}, job={job}, file={file.filename}")
    try:
        form_data = ApplicationEditForm(name=name, email=email, mobile=mobile, job=job)
    except ValueError as e:
        logger.error(f"Form validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    if file.content_type != "application/pdf":
        logger.error("Non-PDF file uploaded")
        raise HTTPException(status_code=400, detail="CV must be a PDF")

    try:
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT user_id, status, cv_path, email FROM applications WHERE id = %s",
                (app_id,)
            )
            application = cursor.fetchone()
            if not application:
                logger.error(f"Application {app_id} not found")
                raise HTTPException(status_code=404, detail="Application not found")
            if current_user["user_id"] != application[0]:
                logger.error(f"User {current_user['user_id']} not authorized to edit application {app_id}")
                raise HTTPException(status_code=403, detail="Not authorized to edit this application")
            if application[1] != "Applied":
                logger.error(f"Application {app_id} status is {application[1]}, cannot edit")
                raise HTTPException(status_code=400, detail="Can only edit applications with status 'Applied'")

            # check for duplicate application with same email and job (excluding current app)
            cursor.execute(
                "SELECT id FROM applications WHERE email LIKE %s AND job = %s AND id != %s",
                (f"{email.split('@')[0]}%@%", job, app_id)
            )
            if cursor.fetchone():
                logger.warning(f"Duplicate application for email={email}, job={job}")
                raise HTTPException(status_code=400, detail="You have already applied for this job with this email.")

            # reuse email from existing application
            stored_email = application[3]  # keep the same email 
            logger.info(f"Reusing email {stored_email} for application {app_id}")

            # Delete the old CV file
            old_cv_path = application[2]
            if os.path.exists(old_cv_path):
                os.remove(old_cv_path)

            # Save the new CV
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            cv_name = f"{timestamp}_{unique_id}.pdf"
            new_cv_path = os.path.join(PDF_DIR, cv_name)
            try:
                with open(new_cv_path, "wb") as f:
                    shutil.copyfileobj(file.file, f)
            except Exception as e:
                logger.error(f"File save error: {e}")
                raise HTTPException(status_code=500, detail=f"Failed to save CV: {str(e)}")

            cursor.execute(
                "UPDATE applications SET name = %s, email = %s, mobile = %s, job = %s, cv_path = %s WHERE id = %s",
                (form_data.name, stored_email, form_data.mobile, form_data.job, new_cv_path, app_id)
            )
            if cursor.rowcount == 0:
                logger.error(f"Failed to update application {app_id}")
                raise HTTPException(status_code=500, detail="Failed to update application")
            db.commit()

            cursor.execute(
                "SELECT id, user_id, name, email, mobile, cv_path, job, status FROM applications WHERE id = %s",
                (app_id,)
            )
            updated_app = cursor.fetchone()
            return ApplicationResponse(
                id=updated_app[0],
                user_id=updated_app[1],
                name=updated_app[2],
                email=extract_original_email(updated_app[3]),
                mobile=updated_app[4],
                cv_path=updated_app[5],
                job=updated_app[6],
                status=updated_app[7]
            )
    except pymysql.MySQLError as e:
        logger.error(f"Database error: {e}")
        # clean up new CV file if database update fails
        if 'new_cv_path' in locals() and os.path.exists(new_cv_path):
            os.remove(new_cv_path)
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except OSError as e:
        logger.error(f"File handling error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to handle CV file: {str(e)}")

###---> (8)delete application --> working with admin access
@app.delete("/applications/{app_id}")
async def delete_application(
    app_id: int,
    current_user: dict = Depends(get_current_user),
    db: pymysql.connections.Connection = Depends(get_db)   
):
    try:
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT user_id, cv_path FROM applications WHERE id = %s",
                (app_id,)
            )
            application = cursor.fetchone()
            if not application:
                raise HTTPException(status_code=404, detail="Application not found")

            # check whether admin use this function
            if current_user["role"] != "admin" and current_user["user_id"] != application[0]:
                raise HTTPException(status_code=403, detail="Not authorized to delete this application")

            # delete the CV file
            cv_path = application[1]
            if os.path.exists(cv_path):
                os.remove(cv_path)
            
            # delete the application from the database
            cursor.execute(
                "DELETE FROM applications WHERE id = %s",
                (app_id,)
            )
            db.commit()

            return {"message": "Application deleted successfully"}
    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete CV file: {str(e)}")

###---> (9) Download CV--> working with admin access
@app.get("/applications/{app_id}/cv")
async def download_cv(
    app_id: int,
    current_user: dict = Depends(get_current_admin),
    db: pymysql.connections.Connection = Depends(get_db)
):
    try:
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT cv_path, status FROM applications WHERE id = %s",
                (app_id,)
            )
            application = cursor.fetchone()
            if not application:
                raise HTTPException(status_code=404, detail="Application not found")

            cv_path = application[0]
            if not os.path.exists(cv_path):
                raise HTTPException(status_code=404, detail="CV file not found")

            if application[1] != "Resume Downloaded":
                cursor.execute(
                    "UPDATE applications SET status = %s WHERE id = %s",
                    ("Resume Downloaded", app_id)
                )
                db.commit()

            return FileResponse(
                path=cv_path,
                filename=os.path.basename(cv_path),
                media_type="application/pdf"
            )
    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Failed to access CV file: {str(e)}")

###---> (11) View Profile --> working
@app.get("/profile", response_model=UserResponse)
async def get_profile(current_user: dict = Depends(get_current_user), db: pymysql.connections.Connection = Depends(get_db)):
    try:
        with db.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(
                "SELECT id, name, email, role FROM users WHERE id = %s",
                (current_user["user_id"],)
            )
            user = cursor.fetchone()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            cursor.execute(
                "SELECT mobile, job, cv_path FROM applications WHERE user_id = %s ORDER BY id DESC LIMIT 1",
                (current_user["user_id"],)
            )
            app = cursor.fetchone()
            if app:
                user["mobile"] = app["mobile"]
                user["job"] = app["job"]
                user["cv"] = app["cv_path"]
            else:
                user["mobile"] = ""
                user["job"] = ""
                user["cv"] = ""

            return user
    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

###---> (12) Update Profile--> working 
@app.put("/profile", response_model=UserResponse)
async def update_profile(
    update_data: ProfileUpdateForm,
    current_user: dict = Depends(get_current_user),
    db: pymysql.connections.Connection = Depends(get_db)
):
    try:
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT name, email, password FROM users WHERE id = %s",
                (current_user["user_id"],)
            )
            user = cursor.fetchone()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            new_name = update_data.name if update_data.name is not None else user[0]
            new_email = update_data.email if update_data.email is not None else user[1]
            new_password = pwd_context.hash(update_data.password.get_secret_value()) if update_data.password else user[2]

            cursor.execute(
                "UPDATE users SET name = %s, email = %s, password = %s WHERE id = %s",
                (new_name, new_email, new_password, current_user["user_id"])
            )
            db.commit()

            cursor.execute(
                "SELECT id, name, email, role FROM users WHERE id = %s",
                (current_user["user_id"],)
            )
            updated_user = cursor.fetchone()
            return UserResponse(
                id=updated_user[0],
                name=updated_user[1],
                email=updated_user[2],
                role=updated_user[3]
            )
    except pymysql.err.IntegrityError:
        raise HTTPException(status_code=400, detail="Email already exists")
    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

###---> (13) Logout --> working
@app.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    blacklisted_tokens.add(token)
    return JSONResponse(status_code=200, content={"message": "Successfully logged out"})

