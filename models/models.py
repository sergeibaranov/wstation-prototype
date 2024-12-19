from pydantic import BaseModel


class Supplier(BaseModel):
    name: str
    email: str
    address: str
