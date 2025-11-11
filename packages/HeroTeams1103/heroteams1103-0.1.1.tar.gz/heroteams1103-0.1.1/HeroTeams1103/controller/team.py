from HeroTeams1103.controller.generic import create_crud_router
from HeroTeams1103.model.models import Team 
from HeroTeams1103.model.dto import TeamCreate, TeamUpdate, TeamRead

router = create_crud_router(
    model=Team,
    create_schema=TeamCreate,
    update_schema=TeamUpdate,
    read_schema=TeamRead,
    prefix="/teams",
    tags=["teams"],
)
