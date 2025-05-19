# from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
# from pydantic import BaseModel, SecretStr, EmailStr, validator
# from fastapi.responses import FileResponse, JSONResponse
# from fastapi.middleware.cors import CORSMiddleware
# import re
# import pymysql
# from fastapi.security import OAuth2PasswordBearer
# from passlib.context import CryptContext
# import jwt
# from datetime import datetime, timedelta
# from dotenv import load_dotenv
# import os
# import shutil
# import uuid
# import logging

# app = FastAPI()

# # In-memory token blacklist
# blacklisted_tokens = set()

# # @app.get("/")
# # async def get():
# #     return "welcome to the website"

# # @app.post("/post")
# # async def post():
# #     id = 12
# #     return id

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  #["http://localhost:5173"]
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# #database configuration   
# db_config = {
#     "host": "localhost",
#     "user": "root",
#     "password": "",
#     "database": "job_tracker",
#     "charset": "utf8mb4"
# }

# #local storage for pdf
# PDF_DIR = "D:\\job-tracker-resumes"
# os.makedirs(PDF_DIR, exist_ok=True)

# #database connection
# def get_db():
#     conn = pymysql.connect(**db_config)
#     try:
#         yield conn
#     finally:
#         conn.close()
        
# #JWT settings
# load_dotenv()
# SECRET_KEY = os.getenv("SECRET_KEY")  #secure secret key
# if not SECRET_KEY:
#     raise ValueError("SECRET_KEY environment variable is not define in the .env file.")
# ADMIN_CODE = os.getenv("ADMIN_CODE")
# if not ADMIN_CODE:
#     raise ValueError("ADMIN_CODE environment variable is not define in the .env file.")
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30

# #password hashing
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")        

# #OAuth2 scheme for JWT
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# # Test the db connection
# @app.get("/test-db")
# async def test_db(db: pymysql.connections.Connection = Depends(get_db)):
#     try:
#         with db.cursor() as cursor:
#             cursor.execute("SELECT 1")
#             result = cursor.fetchone()
#             return {"message": "Database connection successful", "result": result[0]}
#     except pymysql.MySQLError as e:
#         raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

# # Pydantic model for Signup form 
# class UserDataForm(BaseModel):
#     name: str
#     email: EmailStr #built in Pydantic type for email validation
#     password: SecretStr
#     cpassword: SecretStr
    
#     @validator("password")
#     def validate_password(cls, v: SecretStr):
#         password = v.get_secret_value()
#         if len(password) < 8:
#             raise ValueError("Password must be at least 8 characters long")
#         if not re.match(r"^(?=.*[a-zA-Z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]+$", password):
#             raise ValueError(
#                 "Password must contain at least one letter, one number, and one symbol (@$!%*?&)"
#             )
#         return v

#     @validator("cpassword")
#     def passwords_match(cls, v: SecretStr, values):
#         if "password" in values and v.get_secret_value() != values["password"].get_secret_value():
#             raise ValueError("Passwords do not match")
#         return v
    
# #pydantic model for admin signup form
# class AdminSignupForm(UserDataForm):
#     admin_code: str

# #pydantic model for Signup form response
# class UserResponse(BaseModel):
#     id: int
#     name: str
#     email: EmailStr
#     role: str

# #pydantic model for Profile update form
# class ProfileUpdateForm(BaseModel):
#     name: str | None = None
#     email: EmailStr | None = None
#     password: SecretStr | None = None
#     cpassword: SecretStr | None = None
    
#     @validator("password", always=True)
#     def validate_password(cls, v: SecretStr | None, values):
#         if v is None:
#             return v
#         password = v.get_secret_value()
#         if len(password) < 8:
#             raise ValueError("Password must be at least 8 characters long")
#         if not re.match(r"^(?=.*[a-zA-Z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]+$", password):
#             raise ValueError("Password must contain at least one letter, one number, and one symbol (@$!%*?&)")
#         return v

#     @validator("cpassword", always=True)
#     def passwords_match(cls, v: SecretStr | None, values):
#         if "password" in values and values["password"] is not None:
#             if v is None or v.get_secret_value() != values["password"].get_secret_value():
#                 raise ValueError("Passwords do not match")
#         return v
    
# #pydantic model for Login form
# class LoginForm(BaseModel):
#     email: EmailStr
#     password: SecretStr
    
# #pydantic model for Application form
# class ApplicationForm(BaseModel):
#     name: str
#     email: EmailStr 
#     mobile: str
#     # file: cv file?
#     job: str
    
#     @validator("mobile")
#     def validate_mobile(cls, v: str):
#         if not re.match(r"^\+?\d{9,15}$", v):
#             raise ValueError("Mobile must be a valid phone number (e.g., +9478709709)")
#         return v

