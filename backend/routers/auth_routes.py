# routers/auth_routes.py — signup and login routes
#
# WHY a separate router file?
#   FastAPI lets us split routes into "routers" — mini-apps that handle
#   one area of the API. This file owns everything auth-related.
#   main.py then "mounts" this router under the /auth prefix, so all
#   routes here automatically become /auth/signup, /auth/login, etc.
#
# WHAT'S IN THIS FILE (top to bottom):
#   1. Imports
#   2. Pydantic schemas  — describe the shape of request/response bodies
#   3. Helper functions  — hash_password, verify_password, create_access_token
#   4. The router object
#   5. POST /signup
#   6. POST /login

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from models import User


# ═════════════════════════════════════════════════════════════════════════════
# 1. PYDANTIC SCHEMAS
# ═════════════════════════════════════════════════════════════════════════════
#
# WHY Pydantic?
#   FastAPI uses Pydantic to automatically:
#   • Parse the incoming JSON request body into a Python object
#   • Validate that required fields are present and correctly typed
#   • Return a clear error message if validation fails (before our code runs)
#
# A Pydantic model is just a class that inherits from BaseModel.
# Each attribute = one field in the expected JSON.

class SignupRequest(BaseModel):
    """
    The JSON body we expect for POST /auth/signup.
    Example:  { "email": "alice@example.com", "password": "secret123" }
    """
    # EmailStr: Pydantic validates that this is a properly formatted email.
    # If the client sends "notanemail", Pydantic rejects it before our code runs.
    email: EmailStr

    # str: any non-empty string. We don't enforce a minimum length here to keep
    # it simple — add min_length=8 later when hardening for production.
    password: str


class LoginRequest(BaseModel):
    """
    The JSON body we expect for POST /auth/login.
    Same shape as SignupRequest — separate class so they can diverge later
    (e.g. login might accept a username instead of email someday).
    """
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """
    The JSON body we send BACK after a successful signup or login.
    Example:  { "access_token": "eyJ...", "token_type": "bearer" }

    WHY "token_type": "bearer"?
      "Bearer" is an HTTP standard. It tells the client how to use the token:
      include it in the Authorization header as:  Bearer <token>
      Most frontend libraries and API clients understand this convention.
    """
    access_token: str
    token_type: str = "bearer"   # always "bearer" — the default is correct


# ═════════════════════════════════════════════════════════════════════════════
# 2. PASSWORD HASHING HELPERS
# ═════════════════════════════════════════════════════════════════════════════
#
# CryptContext is passlib's main object. It:
#   • Knows which hashing algorithm to use (bcrypt here)
#   • Handles the full hash/verify cycle for us
#
# WHY bcrypt?
#   bcrypt is intentionally SLOW — it's designed to take ~100ms per hash.
#   This makes brute-force attacks impractical: an attacker trying a million
#   passwords would need ~100,000 seconds. Regular password checking is barely
#   affected because we only check once per login.
#
# schemes=["bcrypt"]   → use bcrypt as the only accepted algorithm
# deprecated="auto"    → if we ever add a new algorithm, old hashes are
#                        automatically flagged as "needs rehashing"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """
    Takes a plain-text password and returns its bcrypt hash.

    Example:
        hash_password("secret123")
        → "$2b$12$eImiTXuWVxfM37uY4JANjQ..."  (always different due to random salt)

    WHY is the output always different for the same input?
        bcrypt adds a random "salt" before hashing. This means two users with
        the same password get completely different hashes — so an attacker
        can't use a pre-computed table of known hashes (a "rainbow table").
    """
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Checks whether a plain-text password matches a stored bcrypt hash.
    Returns True if they match, False otherwise.

    WHY not just re-hash and compare?
        Because bcrypt's salt is embedded IN the hash string. passlib reads
        the salt out of the stored hash, re-hashes the plain password with
        THAT same salt, then compares. We never need to store the salt separately.
    """
    return pwd_context.verify(plain_password, hashed_password)


# ═════════════════════════════════════════════════════════════════════════════
# 3. JWT TOKEN HELPER
# ═════════════════════════════════════════════════════════════════════════════
#
# A JWT (JSON Web Token) has three parts, separated by dots:
#   header.payload.signature
#
#   • header   : metadata — algorithm used (HS256)
#   • payload  : the actual data we store ("sub": user email, "exp": expiry time)
#   • signature: HMAC of header+payload using our SECRET_KEY
#
# The signature is the security guarantee. Anyone can READ a JWT (it's just
# Base64-encoded JSON), but only we can CREATE a valid signature because only
# we know SECRET_KEY. If someone tampers with the payload, the signature won't
# match and we reject the token.

def create_access_token(data: dict) -> str:
    """
    Creates and returns a signed JWT string.

    'data' is a dict of claims to embed in the token.
    We always add an 'exp' (expiration) claim before signing.

    Example:
        create_access_token({"sub": "alice@example.com"})
        → "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbGljZUBleGFtcGxlLmNvbSIsImV4cCI6...}"
    """
    # Copy the data so we don't mutate the caller's dict
    payload = data.copy()

    # Calculate the exact moment this token expires.
    # datetime.utcnow() gives the current UTC time.
    # timedelta(minutes=...) creates a duration we add to "now".
    expire = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    # "exp" is a standard JWT claim. python-jose automatically checks it
    # when decoding — if the current time is past exp, decoding raises an error.
    payload.update({"exp": expire})

    # jwt.encode() serialises the payload dict to JSON, Base64-encodes it,
    # then computes and appends the HMAC-SHA256 signature.
    # The result is the compact "header.payload.signature" string.
    encoded_token = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_token


