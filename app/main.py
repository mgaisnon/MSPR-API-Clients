from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="PayeTonKawa - API Clients")
Instrumentator().instrument(app).expose(app)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/clients")
async def get_clients():
    return {"message": "Clients API is running"}