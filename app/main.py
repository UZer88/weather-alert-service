from fastapi import FastAPI
from app.routers import auth, subscriptions
from app.database import init_db

app = FastAPI(title="Weather Alert Service")


@app.on_event("startup")
async def startup():
    await init_db()
    print("✅ Database initialized")


@app.get("/")
async def root():
    return {"message": "Weather Alert Service is running"}


@app.get("/ping")
async def ping():
    return {"status": "ok"}


# Подключаем роутеры
app.include_router(auth.router)
app.include_router(subscriptions.router)