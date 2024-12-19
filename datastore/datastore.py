import asyncio
from datetime import datetime
from ipaddress import IPv4Address, IPv6Address
from typing import Any, Literal, Optional

import asyncpg
import models
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


class Config(BaseModel):
    kind: Literal["postgres"]
    host: IPv4Address | IPv6Address = IPv4Address("127.0.0.1")
    port: int = 5432
    user: str
    password: str
    database: str


class Client:
    __async_engine: AsyncEngine

    def __init__(self, async_engine: AsyncEngine):
        self.__async_engine = async_engine

    @classmethod
    async def create(cls, config: Config) -> "Client":
        async def getconn() -> asyncpg.Connection:
            conn: asyncpg.Connection = await asyncpg.connection.connect(
                host=str(config.host),
                user=config.user,
                password=config.password,
                database=config.database,
                port=config.port,
            )
            return conn

        async_engine = create_async_engine(
            "postgresql+asyncpg://",
            async_creator=getconn,
        )
        if async_engine is None:
            raise TypeError("async_engine not instantiated")
        return cls(async_engine)

    async def initialize_tables(self) -> None:
        async with self.__async_engine.connect() as conn:
            # Create Proposals table if not exists already
            await conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS proposals(
                      id serial PRIMARY KEY,
                      supplier_name TEXT,
                      contact_name TEXT,
                      country_of_origin TEXT,
                      price_per_unit NUMERIC
                    )
                    """
                )
            )
            # Create Suppliers table if not exists already
            await conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS suppliers(
                      id serial PRIMARY KEY,
                      name TEXT,
                      email TEXT,
                      address TEXT
                    )
                    """
                )
            )
            await conn.commit()

    async def insert_supplier(
        self,
        supplier: models.Supplier,
    ):
        async with self.__async_engine.connect() as conn:
            s = text(
                """
                INSERT INTO suppliers (
                    name,
                    email,
                    address
                ) VALUES (
                    :name,
                    :email,
                    :address
                );
                """
            )
            params = {
                "name": supplier.name,
                "email": supplier.email,
                "address": supplier.address,
            }
            result = (await conn.execute(s, params)).mappings()
            await conn.commit()
            if not result:
                raise Exception("Supplier Insertion failure")

    async def list_suppliers(self) -> list[models.Supplier]:
        async with self.__async_engine.connect() as conn:
            s = text("SELECT * FROM suppliers;")

            results = (await conn.execute(s)).mappings().fetchall()

        return [models.Supplier.model_validate(r) for r in results]

    async def close(self):
        await self.__async_engine.dispose()
