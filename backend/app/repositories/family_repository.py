from sqlalchemy.orm import Session

from app.models.family import Family


class FamilyRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_family_by_name(self, name: str) -> Family | None:
        return self.db.query(Family).filter(Family.name == name).first()

    def create_family(self, name: str) -> Family:
        family = Family(name=name)

        self.db.add(family)
        self.db.commit()
        self.db.refresh(family)

        return family