# ═════════════════════════════════════════════════════════════════════════════
# 4. HOW JWT VERIFICATION WILL WORK FOR PROTECTED ROUTES (preview)
# ═════════════════════════════════════════════════════════════════════════════
#
# When we build protected routes later, we'll add a function like this:
#
#   from fastapi.security import OAuth2PasswordBearer
#   oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
#
#   def get_current_user(
#       token: str = Depends(oauth2_scheme),   # FastAPI extracts the token
#       db: Session = Depends(get_db)
#   ):
#       try:
#           payload = jwt.decode(
#               token,
#               settings.SECRET_KEY,
#               algorithms=[settings.ALGORITHM]
#           )
#           email = payload.get("sub")         # "sub" = the user email we stored
#       except JWTError:
#           raise HTTPException(status_code=401, detail="Invalid or expired token")
#
#       user = db.query(User).filter(User.email == email).first()
#       if user is None:
#           raise HTTPException(status_code=401, detail="User not found")
#       return user
#
# Then a protected route looks like this:
#
#   @router.get("/me")
#   def get_me(current_user: User = Depends(get_current_user)):
#       return {"email": current_user.email}
#
# FastAPI calls get_current_user() automatically before the route runs.
# If the token is missing/expired/tampered → 401 is returned automatically.
# If valid → the route gets the user object directly.


# ═════════════════════════════════════════════════════════════════════════════
# 5. ROUTER
# ═════════════════════════════════════════════════════════════════════════════
#
# APIRouter() is FastAPI's way of creating a mini-app.
# Routes defined on 'router' get mounted in main.py under a prefix (/auth).
# The 'tags' list controls grouping in the /docs Swagger UI.

router = APIRouter()


# ═════════════════════════════════════════════════════════════════════════════
# 6. POST /auth/signup
# ═════════════════════════════════════════════════════════════════════════════

@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """
    Register a new user account.

    Steps:
      1. Check the email isn't already taken → 400 if it is
      2. Hash the password
      3. Save the new User row to the database
      4. Return a JWT token (user is immediately logged in)

    'request: SignupRequest'
        FastAPI reads the JSON body and validates it against SignupRequest.
        If 'email' or 'password' is missing/malformed, FastAPI returns 422
        automatically before this function is even called.

    'db: Session = Depends(get_db)'
        FastAPI calls get_db() before this function runs, opens a DB session,
        passes it in as 'db', and closes it when this function returns.
        We never open or close the session manually.
    """

    # ── Step 1: Check for duplicate email ────────────────────────────────────
    #
    # db.query(User)           → start a SELECT query on the "users" table
    # .filter(User.email == request.email)  → add a WHERE clause
    # .first()                 → fetch the first matching row, or None
    #
    # WHY check here AND rely on unique=True in the model?
    #   The unique constraint in the DB is the ultimate safety net.
    #   But catching it here lets us return a friendly 400 message instead
    #   of a raw database IntegrityError (which would cause a 500 response).

    existing_user = db.query(User).filter(User.email == request.email).first()

    if existing_user:
        # HTTPException tells FastAPI to stop and return an error response.
        # status_code=400: "Bad Request" — the client sent invalid data.
        # detail: the human-readable message in the response body.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # ── Step 2: Hash the password ─────────────────────────────────────────────
    hashed = hash_password(request.password)

    # ── Step 3: Create and save the User ─────────────────────────────────────
    #
    # Creating a User instance does NOT write to the database yet.
    # db.add(new_user)    → stages the INSERT (like git add)
    # db.commit()         → executes the INSERT and makes it permanent (like git commit)
    # db.refresh(new_user) → re-reads the row from DB so 'new_user.id' and
    #                        'new_user.created_at' are populated (the DB fills these in)

    new_user = User(email=request.email, hashed_password=hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # ── Step 4: Create and return the JWT ────────────────────────────────────
    #
    # "sub" stands for "subject" — it's a standard JWT claim meaning
    # "who this token represents". We use the email as the identifier
    # because it's unique and we'll use it to look up the user later.

    token = create_access_token({"sub": new_user.email})
    return TokenResponse(access_token=token)


# ═════════════════════════════════════════════════════════════════════════════
# 7. POST /auth/login
# ═════════════════════════════════════════════════════════════════════════════

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate an existing user and return a JWT token.

    Steps:
      1. Look up the user by email → 401 if not found
      2. Verify the submitted password against the stored hash → 401 if wrong
      3. Return a fresh JWT token

    WHY return 401 (Unauthorized) for BOTH "user not found" AND "wrong password"
    with the SAME message ("Invalid credentials")?
      Security best practice: if we returned "user not found" vs "wrong password"
      separately, an attacker could enumerate which emails are registered in our
      system just by trying different emails. By using the same message for both
      failure cases, we reveal nothing about whether the email exists.
    """

    # ── Step 1: Look up user by email ────────────────────────────────────────
    user = db.query(User).filter(User.email == request.email).first()

    # ── Step 2: Verify password ───────────────────────────────────────────────
    #
    # WHY check both conditions before raising the error?
    #   We check 'not user' and 'not verify_password(...)' in one if-block.
    #   If the user doesn't exist, we still call verify_password with a dummy
    #   hash — actually, we short-circuit with 'or', so if 'not user' is True,
    #   verify_password is never called. Python's 'or' is lazy.
    #
    # The important thing: both failures produce IDENTICAL 401 responses.

    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            # WWW-Authenticate header is part of the HTTP standard for auth errors.
            # It tells clients what authentication scheme is expected.
            headers={"WWW-Authenticate": "Bearer"},
        )

    # ── Step 3: Issue a fresh token ───────────────────────────────────────────
    token = create_access_token({"sub": user.email})
    return TokenResponse(access_token=token)
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from database import get_db
from config import settings
from models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user
