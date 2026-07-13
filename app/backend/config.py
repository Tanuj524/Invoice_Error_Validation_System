from pydantic_settings import BaseSettings,SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    SQLALCHEMY_DATABASE_URL:str
    JWT_SECRET:str
    ALGORITHM:str
    ACCESS_TOKEN_EXPIRE_MINUTES:int
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    
    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]
    

settings=Settings()

