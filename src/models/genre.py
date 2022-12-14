from src.models.base import BaseOrjsonModel


class Genre(BaseOrjsonModel):
    id: str
    name: str
    description: str | None

