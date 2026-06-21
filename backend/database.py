# database.py — the single source of truth for our database connection
#
# WHY this file exists as a separate module:
#   Every router and every model needs to talk to the same database.
#   Centralising the connection here means we only configure it once,
#   and every other file just does: from database import Base, get_db

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# ── 1. Database URL ───────────────────────────────────────────────────────────
#
# SQLAlchemy needs a "connection string" to know WHERE the database lives
# and WHAT kind of database it is.
#
# Format: "dialect+driver://path-to-file"
#   • "sqlite:///"  tells SQLAlchemy we're using SQLite (a local file database)
#   • The path after "///" is where the .db file will be created/found
#
# os.path.dirname(__file__)  → the folder THIS file lives in  (backend/)
# os.path.join(..., "storage", "mlforge.db")  → backend/storage/mlforge.db
#
# Using an absolute path prevents surprises when the script is run from
# a different working directory.

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = "sqlite:///" + os.path.join(BASE_DIR, "storage", "mlforge.db")

# ── 2. Engine ─────────────────────────────────────────────────────────────────
#
# The "engine" is SQLAlchemy's low-level connection pool to the database.
# Think of it as the pipeline between Python and the .db file.
#
# connect_args={"check_same_thread": False}
#   SQLite normally raises an error if two different threads try to use
#   the same connection. FastAPI handles requests in threads, so we must
#   disable this check. It is safe here because SQLAlchemy manages the
#   sessions for us.

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# ── 3. SessionLocal ───────────────────────────────────────────────────────────
#
# A "session" is a single conversation with the database — you open it,
# run queries, commit changes, then close it.
#
# sessionmaker() creates a SESSION FACTORY (a class that produces sessions).
#   autocommit=False  → we manually commit, giving us control over transactions
#   autoflush=False   → SQLAlchemy won't automatically write pending changes
#                        to the DB before every query (avoids surprises)
#   bind=engine       → tells each session which engine (database) to use

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ── 4. Base ───────────────────────────────────────────────────────────────────
#
# All SQLAlchemy models (our table definitions) must inherit from Base.
# Base keeps a registry of every model class so that commands like
# Base.metadata.create_all(engine) can create ALL tables in one call.

Base = declarative_base()

# ── 5. get_db() — FastAPI dependency ─────────────────────────────────────────
#
# WHY a dependency function?
#   FastAPI's dependency injection system lets you declare that a route
#   "depends on" a database session. FastAPI will call get_db() before
#   the route runs, pass the session in, and guarantee cleanup afterwards.
#
# HOW it works (the yield pattern):
#   1. Code before  yield  →  runs BEFORE the route handler (opens session)
#   2. yield db            →  hands the session to the route handler
#   3. Code after   yield  →  runs AFTER the route handler (closes session)
#
# The try/finally ensures the session is ALWAYS closed, even if the route
# raises an exception — preventing connection leaks.

def get_db():
    db = SessionLocal()
    try:
        yield db        # hand the session to whoever asked for it
    finally:
        db.close()      # always clean up, no matter what happened above
