from fastapi import FastAPI, Depends
from app.models.organizations import Organization
from app.core.redis import redis_client
from app.api import auth
from app.api import workflows

app = FastAPI()

app.include_router(auth.router)
app.include_router(workflows.router)

@app.get("/health")
def health():
    return{"status": "healthy"}

@app.get("/redis-test")
def redis_test():
    redis_client.set("hello", "world")

    value = redis_client.get("hello")

    return {"value": value.decode()}

from app.core.deps import get_current_user

@app.get("/me")
def read_current_user(current_user = Depends(get_current_user)):
    return current_user