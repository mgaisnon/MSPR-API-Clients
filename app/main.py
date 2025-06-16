from fastapi import FastAPI, APIRouter
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="PayeTonKawa - API Clients")
Instrumentator().instrument(app).expose(app)

router = APIRouter(prefix="/clients")

@router.get("/health")
async def health_check():
    return {"status": "ok"}

@router.get("/")
async def get_clients():
    return {"message": "Clients API is running"}

app.include_router(router)