# #pydantic model for Application form response
# class ApplicationResponse(BaseModel):
#     id: int
#     user_id: int
#     name: str
#     email: EmailStr 
#     mobile: str
#     cv_path: str
#     job: str
#     status: str
    
# #pydantic model for Application list response
# class ApplicationListResponse(BaseModel):
#     applications: list[ApplicationResponse]
    
# #pydantic model for application status
# class UpdateApplicationStatus(BaseModel):
#     status: str
    
#     @validator("status")
#     def validate_status(cls, v:str):
#         valid_statuses = {"Applied", "Viewed", "Resume Downloaded","Interview Scheduled", "Rejected", "Offered"}
#         if v not in valid_statuses:
#             raise ValueError(f"Status must be one of {valid_statuses}")
#         return v
    
# #pydantic model for Application edit form
# class ApplicationEditForm(BaseModel):
#     name: str
#     email: EmailStr
#     mobile: str
#     job: str
    
#     @validator("mobile")
#     def validate_mobile(cls, v: str):
#         if not re.match(r"^\+?\d{9,15}$", v):
#             raise ValueError("Mobile must be a valid phone number (e.g., +9478709709)")
#         return v

# #JWT authentication
# def create_access_token(data: dict):
#     to_encode = data.copy()
#     expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt

# # async def get_current_user(token: str = Depends(oauth2_scheme)):
# #     try:
# #         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
# #         user_id: int = payload.get("sub")
# #         role: str = payload.get("role")
# #         if user_id is None:
# #             raise HTTPException(status_code=401, detail="Invalid token")
# #     except jwt.PyJWTError:
# #         raise HTTPException(status_code=401, detail="Invalid token")
# #     return {"user_id": user_id, "role": role}


# # async def get_current_user(token: str = Depends(oauth2_scheme)):
# #     if token in blacklisted_tokens:
# #         raise HTTPException(status_code=401, detail="Invalid token")
# #     try:
# #         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
# #         user_id: int = payload.get("sub")
# #         role: str = payload.get("role")
# #         if user_id is None:
# #             raise HTTPException(status_code=401, detail="Invalid token")
# #     except jwt.PyJWTError:
# #         raise HTTPException(status_code=401, detail="Invalid token")
# #     return {"user_id": user_id, "role": role}

# # import logging

# async def get_current_user(token: str = Depends(oauth2_scheme)):
#     logging.basicConfig(level=logging.INFO)
#     logger = logging.getLogger(__name__)
#     if token in blacklisted_tokens:
#         logger.error("Token is blacklisted")
#         raise HTTPException(status_code=401, detail="Invalid token")
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         user_id: int = payload.get("sub")
#         role: str = payload.get("role")
#         if user_id is None:
#             logger.error("No user_id in token payload")
#             raise HTTPException(status_code=401, detail="Invalid token")
#         logger.info(f"Token validated for user_id: {user_id}")
#     except jwt.ExpiredSignatureError:
#         logger.error("Token has expired")
#         raise HTTPException(status_code=401, detail="Invalid token")
#     except jwt.InvalidTokenError as e:
#         logger.error(f"Invalid token error: {str(e)}")
#         raise HTTPException(status_code=401, detail="Invalid token")
#     return {"user_id": user_id, "role": role}

# async def get_current_admin(token: str = Depends(oauth2_scheme)):
#     user = await get_current_user(token)
#     if user["role"] != "admin":
#         raise HTTPException(status_code=403, detail="Admin access required")
#     return user

# # endpoints to ensure the authentication
# ###---> (1)handling Signup form 
# @app.post("/signup", response_model=UserResponse)
# async def signup(data: UserDataForm, db: pymysql.connections.Connection = Depends(get_db)):
#     try:
#         with db.cursor() as cursor:
#             hashed_password = pwd_context.hash(data.password.get_secret_value())
#             cursor.execute(
#                 "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
#                 (data.name, data.email, hashed_password, "applicant")
#             )
#             db.commit()
#             cursor.execute("SELECT LAST_INSERT_ID()")
#             user_id = cursor.fetchone()[0]
#         return {"id": user_id, "name": data.name, "email": data.email, "role": "applicant"}
#     except pymysql.err.IntegrityError:
#         raise HTTPException(status_code=400, detail="Email already exists")
#     except pymysql.MySQLError as e:
#         raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# ###---> (6)handling Admin Signup
# # @app.post("/admin-signup", response_model=UserResponse)
# # async def admin_signup(data: AdminSignupForm, db: pymysql.connections.Connection = Depends(get_db)):
# #     if data.admin_code != ADMIN_CODE:
# #         raise HTTPException(status_code=403, detail="Invalid admin code")
    
