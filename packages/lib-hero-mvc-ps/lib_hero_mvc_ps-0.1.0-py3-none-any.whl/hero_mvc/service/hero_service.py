# app/services/hero_service.py
from fastapi import HTTPException, status
from typing import List
from sqlmodel import Session
from model.models import Hero
from model.dto import HeroCreate, HeroUpdate, HeroPublic
from repository.hero_repository import HeroRepository

class HeroService:
    def __init__(self, session: Session):
        self.repo = HeroRepository(session)

    def create(self, payload: HeroCreate) -> HeroPublic:
        # Exemplo de regra: nome único (opcional)
        if self.repo.get_by_name(payload.name):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Hero name already exists")
        hero = self.repo.create(payload)
        return HeroPublic.model_validate(hero)

    def list(self, offset: int, limit: int) -> List[HeroPublic]:
        heroes = self.repo.list(offset, limit)
        return [HeroPublic.model_validate(h) for h in heroes]

    def get(self, hero_id: int) -> HeroPublic:
        hero = self.repo.get(hero_id)
        if not hero:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hero not found")
        return HeroPublic.model_validate(hero)

    def update(self, hero_id: int, payload: HeroUpdate) -> HeroPublic:
        hero = self.repo.get(hero_id)
        if not hero:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hero not found")
        hero = self.repo.update(hero, payload)
        return HeroPublic.model_validate(hero)

    def delete(self, hero_id: int) -> None:
        hero = self.repo.get(hero_id)
        if not hero:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hero not found")
        self.repo.delete(hero)
