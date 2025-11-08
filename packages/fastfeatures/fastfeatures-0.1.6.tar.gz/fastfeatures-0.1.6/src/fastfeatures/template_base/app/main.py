from contextlib import asynccontextmanager

from app import features
from app.core.settings import settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastfeatures import add_features_routes


@asynccontextmanager
async def life_span(app: FastAPI):
    print(f"Server is starting ...")
    yield
    print(f"Server has been stopped.")


app = FastAPI(
    title="{%PROJECT_NAME%}",
    version="0.1.0",
    description="{%PROJECT_DESCRIPTION%}",
    lifespan=life_span,
)

# Add middleware to prevent CORS issues
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    """
    Root endpoint for the {%PROJECT_NAME%}} API.
    """
    return {"message": "Welcome to {%PROJECT_NAME%}} API"}


add_features_routes(app, features)