# #     try:
# #         with db.cursor() as cursor:
# #             hashed_password = pwd_context.hash(data.password.get_secret_value())
# #             cursor.execute(
# #                 "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)",
# #                 (data.name, data.email, hashed_password, "admin")
# #             )
# #             db.commit()
# #             cursor.execute("SELECT LAST_INSERT_ID()")
# #             user_id = cursor.fetchone()[0]
# #         return {"id": user_id, "name": data.name, "email": data.email, "role": "admin"}
# #     except pymysql.err.IntegrityError:
# #         raise HTTPException(status_code=400, detail="Email already exists")
# #     except pymysql.MySQLError as e:
# #         raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
# ###---> (2)handling Login form --endpoints to ensure the authentication
# @app.post("/login")
# async def login(data: LoginForm, db: pymysql.connections.Connection = Depends(get_db)):
#     try:
#         with db.cursor(pymysql.cursors.DictCursor) as cursor:
#             cursor.execute("SELECT id, name, email, password, role FROM users WHERE email = %s", (data.email,))
#             user = cursor.fetchone()
#             if not user or not pwd_context.verify(data.password.get_secret_value(), user["password"]):
#                 raise HTTPException(status_code=401, detail="Invalid credentials")
#             access_token = create_access_token({"sub": user["id"], "role": user["role"]})
#             return {
#                 "access_token": access_token,
#                 "token_type": "bearer",
#                 "user": {"id": user["id"], "name": user["name"], "email": user["email"], "role": user["role"]}
#             }
#     except pymysql.MySQLError as e:
#         raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    
# # # Add this before the /application-submit POST endpoint
# # @app.options("/application-submit")
# # async def options_application_submit():
# #     return Response(status_code=200, headers={
# #         "Access-Control-Allow-Origin": "http://localhost:5173",
# #         "Access-Control-Allow-Methods": "POST",
# #         "Access-Control-Allow-Headers": "Authorization, Content-Type"
# #     })
    
# ###---> (3)handling Application form 
# @app.post("/application-submit", response_model=ApplicationResponse)
# async def submit_application(
#     name: str = Form(...),
#     # email: str = Form(...),
#     email: EmailStr = Form(...),
#     mobile: str = Form(...),
#     job: str = Form(...),
#     cv: UploadFile = File(...),
#     current_user: dict = Depends(get_current_user),
#     db: pymysql.connections.Connection = Depends(get_db)
    
# ):
#     logging.basicConfig(level=logging.INFO)
#     logger = logging.getLogger(__name__)
#     logger.info(f"Received token: {current_user}")
#     logger.info(f"Received form data: name={name}, email={email}, mobile={mobile}, job={job}")
#     logger.info(f"File: {cv.filename}, Content-Type: {cv.content_type}")

#     #to validate the pdf
#     if cv.content_type != "application/pdf":
#         logger.error("Non-PDF file uploaded")
#         raise HTTPException(status_code=400, detail="CV must be a PDF")
    
#     #validate form data with pydantic 
#     try:
#         form_data = ApplicationForm(name=name, email=email, mobile=mobile, job=job)
#     except ValueError as e:
#         logger.error(f"Form validation error: {e}")
#         raise HTTPException(status_code=400, detail=str(e))

#     #generate unique filename for CV
#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     unique_id = str(uuid.uuid4())[:8]
#     cv_name = f"{timestamp}_{unique_id}.pdf"
#     cv_path = os.path.join(PDF_DIR, cv_name)
    
#     #save pdf 
#     with open(cv_path, "wb") as f:
#         shutil.copyfileobj(cv.file, f)
    
#     #store in database
#     try:
#         with db.cursor() as cursor:
#             cursor.execute(
#                 "INSERT INTO applications (user_id, name, email, mobile, cv_path, job, status) VALUES (%s, %s, %s, %s, %s, %s, %s)",
#                 (current_user["user_id"], form_data.name, form_data.email, form_data.mobile, cv_path, form_data.job, "Applied")
#             )
#             db.commit()
#             cursor.execute("SELECT LAST_INSERT_ID()")
#             app_id = cursor.fetchone()[0]
            
