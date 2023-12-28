from pydantic import BaseModel


class video(BaseModel):
    id: int
    name: str
    author: str
    description: str
    genre: str
