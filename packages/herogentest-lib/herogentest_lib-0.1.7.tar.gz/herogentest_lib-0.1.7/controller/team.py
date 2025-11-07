# app/routers/team.py
from controller.generic import create_crud_router
from herogentest_lib.model.models import Team 
from herogentest_lib.model.dto import TeamCreate, TeamUpdate, TeamRead

router = create_crud_router(
    model=Team,
    create_schema=TeamCreate,
    update_schema=TeamUpdate,
    read_schema=TeamRead,
    prefix="/teams",
    tags=["teams"],
)