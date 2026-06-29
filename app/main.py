from fastapi import FastAPI
from app.db.database import Base, engine
from app.models.organizations import Organization
from app.core.redis import redis_client
from app.api import auth

app = FastAPI()

app.include_router(auth.router)

@app.get("/health")
def health():
    return{"status": "healthy"}

@app.get("/redis-test")
def redis_test():
    redis_client.set("hello", "world")

    value = redis_client.get("hello")

    return {"value": value.decode()}