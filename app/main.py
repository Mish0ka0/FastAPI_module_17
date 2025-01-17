from fastapi import FastAPI
from app.routers import task, user

app = FastAPI()


@app.get("/")
async def main():
    return {"message": "Welcome to TaskManager"}


app.include_router(user.router)
app.include_router(task.router)
