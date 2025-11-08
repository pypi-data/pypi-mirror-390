import os
class Settings:

    # Database URL
    DATABASE_URL: str = os.getenv("DATABASE_URL")

    DB_USER: str = os.getenv("DB_USER")
    DB_HOST: str = os.getenv("DB_HOST")
    DB_NAME: str = os.getenv("DB_NAME")
    DB_PORT: str = os.getenv("DB_PORT")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")

    # Application settings
    APP_NAME: str = os.getenv("APP_NAME", "Python Template API")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true",1)
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    
    # Logging settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "detailed")  # detailed, json, simple
    LOG_TO_FILE: bool = os.getenv("LOG_TO_FILE", "False").lower() in ("true", 1)
    LOG_MAX_SIZE: int = int(os.getenv("LOG_MAX_SIZE", "10485760"))  # 10MB
    LOG_BACKUP_COUNT: int = int(os.getenv("LOG_BACKUP_COUNT", "5"))
    LOG_DIR: str = os.getenv("LOG_DIR", "logs")
        
   # Security settings
    ENVIRONMENT: str = os.getenv("ENVIRONMENT")
    ALGORITHM: str = os.getenv("ALGORITHM")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))
    
    # =============================================================================
    # SHARED TABLES (main schema)
    # =============================================================================
    MAIN_TENANTS_TABLE = os.getenv("MAIN_TENANTS_TABLE")
    MAIN_ROLE_PERMISSIONS_TABLE = os.getenv("MAIN_ROLE_PERMISSIONS_TABLE")
    MAIN_USER_SUBSCRIPTIONS_TABLE = os.getenv("MAIN_USER_SUBSCRIPTIONS_TABLE")
    MAIN_USER_SUBSCRIPTION_HISTORY_TABLE = os.getenv("MAIN_USER_SUBSCRIPTION_HISTORY_TABLE")
    MAIN_SUBSCRIPTIONS_TABLE = os.getenv("MAIN_SUBSCRIPTIONS_TABLE")

    # =============================================================================
    # TENANT-SPECIFIC TABLES (tenant schemas)
    # =============================================================================
    TENANT_LOGIN_SETTINGS_TABLE = os.getenv("TENANT_LOGIN_SETTINGS_TABLE")
    TENANT_ASSIGN_ROLES_TABLE = os.getenv("TENANT_ASSIGN_ROLES_TABLE")
    TENANT_USER_GROUPS_TABLE = os.getenv("TENANT_USER_GROUPS_TABLE")

    @property
    def database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL

        port = int(self.DB_PORT) if self.DB_PORT else 5432
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{port}/{self.DB_NAME}"

# Global settings instance
db_settings = Settings()