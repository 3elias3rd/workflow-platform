from fastapi import FastAPI, Depends
from app.core.redis import redis_client
from app.api import auth, triggers, workflows, actions, webhooks, executions


app = FastAPI()

app.include_router(auth.router)
app.include_router(workflows.router)
app.include_router(triggers.router)
app.include_router(actions.router)
app.include_router(webhooks.router)
app.include_router(executions.router)

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