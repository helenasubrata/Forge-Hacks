from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.find import router as find_router

app = FastAPI(title="Receipts API", description="Find real sources and check citations.")

# Lets the website (running on a different address) talk to this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(find_router)


@app.get("/")
def home():
    """Quick check that the API is running."""
    return {"status": "ok", "message": "Receipts API is running"}