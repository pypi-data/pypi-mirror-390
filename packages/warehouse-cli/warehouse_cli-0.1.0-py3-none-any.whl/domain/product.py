from dataclasses import dataclass
from pydantic import BaseModel, field_validator, ConfigDict

@dataclass(frozen=True)
class ProductId:
    id: int


class Product(BaseModel):
    id: ProductId | None = None
    name: str
    price: float = 0.0
    quantity: int = 0

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ProductId: lambda v: v.id}
    )

    @field_validator('quantity')
    @classmethod
    def quantity_positive(cls, v: int) -> int:
        if v < 1:
            raise ValueError('quantity field have to be a positive number ... !')
        return v

    @field_validator('price')
    @classmethod
    def price_non_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError('price field have to be a not negative number ... !')
        return v

    @field_validator('name')
    @classmethod
    def name_valid(cls, v: str) -> str:
        cleaned = v.strip()
        if len(cleaned) < 3:
            raise ValueError('name field have to be at least 3 character ... !')
        return cleaned

    def to_dict(self) -> dict:
        return {
            'id': self.id.id if self.id else None,
            'name': self.name,
            'price': self.price,
            'quantity': self.quantity
        }