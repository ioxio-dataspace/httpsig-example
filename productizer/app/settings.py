from pathlib import Path

from app.keys import RsaPrivateKey
from pydantic import BaseSettings


class Settings(BaseSettings):
    # For creating HTTP Message Signatures
    PRIVATE_KEY: RsaPrivateKey
    # Where to load public keys to verify HTTP Message Signatures
    HTTP_SIG_VERIFY_JWKS_URI: str = "http://127.0.0.1:8080/.well-known/jwks.json"

    class Config:
        env_file = Path(__file__).parent.parent / ".env"


conf = Settings()
