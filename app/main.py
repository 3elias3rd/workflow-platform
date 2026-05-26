from fastapi import FastAPI
from app.db.database import Base, engine
from app.models.organization import Organization
from app.core.redis import redis_client

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/health")
def health():
    return{"status": "healthy"}

@app.get("/redis-test")
def redis_test():
    redis_client.set("hello", "world")

    value = redis_client.get("hello")

    return {"value": value.decode()}