#         return ApplicationResponse(
#             id=app_id,
#             user_id=current_user["user_id"],
#             name=form_data.name,
#             email=form_data.email,
#             mobile=form_data.mobile,
#             cv_path=cv_path,
#             job=form_data.job,
#             status="Applied"
#         )
#     except pymysql.MySQLError as e:
#         logger.error(f"Database error: {e}")
#         # clean up file if database fails
#         if os.path.exists(cv_path):
#             os.remove(cv_path)
#         raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# ###---> (4)listing the applications(applicant can view their own appplications)
# @app.get("/applications", response_model=ApplicationListResponse)
# async def get_applications(current_user: dict = Depends(get_current_user), db: pymysql.connections.Connection = Depends(get_db)):
#     try:
#         with db.cursor(pymysql.cursors.DictCursor) as cursor:
#             cursor.execute(
#                 "SELECT id, user_id, name, email, mobile, cv_path, job, status FROM applications WHERE user_id = %s",
#                 (current_user["user_id"],)
#             )
#             applications = cursor.fetchall()
#             if not applications:
#                 raise HTTPException(status_code=404, detail="No applications found")
#             return ApplicationListResponse(applications=[ApplicationResponse(**app) for app in applications])
#     except pymysql.MySQLError as e:
#         raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# # ###---> (7)admin view of all applications
# # @app.get("/admin/applications", response_model=ApplicationListResponse)
# # async def get_all_applications(current_user: dict = Depends(get_current_admin), db: pymysql.connections.Connection = Depends(get_db)):
# #     try:
# #         with db.cursor(pymysql.cursors.DictCursor) as cursor:
# #             cursor.execute(
# #                 "SELECT id, user_id, name, email, mobile, cv_path, job, status FROM applications"
# #             )
# #             applications = cursor.fetchall()
# #             if not applications:
# #                 raise HTTPException(status_code=404, detail="No applications found")
# #             return ApplicationListResponse(applications=[ApplicationResponse(**app) for app in applications])
# #     except pymysql.MySQLError as e:
# #         raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# # ###---> (5)admin updates applications status 
# # @app.put("/applications/{app_id}", response_model=ApplicationResponse)
# # async def update_application_status(
# #     app_id: int,
# #     update_data: UpdateApplicationStatus,
# #     current_user: dict = Depends(get_current_admin),
# #     db: pymysql.connections.Connection = Depends(get_db)
# # ):
# #     try:
# #         with db.cursor() as cursor:
# #             # Check if application exists
# #             cursor.execute(
# #                 "SELECT user_id, status FROM applications WHERE id = %s",
# #                 (app_id,)
# #             )
# #             application = cursor.fetchone()
# #             if not application:
# #                 raise HTTPException(status_code=404, detail="Application not found")

# #             # Update the status
# #             cursor.execute(
# #                 "UPDATE applications SET status = %s WHERE id = %s",
# #                 (update_data.status, app_id)
# #             )
# #             if cursor.rowcount == 0:
# #                 raise HTTPException(status_code=500, detail="Failed to update application")
# #             db.commit()

# #             # Fetch updated application details
# #             cursor.execute(
# #                 "SELECT id, user_id, name, email, mobile, cv_path, job, status FROM applications WHERE id = %s",
# #                 (app_id,)
# #             )
# #             updated_app = cursor.fetchone()
# #             return ApplicationResponse(
# #                 id=updated_app[0],
# #                 user_id=updated_app[1],
# #                 name=updated_app[2],
# #                 email=updated_app[3],
# #                 mobile=updated_app[4],
# #                 cv_path=updated_app[5],
# #                 job=updated_app[6],
# #                 status=updated_app[7]
# #             )
# #     except pymysql.MySQLError as e:
# #         raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
# # ###---> (10) Applicant can edit the application
# # @app.put("/applications/{app_id}", response_model=ApplicationResponse)
# # async def edit_application(
    
# # #     app_id: int,
# # #     update_data: ApplicationEditForm,
# # #     current_user: dict = Depends(get_current_user),
# # #     db: pymysql.connections.Connection = Depends(get_db)
# # # ):
# # #     try:
# # #         with db.cursor() as cursor:
# # #             # Check if application exists and belongs to the user
# # #             cursor.execute(
# # #                 "SELECT user_id, status FROM applications WHERE id = %s",
# # #                 (app_id,)
# # #             )
# # #             application = cursor.fetchone()
# # #             if not application:
# # #                 raise HTTPException(status_code=404, detail="Application not found")
# # #             if current_user["user_id"] != application[0]:
# # #                 raise HTTPException(status_code=403, detail="Not authorized to edit this application")
# # #             if application[1] != "Applied":
# # #                 raise HTTPException(status_code=400, detail="Can only edit applications with status 'Applied'")

# # #             # Update the application details
# # #             cursor.execute(
# # #                 "UPDATE applications SET name = %s, email = %s, mobile = %s, job = %s WHERE id = %s",
# # #                 (update_data.name, update_data.email, update_data.mobile, update_data.job, app_id)
# # #             )
# # #             if cursor.rowcount == 0:
# # #                 raise HTTPException(status_code=500, detail="Failed to update application")
# # #             db.commit()

