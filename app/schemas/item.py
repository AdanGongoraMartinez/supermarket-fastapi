from sqlmodel import Field, SQLModel


class ItemBase(SQLModel):
    nombre: str
    precio: float = Field(gt=0)


class ItemCreate(ItemBase):
    pass


class ItemUpdate(ItemBase):
    pass


class ItemPublic(ItemBase):
    id: int
