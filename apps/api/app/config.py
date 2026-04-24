from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+psycopg://forge:forge@localhost:5432/forge"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Object Storage
    R2_ENDPOINT: str = "http://localhost:9000"
    R2_ACCESS_KEY: str = ""
    R2_SECRET_KEY: str = ""
    R2_BUCKET: str = "forge-assets"

    # Anthropic
    ANTHROPIC_API_KEY: str = ""

    # Marketplace APIs
    ETSY_API_KEY: str = ""
    SHOPIFY_API_KEY: str = ""
    SHOPIFY_STORE_URL: str = ""

    # 3D Generation
    MESHY_API_KEY: str = ""

    # Shipping
    SHIPPO_API_KEY: str = ""

    # Auth
    RESEND_API_KEY: str = ""
    OPERATOR_EMAIL: str = ""
    SECRET_KEY: str = "change-me-in-production"

    # Shop
    SHOP_NAME: str = "Forge Prints"

    # Environment
    ENV: str = "development"
    LOG_LEVEL: str = "INFO"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
