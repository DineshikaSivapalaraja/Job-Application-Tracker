# Job-Application-Tracker

# 💼 Job Application Tracker - Backend
Welcome! This is the backend of the Job Application Tracker project, built with FastAPI.
This section will walk you through how to set everything up and get the backend running locally.

⚙️ What You’ll Need
Before you get started, make sure you have:

Python 3.12 or newer(I used 3.13)

pip for installing packages

A virtual environment to keep things clean

## 📦 Setting Things Up

### 1. Use a Virtual Environment (Recommended)

It's a good idea to use a virtual environment so your project dependencies don't interfere with other Python projects on your system.

```bash
python -m venv venv
.venv\Scripts\activate  # On Windows
```

### 2. Install the Required Packages

```bash
pip install fastapi uvicorn pymysql passlib[bcrypt] pyjwt python-dotenv
```

---

## 🔑 Generating a Secret Key

I use a secret key for handling JWTs (JSON Web Tokens). To generate one, just run:

```bash
python generate_key.py
```

---

## 🚀 Running the Backend

Once everything’s set up, you can start the development server with:

```bash
uvicorn app:app --reload
```

If you want to run it on a different port (say, 8005), use:

```bash
uvicorn app:app --reload --port 8005
```

The `--reload` flag makes the server automatically restart when you make changes — useful for development.

---

## 📋 Managing Dependencies

To save your installed dependencies:

```bash
pip freeze > requirements.txt
```

And if you're setting up the project on a new machine later:

```bash
pip install -r requirements.txt
```



