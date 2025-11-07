from model.models import HeroBase, TeamBase
from typing import  List, Optional
from sqlmodel import Field

class TeamCreate(TeamBase):
    pass
# fim_class

class TeamPublic(TeamBase):
    id: int
    model_config = {"from_attributes": True}
# fim_class

class TeamWithHeroes(TeamPublic):
    heroes: List["HeroPublic"] = []
    model_config = {"from_attributes": True}
# fim_class

class TeamCreate(TeamBase):
    pass
# fim_class

class TeamRead(TeamBase):
    id: int
# fim_class

class TeamUpdate(TeamBase):
    name: Optional[str] = None
# fim_class

class HeroCreate(HeroBase):
    team_id: Optional[int] = None  # permite já criar vinculado a um time
# fim_class

class HeroUpdate(HeroBase):
    name: Optional[str] = Field(default=None, min_length=2, max_length=120)
    secret_name: Optional[str] = None
    age: Optional[int] = Field(default=None, ge=0, le=200)
# fim_class
    
class HeroPublic(HeroBase):
    id: int
    model_config = {"from_attributes": True}
# fim_class

class HeroRead(HeroBase):
    id: int
    team_id: Optional[int] = None
# fim_class
