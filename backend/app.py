from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def get():
    return "welcome to the website"

@app.post("/post")
async def post():
    greeting = "Welcome"
    return greeting

