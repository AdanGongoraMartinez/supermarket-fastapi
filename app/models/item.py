from sqlmodel import Field

from app.schemas.item import ItemBase


class Item(ItemBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
