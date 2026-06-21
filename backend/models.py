# models.py — SQLAlchemy table definitions
#
# WHY a separate models file?
#   SQLAlchemy uses Python classes to represent database tables.
#   Each class = one table. Each class attribute = one column.
#   Keeping them here (separate from business logic) makes the
#   schema easy to find and change.
#
# HOW it works:
#   Every model class must:
#     1. Inherit from Base (imported from database.py)
#     2. Have a __tablename__ (the actual SQL table name)
#     3. Have at least one Column marked as primary_key=True
#
# When main.py calls Base.metadata.create_all(engine), SQLAlchemy
# reads all classes that inherit from Base and creates the matching
# SQL tables in the database — IF they don't already exist.
#
# ─────────────────────────────────────────────────────────────────
# Models in this file:
#   • User    — stores registered accounts (email + hashed password)
#
# Future models to add:
#   • Dataset — uploaded CSV files
#   • MLModel — trained model metadata
# ─────────────────────────────────────────────────────────────────

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, ForeignKey

from database import Base


# ── User model ────────────────────────────────────────────────────────────────
#
# This class maps to a table called "users" in mlforge.db.
# Each instance of this class = one row in that table.

class User(Base):
    __tablename__ = "users"

    # ── id ────────────────────────────────────────────────────────────────────
    # Integer: stored as a whole number (1, 2, 3, …).
    # primary_key=True: uniquely identifies each row. No two users share an id.
    # index=True: SQLite builds an internal lookup table for this column so
    #   queries like "find user where id=5" run fast even with millions of rows.
    id = Column(Integer, primary_key=True, index=True)

    # ── email ─────────────────────────────────────────────────────────────────
    # String: stored as text.
    # unique=True: the database itself rejects duplicate emails at the DB level,
    #   not just at the Python level. This is the safest guarantee.
    # nullable=False: the database will refuse to insert a row with no email.
    # index=True: we'll frequently look users up by email (login, duplicate check)
    #   so an index here makes those queries fast.
    email = Column(String, unique=True, nullable=False, index=True)

    # ── hashed_password ───────────────────────────────────────────────────────
    # WHY store a hash and NOT the real password?
    #   If the database is ever leaked, attackers get gibberish instead of
    #   real passwords. bcrypt hashes are designed to be slow to crack.
    #   We NEVER store or log the plain-text password anywhere.
    hashed_password = Column(String, nullable=False)

    # ── created_at ────────────────────────────────────────────────────────────
    # DateTime: stores a date+time value.
    # default=datetime.utcnow: when a new User row is inserted and no created_at
    #   is given, SQLAlchemy calls datetime.utcnow() automatically and uses the
    #   result. Note: we pass the FUNCTION (utcnow), not the RESULT (utcnow()).
    #   If we wrote utcnow() with parentheses, every user would get the SAME
    #   timestamp (the time the file was imported). Without parentheses, it's
    #   called fresh for every new row.
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        # __repr__ controls what Python shows when you print a User object.
        # Useful for debugging. We intentionally exclude hashed_password.
        return f"<User id={self.id} email={self.email!r}>"
class Dataset(Base):
    __tablename__ = "datasets"

    id          = Column(Integer, primary_key=True, index=True)
    owner_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename    = Column(String, nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow)
class Experiment(Base):
    __tablename__ = "experiments"

    id              = Column(Integer, primary_key=True, index=True)
    owner_id        = Column(Integer, ForeignKey("users.id"), nullable=False)
    dataset_id      = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    target_column   = Column(String, nullable=False)
    results         = Column(String, nullable=False)  # JSON string of all 4 model scores
    created_at      = Column(DateTime, default=datetime.utcnow)