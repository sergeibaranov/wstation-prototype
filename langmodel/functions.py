def add_proposal_to_database(
    supplier_name: str,
    contact_name: str,
    price_per_unit: float,
    price_currency: str,
    minimum_order_quantity: float,
    country_of_origin: str,
    payment_terms: str,
    certifications: list[str],
):
    """Add a proposal to the database.

    Args:
        supplier_name: Name of the supplier. Pass 'Unknown' if information is not provided.
        contact_name: Name of the contact person. Pass 'Unknown' if information is not provided.
        price_per_unit: Price per unit of goods (e.g. pound or ton) in any currency. Pass 0 if information is not provided.
        price_currency: Currency of the price (USD, EUR, etc). Pass 'Unknown' if information is not provided.
        minumum_order_quantity: Minimum order quantity. Pass 0 if information is not provided.
        country_of_origin: Country of origin without state or city. Pass 'Unknown' if information is not provided.
        payment_terms: Payment terms, for example 'Net 30' or 'Net 60'. Pass 'Unknown' if information is not provided.
        certifications: Array of certifications names.

    Returns:
        None
    """
    pass
