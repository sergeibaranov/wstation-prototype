from fastapi import APIRouter

routes = APIRouter()

@routes.get("/")
async def root():
    return {"message": "Hello World"}
