from fastapi import FastAPI
from .routes import routes
from pydantic import BaseModel
from ipaddress import IPv4Address, IPv6Address
from typing import Optional
import yaml
import datastore
import langmodel
import vertexai
from contextlib import asynccontextmanager


class AppConfig(BaseModel):
    host: IPv4Address | IPv6Address = IPv4Address("127.0.0.1")
    port: int = 8080
    datastore: datastore.Config
    langmodel: langmodel.Config
    clientId: Optional[str] = None


def parse_config(path: str) -> AppConfig:
    with open(path, "r") as file:
        config = yaml.safe_load(file)
    return AppConfig(**config)


def gen_init(cfg: AppConfig):
    async def initialize_datastore(app: FastAPI):
        app.state.datastore = await datastore.Client.create(cfg.datastore)
        app.state.langmodel = await langmodel.LangModelClient.create(cfg.langmodel)
        yield
        await app.state.datastore.close()

    return asynccontextmanager(initialize_datastore)


def init_app(cfg: AppConfig) -> FastAPI:
    vertexai.init()
    app = FastAPI(lifespan=gen_init(cfg))
    app.state.client_id = cfg.clientId
    app.include_router(routes)
    return app
