from sqlmodel import Field, SQLModel


class ComparerRequest(SQLModel):
    product_ids: list[int] = Field(min_length=1)


class SupermarketComparison(SQLModel):
    supermarket_id: int
    supermarket_name: str
    total: float
    found_products: int
    missing_product_ids: list[int] = Field(default_factory=list)


class ComparerResult(SQLModel):
    best: SupermarketComparison | None
    ranking: list[SupermarketComparison]
