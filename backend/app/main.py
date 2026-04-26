"""FastAPI main application."""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes import auth, vendedores, balance

app = FastAPI(
    title="Congroup Analytics API",
    version="2.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(vendedores.router, prefix="/api/vendedores", tags=["vendedores"])
app.include_router(balance.router, prefix="/api/balance", tags=["balance"])


@app.get("/api/health")
def health_check():
    return {"status": "ok"}

# Serve frontend static files (production build)
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.isdir(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
