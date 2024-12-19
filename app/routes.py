from fastapi import APIRouter, Request
import datastore
import models

routes = APIRouter()


@routes.get("/")
async def root():
    return {"message": "Hello World"}


@routes.get("/suppliers")
async def list_suppliers(request: Request):
    ds: datastore.Client = request.app.state.datastore
    results = await ds.list_suppliers()
    return {"results": results}


@routes.post("/suppliers/insert")
async def insert_supplier(
    request: Request,
    supplier: models.Supplier,
):
    ds: datastore.Client = request.app.state.datastore
    results = await ds.insert_supplier(supplier)
    return results
