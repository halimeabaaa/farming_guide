from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenVerisi(BaseModel):
    eposta: str | None = None