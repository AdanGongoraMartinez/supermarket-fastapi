from sqlmodel import SQLModel


class SupermarketBase(SQLModel):
    name: str


class SupermarketCreate(SupermarketBase):
    pass


class SupermarketUpdate(SupermarketBase):
    pass


class SupermarketPublic(SupermarketBase):
    id: int
