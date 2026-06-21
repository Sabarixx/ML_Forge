# main.py — the entry point for the entire FastAPI application
#
# WHY this file?
#   Every FastAPI project needs ONE place where the app object is created
#   and all the pieces are wired together. This is that file.
#   When uvicorn starts the server, it looks for "main:app" —
#   meaning "the variable named 'app' inside main.py".

from fastapi import FastAPI
from database import engine, Base
from routers import auth_routes
from routers import experiment_routes
from fastapi.middleware.cors import CORSMiddleware
# ── Import all models so Base "sees" them ─────────────────────────────────────
#
# WHY import models here even though we don't use them directly?
#   SQLAlchemy's Base only knows about a model if that model's class has
#   been *imported* somewhere before create_all() is called.
#   If we skip this import, create_all() won't create any tables.
#
# As we add more model files (e.g. user models, dataset models),
# we'll add more import lines here.

import models  # noqa: F401  — "F401" silences the "imported but unused" warning

# ── Create the FastAPI app ─────────────────────────────────────────────────────
#
# FastAPI() creates the application instance.
#   title     → shows up in the auto-generated Swagger docs at /docs
#   version   → useful for API versioning later
#   description → a short blurb that also appears in /docs

app = FastAPI(
    title="MLForge API",
    version="0.1.0",
    description="A learning-focused ML platform backend built with FastAPI and SQLAlchemy.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allows any origin — fine for local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Create database tables on startup ─────────────────────────────────────────
#
# WHY call this here (at module load time)?
#   create_all() looks at every model that inherits from Base and creates
#   the corresponding SQL table in the database — IF it doesn't already exist.
#   Running it at startup means the DB is always in sync with our models,
#   without needing a separate migration step during development.
#
# In production you'd use Alembic (a migration tool) instead, but
# create_all() is perfect while we're learning and iterating quickly.

Base.metadata.create_all(bind=engine)

# ── Include routers ────────────────────────────────────────────────────────────
#
# app.include_router() mounts a router onto the main app.
#
#   router      → the APIRouter object defined inside auth_routes.py
#   prefix      → prepended to every route in that router
#                 e.g. prefix="/auth" + route "/signup" = /auth/signup
#   tags        → groups routes together in the /docs Swagger UI
#
# Future routers will be added the same way:
#   app.include_router(datasets.router, prefix="/datasets", tags=["Datasets"])

app.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])
from routers import datasets_routes
app.include_router(datasets_routes.router, prefix="/datasets", tags=["Datasets"])
app.include_router(experiment_routes.router, prefix="/experiments", tags=["Experiments"])
# ── Health check route ─────────────────────────────────────────────────────────
#
# WHY a health check?
#   It's the simplest possible route — no database, no auth, no logic.
#   It lets us verify the server is alive and responding before we test
#   anything more complex.
#
# @app.get("/")  is a decorator. It tells FastAPI:
#   "When someone sends a GET request to the URL '/', call the function below."
#
# FastAPI automatically converts the dict we return into a JSON response.

@app.get("/", tags=["Health"])
def health_check():
    """Returns a simple status message to confirm the server is running."""
    return {"status": "MLForge running", "version": "0.1.0"}