# # #             # Fetch updated application details
# # #             cursor.execute(
# # #                 "SELECT id, user_id, name, email, mobile, cv_path, job, status FROM applications WHERE id = %s",
# # #                 (app_id,)
# # #             )
# # #             updated_app = cursor.fetchone()
# # #             return ApplicationResponse(
# # #                 id=updated_app[0],
# # #                 user_id=updated_app[1],
# # #                 name=updated_app[2],
# # #                 email=updated_app[3],
# # #                 mobile=updated_app[4],
# # #                 cv_path=updated_app[5],
# # #                 job=updated_app[6],
# # #                 status=updated_app[7]
# # #             )
# # #     except pymysql.MySQLError as e:
# # #         raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
# #     app_id: int,
# #         name: str = Form(...),
# #         email: EmailStr = Form(...),
# #         mobile: str = Form(...),
# #         job: str = Form(...),
# #         cv: UploadFile = File(None),
# #         current_user: dict = Depends(get_current_user),
# #         db: pymysql.connections.Connection = Depends(get_db)
# #     ):
# #     # Validate form data with Pydantic
# #     try:
# #         form_data = ApplicationEditForm(name=name, email=email, mobile=mobile, job=job)
# #     except ValueError as e:
# #         raise HTTPException(status_code=400, detail=str(e))

# #     try:
# #         with db.cursor() as cursor:
# #             # Check if application exists and belongs to the user
# #             cursor.execute(
# #                 "SELECT user_id, status, cv_path FROM applications WHERE id = %s",
# #                 (app_id,)
# #             )
# #             application = cursor.fetchone()
# #             if not application:
# #                 raise HTTPException(status_code=404, detail="Application not found")
# #             if current_user["user_id"] != application[0]:
# #                 raise HTTPException(status_code=403, detail="Not authorized to edit this application")
# #             if application[1] != "Applied":
# #                 raise HTTPException(status_code=400, detail="Can only edit applications with status 'Applied'")

# #             # Handle CV update if provided
# #             new_cv_path = application[2]  # Default to existing cv_path
# #             if cv:
# #                 # Validate the new CV
# #                 if cv.content_type != "application/pdf":
# #                     raise HTTPException(status_code=400, detail="CV must be a PDF")

# #                 # Delete the old CV file
# #                 old_cv_path = application[2]
# #                 if os.path.exists(old_cv_path):
# #                     os.remove(old_cv_path)

# #                 # Generate new filename and save the new CV
# #                 timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
# #                 unique_id = str(uuid.uuid4())[:8]
# #                 cv_name = f"{timestamp}_{unique_id}.pdf"
# #                 new_cv_path = os.path.join(PDF_DIR, cv_name)
# #                 with open(new_cv_path, "wb") as f:
# #                     shutil.copyfileobj(cv.file, f)

# #             # Update the application details
# #             cursor.execute(
# #                 "UPDATE applications SET name = %s, email = %s, mobile = %s, job = %s, cv_path = %s WHERE id = %s",
# #                 (form_data.name, form_data.email, form_data.mobile, form_data.job, new_cv_path, app_id)
# #             )
# #             if cursor.rowcount == 0:
# #                 raise HTTPException(status_code=500, detail="Failed to update application")
# #             db.commit()

# #             # Fetch updated application details
# #             cursor.execute(
# #                 "SELECT id, user_id, name, email, mobile, cv_path, job, status FROM applications WHERE id = %s",
# #                 (app_id,)
# #             )
# #             updated_app = cursor.fetchone()
# #             return ApplicationResponse(
# #                 id=updated_app[0],
# #                 user_id=updated_app[1],
# #                 name=updated_app[2],
# #                 email=updated_app[3],
# #                 mobile=updated_app[4],
# #                 cv_path=updated_app[5],
# #                 job=updated_app[6],
# #                 status=updated_app[7]
# #             )
# #     except pymysql.MySQLError as e:
# #         # Clean up new CV file if database update fails
# #         if cv and 'new_cv_path' in locals() and os.path.exists(new_cv_path):
# #             os.remove(new_cv_path)
# #         raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
# #     except OSError as e:
# #         raise HTTPException(status_code=500, detail=f"Failed to handle CV file: {str(e)}")
    
# # ###---> (8)delete application
# # @app.delete("/applications/{app_id}")
# # async def delete_application(
# #     app_id: int,
# #     current_user: dict = Depends(get_current_user),
# #     db: pymysql.connections.Connection = Depends(get_db)   
# # ):
# #     try:
# #         with db.cursor() as cursor:
# #             # Check if application exists
# #             cursor.execute(
# #                 "SELECT user_id, cv_path FROM applications WHERE id = %s",
# #                 (app_id,)
# #             )
# #             application = cursor.fetchone()
# #             if not application:
# #                 raise HTTPException(status_code=404, detail="Application not found")

# #             # Check ownership or admin privilege
# #             if current_user["role"] != "admin" and current_user["user_id"] != application[0]:
# #                 raise HTTPException(status_code=403, detail="Not authorized to delete this application")

# #             # Delete the CV file
# #             cv_path = application[1]
# #             if os.path.exists(cv_path):
# #                 os.remove(cv_path)

