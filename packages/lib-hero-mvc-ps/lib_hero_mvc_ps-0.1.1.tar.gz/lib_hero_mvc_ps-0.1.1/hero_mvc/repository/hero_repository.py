# app/repositories/hero_repository.py
from sqlmodel import Session, select
from typing import List, Optional
from model.dto import HeroCreate, HeroUpdate
from model.models import Hero

class HeroRepository:
    def __init__(self, session: Session):
        self.session = session

    def list(self, offset: int = 0, limit: int = 100) -> List[Hero]:
        return list(self.session.exec(select(Hero).offset(offset).limit(limit)).all())

    def get(self, hero_id: int) -> Optional[Hero]:
        return self.session.get(Hero, hero_id)

    def get_by_name(self, name: str) -> Optional[Hero]:
        return self.session.exec(select(Hero).where(Hero.name == name)).first()

    def create(self, data: HeroCreate) -> Hero:
        hero = Hero.model_validate(data)  # equivalente a Hero(**data.model_dump())
        self.session.add(hero)
        self.session.commit()
        self.session.refresh(hero)
        return hero

    def update(self, hero: Hero, data: HeroUpdate) -> Hero:
        update_data = data.model_dump(exclude_unset=True)
        for k, v in update_data.items():
            setattr(hero, k, v)
        self.session.add(hero)
        self.session.commit()
        self.session.refresh(hero)
        return hero

    def delete(self, hero: Hero) -> None:
        self.session.delete(hero)
        self.session.commit()
