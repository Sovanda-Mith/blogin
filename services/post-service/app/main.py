from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import posts
from app.database import Base, engine
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Blogin Post Service",
    description="Blog post management service for Blogin",
    version="1.0.0",
    redirect_slashes=False,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    logger.info("Starting up Post Service...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Post Service...")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "post-service"}


app.include_router(posts.router, prefix="/posts")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
