from pydantic import BaseModel

from typing import Optional


class Supplier(BaseModel):
    name: str
    email: str
    address: str


class Proposal(BaseModel):
    supplier_name: str
    contact_name: str
    price_per_unit: float
    price_currency: str
    minimum_order_quantity: float
    country_of_origin: str
    payment_terms: str
    certifications: list[str]


class ProposalEmail(BaseModel):
    rfp_name: str
    from_address: str
    text: str
