from fastapi import FastAPI

from app.database import Base, engine

from app.models.employee import Employee
from app.models.user import User

from app.routes.auth import router as auth_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FaceAI API",
    version="1.0.0"
)

app.include_router(auth_router)


@app.get("/")
def root():
    return {
        "status": "success",
        "message": "FaceAI Backend Running 🚀"
    }