# config.py — central place for all application settings
#
# WHY a dedicated config file?
#   If we scattered os.getenv("SECRET_KEY") calls across multiple files,
#   we'd have to hunt them all down whenever we want to change a setting.
#   Instead, we read everything ONCE here, and every other file just does:
#       from config import settings
#   That's one import, and all settings are available as typed attributes.
#
# HOW python-dotenv works:
#   load_dotenv() looks for a file named ".env" in the current directory
#   (or parent directories) and loads each KEY=VALUE line into the
#   process's environment variables — as if you'd set them in the shell.
#   After that, os.getenv("KEY") works normally.
#
#   If a variable is already set in the real environment (e.g. on a server),
#   load_dotenv() does NOT override it. This is the correct production behaviour.

import os
from dotenv import load_dotenv

# Load .env file into the environment.
# We call this ONCE here so it happens before any os.getenv() calls.
load_dotenv()

class Settings:
    """
    A simple container for all configuration values.

    WHY a class instead of module-level constants?
      A class lets us group related settings under one name ('settings.SECRET_KEY')
      which is cleaner than loose variables at the top of a file.
      It also makes it easy to add validation or defaults later.
    """

    # ── JWT ───────────────────────────────────────────────────────────────────

    # The secret key used to sign tokens. Read from .env.
    # We provide a fallback ("...") only so the app doesn't crash if .env is
    # missing during testing — but in practice .env must always be present.
    SECRET_KEY: str = os.getenv("SECRET_KEY", "fallback-insecure-secret")

    # The signing algorithm. HS256 is standard for single-server APIs.
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")

    # Token lifetime in minutes. int() converts the string from .env to a number.
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
    )


# Create a single shared instance.
# Every other file imports this ONE object:  from config import settings
settings = Settings()
