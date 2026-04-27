from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'SentinelForge API'
    environment: str = 'dev'
    debug: bool = False
    api_prefix: str = '/api/v1'
    allowed_origins: str = '*'
    api_key: str = Field(default='', alias='API_KEY')

    database_url: str = Field(default='sqlite:///./sentinelforge.db', alias='DATABASE_URL')
    redis_url: str = Field(default='redis://localhost:6379/0', alias='REDIS_URL')
    neo4j_uri: str = Field(default='bolt://localhost:7687', alias='NEO4J_URI')
    neo4j_user: str = Field(default='neo4j', alias='NEO4J_USER')
    neo4j_password: str = Field(default='neo4jpassword', alias='NEO4J_PASSWORD')


settings = Settings()
