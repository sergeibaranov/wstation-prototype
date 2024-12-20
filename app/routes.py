from fastapi import APIRouter, Request
import datastore
import langmodel
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


@routes.post("/proposal_emails")
async def insert_supplier(
    request: Request,
    email: models.ProposalEmail,
):
    ds: datastore.Client = request.app.state.datastore
    lm: langmodel.LangModelClient = request.app.state.langmodel
    proposal = await lm.ingest_proposal(email.text)
    await ds.insert_proposal(proposal, email.rfp_name, email.from_address)
    return {"result": proposal}
