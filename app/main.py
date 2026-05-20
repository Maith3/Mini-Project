from fastapi import FastAPI

from app.routes.auth_routes import router as auth_router
from app.routes.prediction_routes import router as prediction_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(prediction_router)