# #             # Delete the application from the database
# #             cursor.execute(
# #                 "DELETE FROM applications WHERE id = %s",
# #                 (app_id,)
# #             )
# #             db.commit()

# #             return {"message": "Application deleted successfully"}
# #     except pymysql.MySQLError as e:
# #         raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
# #     except OSError as e:
# #         raise HTTPException(status_code=500, detail=f"Failed to delete CV file: {str(e)}")
    
# # ###---> (9) Download CV
# # @app.get("/applications/{app_id}/cv")
# # async def download_cv(
# #     app_id: int,
# #     current_user: dict = Depends(get_current_admin),
# #     db: pymysql.connections.Connection = Depends(get_db)
# # ):
# #     try:
# #         with db.cursor() as cursor:
# #             # Check if application exists
# #             cursor.execute(
# #                 "SELECT cv_path, status FROM applications WHERE id = %s",
# #                 (app_id,)
# #             )
# #             application = cursor.fetchone()
# #             if not application:
# #                 raise HTTPException(status_code=404, detail="Application not found")

# #             cv_path = application[0]
# #             if not os.path.exists(cv_path):
# #                 raise HTTPException(status_code=404, detail="CV file not found")

# #             # Update status to "Resume Downloaded" if not already
# #             if application[1] != "Resume Downloaded":
# #                 cursor.execute(
# #                     "UPDATE applications SET status = %s WHERE id = %s",
# #                     ("Resume Downloaded", app_id)
# #                 )
# #                 db.commit()

# #             return FileResponse(
# #                 path=cv_path,
# #                 filename=os.path.basename(cv_path),
# #                 media_type="application/pdf"
# #             )
# #     except pymysql.MySQLError as e:
# #         raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
# #     except OSError as e:
# #         raise HTTPException(status_code=500, detail=f"Failed to access CV file: {str(e)}")

# # ###---> (11) View Profile
# # @app.get("/profile", response_model=UserResponse)
# # async def get_profile(current_user: dict = Depends(get_current_user), db: pymysql.connections.Connection = Depends(get_db)):
# #     try:
# #         with db.cursor(pymysql.cursors.DictCursor) as cursor:
# #             cursor.execute(
# #                 "SELECT id, name, email, role FROM users WHERE id = %s",
# #                 (current_user["user_id"],)
# #             )
# #             user = cursor.fetchone()
# #             if not user:
# #                 raise HTTPException(status_code=404, detail="User not found")
# #             return user
# #     except pymysql.MySQLError as e:
# #         raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# # ###---> (12) Update Profile
# # @app.put("/profile", response_model=UserResponse)
# # async def update_profile(
# #     update_data: ProfileUpdateForm,
# #     current_user: dict = Depends(get_current_user),
# #     db: pymysql.connections.Connection = Depends(get_db)
# # ):
# #     try:
# #         with db.cursor() as cursor:
# #             # Fetch current user details
# #             cursor.execute(
# #                 "SELECT name, email, password FROM users WHERE id = %s",
# #                 (current_user["user_id"],)
# #             )
# #             user = cursor.fetchone()
# #             if not user:
# #                 raise HTTPException(status_code=404, detail="User not found")

# #             # Prepare updated values
# #             new_name = update_data.name if update_data.name is not None else user[0]
# #             new_email = update_data.email if update_data.email is not None else user[1]
# #             new_password = pwd_context.hash(update_data.password.get_secret_value()) if update_data.password else user[2]

# #             # Update user in database
# #             cursor.execute(
# #                 "UPDATE users SET name = %s, email = %s, password = %s WHERE id = %s",
# #                 (new_name, new_email, new_password, current_user["user_id"])
# #             )
# #             db.commit()

# #             # Fetch updated user details
# #             cursor.execute(
# #                 "SELECT id, name, email, role FROM users WHERE id = %s",
# #                 (current_user["user_id"],)
# #             )
# #             updated_user = cursor.fetchone()
# #             return UserResponse(
# #                 id=updated_user[0],
# #                 name=updated_user[1],
# #                 email=updated_user[2],
# #                 role=updated_user[3]
# #             )
# #     except pymysql.err.IntegrityError:
# #         raise HTTPException(status_code=400, detail="Email already exists")
# #     except pymysql.MySQLError as e:
# #         raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
# ###---> (13) Logout
# @app.post("/logout")
# async def logout(token: str = Depends(oauth2_scheme)):
#     blacklisted_tokens.add(token)
#     return JSONResponse(status_code=200, content={"message": "Successfully logged out"})

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel, SecretStr, EmailStr, validator
from fastapi.responses import FileResponse, JSONResponse
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

