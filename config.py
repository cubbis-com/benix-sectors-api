"""
Configuration module for Sectors API Middleware.
Loads variables from .env file and provides typed settings.
"""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# Base directory for the API folder
BASE_DIR = Path(__file__).resolve().parent

class Settings(BaseSettings):
    # Sectors API Settings
    SECTORS_API_KEY: str = Field(
        default="",
        description="Sectors Financial API Key (Insider Tier)"
    )
    SECTORS_BASE_URL: str = Field(
        default="https://api.sectors.app/v2",
        description="Base URL for Sectors Financial API v2"
    )
    SECTORS_MCP_URL: str = Field(
        default="https://sectors-mcp.supertype.ai/mcp",
        description="Streamable HTTP MCP Server URL"
    )

    # WhatsApp Reporting Gateway (for automated briefs and alerts)
    WA_GATEWAY_URL: str = Field(
        default="https://wa.inovasiuitjbt.uk/api/instances/6285717905851/send",
        description="WhatsApp sending endpoint"
    )
    WA_TOKEN: str = Field(
        default="",
        description="WhatsApp Gateway Bearer token"
    )
    WA_DEFAULT_TARGET: str = Field(
        default="6281805040354",
        description="Default WhatsApp destination number"
    )

    # Garda AI LLM Inference Settings (Gemma 4 via Inovasi UIT JBT)
    GARDA_API_URL: str = Field(
        default="https://iss-uitjbt.inovasiuitjbt.uk/garda-api/v1/chat/completions",
        description="Garda AI Chat Completions Endpoint"
    )
    GARDA_API_KEY: str = Field(
        default="",
        description="Garda API Bearer Key"
    )
    GARDA_MODEL: str = Field(
        default="gemma4:e4b",
        description="Garda LLM Model"
    )
    GARDA_TIMEOUT_SECONDS: float = Field(
        default=45.0,
        description="Garda LLM Timeout"
    )

    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ENVIRONMENT: str = "development"
    PROJECT_NAME: str = "BE.N.IX — Anvieo Trading Analytics"
    VERSION: str = "2.0.0"

    # Credit Shield & Cache TTLs (in seconds)
    CACHE_TTL_HELPERS: int = 86400    # 24 hours
    CACHE_TTL_REPORTS: int = 21600    # 6 hours
    CACHE_TTL_DAILY: int = 3600       # 1 hour
    CACHE_TTL_BROKERS: int = 1800     # 30 mins
    CACHE_TTL_DEFAULT: int = 3600     # 1 hour

    # Database Path (SQLite)
    DATABASE_PATH: str = str(BASE_DIR / "gateway.db")

    # Client Request Settings
    REQUEST_TIMEOUT_SECONDS: float = 25.0
    USER_AGENT: str = "SectorsPythonMiddleware/2.0.0 (FastAPI-Gateway)"

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
