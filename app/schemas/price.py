from sqlmodel import Field, SQLModel


class PriceBase(SQLModel):
    price: float = Field(gt=0)


class PriceCreate(PriceBase):
    product_id: int
    supermarket_id: int


class PriceUpdate(PriceBase):
    product_id: int
    supermarket_id: int


class PricePublic(PriceBase):
    id: int