#database configuration   
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
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not define in the .env file.")
ADMIN_CODE = os.getenv("ADMIN_CODE")
if not ADMIN_CODE:
    raise ValueError("ADMIN_CODE environment variable is not define in the .env file.")
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
    cpassword: SecretStr | None = None
    
    @validator("password", always=True)
    def validate_password(cls, v: SecretStr | None, values):
        if v is None:
            return v
        password = v.get_secret_value()
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.match(r"^(?=.*[a-zA-Z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]+$", password):
            raise ValueError("Password must contain at least one letter, one number, and one symbol (@$!%*?&)")
        return v

    @validator("cpassword", always=True)
    def passwords_match(cls, v: SecretStr | None, values):
        if "password" in values and values["password"] is not None:
            if v is None or v.get_secret_value() != values["password"].get_secret_value():
                raise ValueError("Passwords do not match")
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

async def get_current_admin(token: str = Depends(oauth2_scheme)):
    user = await get_current_user(token)
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

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

###---> (6)handling Admin Signup
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

###---> (4)listing the applications(applicant can view their own appplications)
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

###---> (7)admin view of all applications
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
            return ApplicationListResponse(applications=[ApplicationResponse(**app) for app in applications])
    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

###---> (5)admin updates applications status 
@app.put("/applications/{app_id}", response_model=ApplicationResponse)
async def update_application_status(
    app_id: int,
    update_data: UpdateApplicationStatus,
    current_user: dict = Depends(get_current_admin),
    db: pymysql.connections.Connection = Depends(get_db)
):
    try:
        with db.cursor() as cursor:
            # Check if application exists
            cursor.execute(
                "SELECT user_id, status FROM applications WHERE id = %s",
                (app_id,)
            )
            application = cursor.fetchone()
            if not application:
                raise HTTPException(status_code=404, detail="Application not found")

            # Update the status
            cursor.execute(
                "UPDATE applications SET status = %s WHERE id = %s",
                (update_data.status, app_id)
            )
            if cursor.rowcount == 0:
                raise HTTPException(status_code=500, detail="Failed to update application")
            db.commit()

            # Fetch updated application details
            cursor.execute(
                "SELECT id, user_id, name, email, mobile, cv_path, job, status FROM applications WHERE id = %s",
                (app_id,)
            )
            updated_app = cursor.fetchone()
            return ApplicationResponse(
                id=updated_app[0],
                user_id=updated_app[1],
                name=updated_app[2],
                email=updated_app[3],
                mobile=updated_app[4],
                cv_path=updated_app[5],
                job=updated_app[6],
                status=updated_app[7]
            )
    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
###---> (10) Applicant can edit the application
@app.put("/applications/{app_id}", response_model=ApplicationResponse)
async def edit_application(
    
#     app_id: int,
#     update_data: ApplicationEditForm,
#     current_user: dict = Depends(get_current_user),
#     db: pymysql.connections.Connection = Depends(get_db)
# ):
#     try:
#         with db.cursor() as cursor:
#             # Check if application exists and belongs to the user
#             cursor.execute(
#                 "SELECT user_id, status FROM applications WHERE id = %s",
#                 (app_id,)
#             )
#             application = cursor.fetchone()
#             if not application:
#                 raise HTTPException(status_code=404, detail="Application not found")
#             if current_user["user_id"] != application[0]:
#                 raise HTTPException(status_code=403, detail="Not authorized to edit this application")
#             if application[1] != "Applied":
#                 raise HTTPException(status_code=400, detail="Can only edit applications with status 'Applied'")

#             # Update the application details
#             cursor.execute(
#                 "UPDATE applications SET name = %s, email = %s, mobile = %s, job = %s WHERE id = %s",
#                 (update_data.name, update_data.email, update_data.mobile, update_data.job, app_id)
#             )
#             if cursor.rowcount == 0:
#                 raise HTTPException(status_code=500, detail="Failed to update application")
#             db.commit()

#             # Fetch updated application details
#             cursor.execute(
#                 "SELECT id, user_id, name, email, mobile, cv_path, job, status FROM applications WHERE id = %s",
#                 (app_id,)
#             )
#             updated_app = cursor.fetchone()
#             return ApplicationResponse(
#                 id=updated_app[0],
#                 user_id=updated_app[1],
#                 name=updated_app[2],
#                 email=updated_app[3],
#                 mobile=updated_app[4],
#                 cv_path=updated_app[5],
#                 job=updated_app[6],
#                 status=updated_app[7]
#             )
#     except pymysql.MySQLError as e:
#         raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    app_id: int,
        name: str = Form(...),
        email: EmailStr = Form(...),
        mobile: str = Form(...),
        job: str = Form(...),
        cv: UploadFile = File(None),
        current_user: dict = Depends(get_current_user),
        db: pymysql.connections.Connection = Depends(get_db)
    ):
    # Validate form data with Pydantic
    try:
        form_data = ApplicationEditForm(name=name, email=email, mobile=mobile, job=job)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        with db.cursor() as cursor:
            # Check if application exists and belongs to the user
            cursor.execute(
                "SELECT user_id, status, cv_path FROM applications WHERE id = %s",
                (app_id,)
            )
            application = cursor.fetchone()
            if not application:
                raise HTTPException(status_code=404, detail="Application not found")
            if current_user["user_id"] != application[0]:
                raise HTTPException(status_code=403, detail="Not authorized to edit this application")
            if application[1] != "Applied":
                raise HTTPException(status_code=400, detail="Can only edit applications with status 'Applied'")

            # Handle CV update if provided
            new_cv_path = application[2]  # Default to existing cv_path
            if cv:
                # Validate the new CV
                if cv.content_type != "application/pdf":
                    raise HTTPException(status_code=400, detail="CV must be a PDF")

                # Delete the old CV file
                old_cv_path = application[2]
                if os.path.exists(old_cv_path):
                    os.remove(old_cv_path)

                # Generate new filename and save the new CV
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                unique_id = str(uuid.uuid4())[:8]
                cv_name = f"{timestamp}_{unique_id}.pdf"
                new_cv_path = os.path.join(PDF_DIR, cv_name)
                with open(new_cv_path, "wb") as f:
                    shutil.copyfileobj(cv.file, f)

            # Update the application details
            cursor.execute(
                "UPDATE applications SET name = %s, email = %s, mobile = %s, job = %s, cv_path = %s WHERE id = %s",
                (form_data.name, form_data.email, form_data.mobile, form_data.job, new_cv_path, app_id)
            )
            if cursor.rowcount == 0:
                raise HTTPException(status_code=500, detail="Failed to update application")
            db.commit()

            # Fetch updated application details
            cursor.execute(
                "SELECT id, user_id, name, email, mobile, cv_path, job, status FROM applications WHERE id = %s",
                (app_id,)
            )
            updated_app = cursor.fetchone()
            return ApplicationResponse(
                id=updated_app[0],
                user_id=updated_app[1],
                name=updated_app[2],
                email=updated_app[3],
                mobile=updated_app[4],
                cv_path=updated_app[5],
                job=updated_app[6],
                status=updated_app[7]
            )
    except pymysql.MySQLError as e:
        # Clean up new CV file if database update fails
        if cv and 'new_cv_path' in locals() and os.path.exists(new_cv_path):
            os.remove(new_cv_path)
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Failed to handle CV file: {str(e)}")
    
