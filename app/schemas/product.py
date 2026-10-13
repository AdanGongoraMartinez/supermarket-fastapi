from sqlmodel import SQLModel


class ProductBase(SQLModel):
    name: str
    brand: str | None
    presentation: str
    barcode: str | None
    # category_id: str


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    pass


class ProductPublic(ProductBase):
    id: int
