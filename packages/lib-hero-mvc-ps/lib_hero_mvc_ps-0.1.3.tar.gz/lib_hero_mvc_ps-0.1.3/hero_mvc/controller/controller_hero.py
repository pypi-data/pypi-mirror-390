# app/controllers/heroes.py
from fastapi import APIRouter, Query, Depends
from typing import List, Annotated
from util.database import SessionDep
from model.dto import HeroCreate, HeroUpdate, HeroPublic
from service.hero_service import HeroService

router = APIRouter(prefix="/heroes", tags=["Heroes"])

def get_hero_service(session: SessionDep) -> HeroService:
    return HeroService(session)

ServiceDep = Annotated[HeroService, Depends(get_hero_service)]

@router.post("/", response_model=HeroPublic, status_code=201)
def create_hero(hero: HeroCreate, service: ServiceDep):
    return service.create(hero)

@router.get("/", response_model=List[HeroPublic])
def read_heroes(
    service: ServiceDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    return service.list(offset, limit)

@router.get("/{hero_id}", response_model=HeroPublic)
def read_hero(hero_id: int, service: ServiceDep):
    return service.get(hero_id)

@router.patch("/{hero_id}", response_model=HeroPublic)
def update_hero(hero_id: int, hero: HeroUpdate, service: ServiceDep):
    return service.update(hero_id, hero)

@router.delete("/{hero_id}", status_code=204)
def delete_hero(hero_id: int, service: ServiceDep):
    service.delete(hero_id)
    return None
