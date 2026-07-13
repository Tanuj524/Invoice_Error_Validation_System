from pydantic_settings import BaseSettings,SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    SQLALCHEMY_DATABASE_URL:str
    JWT_SECRET:str
    ALGORITHM:str
    ACCESS_TOKEN_EXPIRE_MINUTES:int
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    ENVIRONMENT:str = "development"
    FRONTEND_URL: str = "http://localhost:3000"

    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str        # your Gmail address
    SMTP_PASSWORD: str        # the 16-char app password
    SMTP_FROM_EMAIL: str      # usually same as SMTP_USERNAME
    SMTP_FROM_NAME: str = "Invoice Validation System"
    
    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]
    

settings=Settings()

