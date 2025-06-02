from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env",),
        extra="allow",
    )

    WEAVIATE_HTTP_HOST: str
    WEAVIATE_HTTP_PORT: int
    WEAVIATE_GRPC_HOST: str
    WEAVIATE_GRPC_PORT: int
    GEMINI_API_KEY: str

    DEFAULT_DATA_DIR: str = "./data"
    DEFAULT_DOC_RETRIEVAL_NUM: int = 5


settings = Settings()
