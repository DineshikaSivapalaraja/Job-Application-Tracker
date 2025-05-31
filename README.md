# Job-Application-Tracker

### Welcome to My Job Application Tracker!

This is a full-stack web application designed to help job applicants track the status of their job applications. It aims to solve a real-world problem where many applicants apply for jobs but never hear back from companies.

### Purpose

The main goal of this app is to:

* Help applicants apply for jobs and track their application status.
* Allow admins (HR or recruiters) to update the status of each application.
* Improve communication between job seekers and companies.

### Key Roles

* **Applicant** – Can apply for jobs and view the current status.
* **Admin** – Can view applications and update their status.

### Features

* Secure user registration and login(admin & applicant) using **JWT authentication**.
* Role-based access control.
* Profile management
* Submit, edit, and delete job applications
* Upload and download CVs
* Admin dashboard to manage all applications and users
* Easy-to-use interface for both applicants and admins.
* Real-time status updates.
* Responsive UI(Simple design)

## Tech Stack
- **Backend:** FastAPI
- **Frontend:** React
- **Database:** MySQL

---

## Setup Instructions

### Backend

## Requirements
* Python 3.12 or newer(I used 3.13)
* pip for installing packages
* A virtual environment to keep things clean

## Setting Things Up

1. **Install dependencies**
    ```bash
    cd backend
    pip install -r requirements.txt
    ```
    To install the backend dependencies manually,
    ```bash
    pip install fastapi uvicorn pymysql passlib[bcrypt] pyjwt python-dotenv
    ```

2. **Configure environment variables**  
   Follow the variable set as `backend/.env.example` to make .env file with own values:

3. **Generating a Secret Key**
    I use a secret key for handling JWTs (JSON Web Tokens). To generate one, just run:

    ```bash
    python generate_key.py
    ```
4. **Use a Virtual Environment (Recommended)**
    It's a good idea to use a virtual environment so your project dependencies don't interfere with other Python projects on your system.

    ```bash
    python -m venv venv
    .venv\Scripts\activate  # On Windows
    ```
5. **Run the backend server**
    ```bash
    uvicorn app:app --reload
    ```
    If you want to run it on a different port (say, 8005), use:

    ```bash
    uvicorn app:app --reload --port 8005
    ```
---

### Frontend

1. **Install dependencies**
    ```bash
    cd frontend
    npm install
    ```

2. **Configure environment variables**  
   Edit `frontend/.env`:
    ```
    VITE_API_URL=http://127.0.0.1:8000
    ```

3. **Run the frontend dev server**
    ```sh
    npm run dev
    ```
---

## Environment Variables

- **Backend:**  
  See `backend/.env.example` for all required variables.

- **Frontend:**  
  - `VITE_API_URL` — Base URL for backend API.

---

## Usage

- Visit the frontend in your browser (default: `http://localhost:5173`).
- Register as an applicant or admin.
- Applicants can submit and track job applications, upload CVs.
- Admins can view, manage, and download all applications and CVs.

---

## API Endpoints

**Applicants:**
- `POST /signup` — Register
- `POST /login` — Login
- `GET /profile` — View profile
- `PUT /profile` — Edit profile
- `POST /application-submit` — Submit application
- `GET /applications` — List own applications
- `PUT /edit-applications/{app_id}` — Edit application
- `DELETE /applications/{app_id}` — Delete application

**Admins:**
- `POST /admin-signup` — Register as admin
- `GET /admin/applications` — List all applications
- `PUT /applications/{app_id}` — Update application status
- `GET /applications/{app_id}/cv` — Download CV

---



