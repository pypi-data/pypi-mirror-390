from fastapi import FastAPI
from util.database import init_db
from controller.controller_hero import router as heroes_router

app = FastAPI(title="FastAPI + SQLModel - MVC + Repository")

init_db()

app.include_router(heroes_router)

@app.get("/")
def health():
    return {"status": "ok"}
