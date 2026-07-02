from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_model_name: str = "gpt-4o"
    openai_max_tokens: int = 4096
    openai_temperature: float = 0.3
    github_token: str = ""
    review_max_retries: int = 3
    host: str = "0.0.0.0"
    port: int = 8000

    supported_languages: List[str] = [
        "python", "javascript", "typescript", "java", "go", "rust",
        "cpp", "csharp", "ruby", "php", "swift", "kotlin",
        "scala", "html", "css", "sql", "bash", "yaml", "json"
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
