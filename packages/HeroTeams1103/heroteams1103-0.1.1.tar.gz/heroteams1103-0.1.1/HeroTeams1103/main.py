from fastapi import FastAPI
from HeroTeams1103.util.database import init_db
from HeroTeams1103.controller.hero import router as heroes_router
from HeroTeams1103.controller.team import router as teams_router

app = FastAPI(title="FastAPI + SQLModel - MVC + Repository")

init_db()

app.include_router(heroes_router)
app.include_router(teams_router)

@app.get("/")
def health():
    return {"status": "ok"}
