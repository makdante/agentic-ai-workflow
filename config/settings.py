#config/settings.py                                                                                                                                                                                                                                                                                         
"""
Central configuration management for the Agentic AI Workflow.
Handles environment variables, validation, and application settings.
"""

import os
from pathlib import Path
from typing import Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with validation and type hints."""
    
    # Application Configuration
    app_name: str = Field(default="Agentic AI Workflow", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # API Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    github_personal_access_token: str = Field(..., env="GITHUB_PERSONAL_ACCESS_TOKEN")
    
    # Google Cloud Configuration
    google_cloud_project: Optional[str] = Field(default=None, env="GOOGLE_CLOUD_PROJECT")
    google_application_credentials: Optional[str] = Field(
        default=None, env="GOOGLE_APPLICATION_CREDENTIALS"
    )
    
    # Database Configuration
    database_url: str = Field(
        default="sqlite:///data/database/agentic_workflow.db",
        env="DATABASE_URL"
    )
    database_pool_size: int = Field(default=10, env="DATABASE_POOL_SIZE")
    database_echo: bool = Field(default=False, env="DATABASE_ECHO")
    
    # GitHub MCP Server Configuration
    github_mcp_server_url: str = Field(
        default="http://localhost:3000", 
        env="GITHUB_MCP_SERVER_URL"
    )
    github_mcp_server_token: Optional[str] = Field(
        default=None, 
        env="GITHUB_MCP_SERVER_TOKEN"
    )
    
    # Repository Processing Configuration
    temp_repo_path: str = Field(
        default="data/temp/repositories", 
        env="TEMP_REPO_PATH"
    )
    max_repo_size_mb: int = Field(default=500, env="MAX_REPO_SIZE_MB")
    clone_timeout_seconds: int = Field(default=300, env="CLONE_TIMEOUT_SECONDS")
    
    # Rate Limiting Configuration
    openai_requests_per_minute: int = Field(
        default=50, 
        env="OPENAI_REQUESTS_PER_MINUTE"
    )
    github_requests_per_hour: int = Field(
        default=5000, 
        env="GITHUB_REQUESTS_PER_HOUR"
    )
    
    # Context Window Configuration
    max_context_length: int = Field(default=32000, env="MAX_CONTEXT_LENGTH")
    max_files_per_analysis: int = Field(default=100, env="MAX_FILES_PER_ANALYSIS")
    
    @validator("log_level")
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is one of the standard Python logging levels."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()
    
    @validator("database_url")
    def validate_database_url(cls, v: str) -> str:
        """Ensure database directory exists for SQLite."""
        if v.startswith("sqlite://"):
            db_path = v.replace("sqlite://", "")
            if not db_path.startswith("/"):  # Relative path
                db_dir = Path(db_path).parent
                db_dir.mkdir(parents=True, exist_ok=True)
        return v
    
    @validator("temp_repo_path")
    def validate_temp_repo_path(cls, v: str) -> str:
        """Ensure temporary repository path exists."""
        temp_path = Path(v)
        temp_path.mkdir(parents=True, exist_ok=True)
        return str(temp_path.absolute())
    
    @property
    def project_root(self) -> Path:
        """Get the project root directory."""
        return Path(__file__).parent.parent.parent
    
    @property
    def data_dir(self) -> Path:
        """Get the data directory path."""
        data_dir = self.project_root / "data"
        data_dir.mkdir(exist_ok=True)
        return data_dir
    
    @property
    def logs_dir(self) -> Path:
        """Get the logs directory path."""
        logs_dir = self.data_dir / "logs"
        logs_dir.mkdir(exist_ok=True)
        return logs_dir
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the application settings instance."""
    return settings