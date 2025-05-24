# Job-Application-Tracker

# 💼 Job Application Tracker - Backend

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