###---> (8)delete application
@app.delete("/applications/{app_id}")
async def delete_application(
    app_id: int,
    current_user: dict = Depends(get_current_user),
    db: pymysql.connections.Connection = Depends(get_db)   
):
    try:
        with db.cursor() as cursor:
            # Check if application exists
            cursor.execute(
                "SELECT user_id, cv_path FROM applications WHERE id = %s",
                (app_id,)
            )
            application = cursor.fetchone()
            if not application:
                raise HTTPException(status_code=404, detail="Application not found")

            # Check ownership or admin privilege
            if current_user["role"] != "admin" and current_user["user_id"] != application[0]:
                raise HTTPException(status_code=403, detail="Not authorized to delete this application")

            # Delete the CV file
            cv_path = application[1]
            if os.path.exists(cv_path):
                os.remove(cv_path)

            # Delete the application from the database
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
    
###---> (9) Download CV
@app.get("/applications/{app_id}/cv")
async def download_cv(
    app_id: int,
    current_user: dict = Depends(get_current_admin),
    db: pymysql.connections.Connection = Depends(get_db)
):
    try:
        with db.cursor() as cursor:
            # Check if application exists
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

            # Update status to "Resume Downloaded" if not already
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

###---> (11) View Profile
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
            return user
    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

###---> (12) Update Profile
@app.put("/profile", response_model=UserResponse)
async def update_profile(
    update_data: ProfileUpdateForm,
    current_user: dict = Depends(get_current_user),
    db: pymysql.connections.Connection = Depends(get_db)
):
    try:
        with db.cursor() as cursor:
            # Fetch current user details
            cursor.execute(
                "SELECT name, email, password FROM users WHERE id = %s",
                (current_user["user_id"],)
            )
            user = cursor.fetchone()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Prepare updated values
            new_name = update_data.name if update_data.name is not None else user[0]
            new_email = update_data.email if update_data.email is not None else user[1]
            new_password = pwd_context.hash(update_data.password.get_secret_value()) if update_data.password else user[2]

            # Update user in database
            cursor.execute(
                "UPDATE users SET name = %s, email = %s, password = %s WHERE id = %s",
                (new_name, new_email, new_password, current_user["user_id"])
            )
            db.commit()

            # Fetch updated user details
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
    
###---> (13) Logout
@app.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    blacklisted_tokens.add(token)
    return JSONResponse(status_code=200, content={"message": "Successfully logged out"})