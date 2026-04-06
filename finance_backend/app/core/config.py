import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


@dataclass
class Settings:
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./finance.db")

    @property
    def sqlalchemy_database_url(self) -> str:
        if self.database_url.startswith("sqlite:///./"):
            db_name = self.database_url.replace("sqlite:///./", "", 1)
            project_dir = Path(__file__).resolve().parents[2]
            return f"sqlite:///{(project_dir / db_name).as_posix()}"
        return self.database_url


settings = Settings()
