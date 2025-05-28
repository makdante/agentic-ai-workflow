#config/api_config.py
"""
API configuration for external services.
Handles OpenAI GPT-4o, GitHub, and Google Cloud API settings.
"""

from dataclasses import dataclass
from typing import Dict, Optional

from config.settings import get_settings

settings = get_settings()


@dataclass
class OpenAIConfig:
    """OpenAI GPT-4o API configuration."""
    
    api_key: str
    model: str = "gpt-4o"
    max_tokens: int = 4096
    temperature: float = 0.1
    timeout: int = 60
    max_retries: int = 3
    requests_per_minute: int = 50
    
    @property
    def headers(self) -> Dict[str, str]:
        """Get HTTP headers for OpenAI API requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": f"{settings.app_name}/{settings.app_version}"
        }
    
    @property
    def rate_limit_config(self) -> Dict[str, int]:
        """Get rate limiting configuration."""
        return {
            "requests_per_minute": self.requests_per_minute,
            "tokens_per_minute": 200000,  # GPT-4o rate limit
            "requests_per_day": 10000
        }


@dataclass
class GitHubConfig:
    """GitHub API configuration."""
    
    token: str
    api_base_url: str = "https://api.github.com"
    timeout: int = 30
    max_retries: int = 3
    requests_per_hour: int = 5000
    
    @property
    def headers(self) -> Dict[str, str]:
        """Get HTTP headers for GitHub API requests."""
        return {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": f"{settings.app_name}/{settings.app_version}"
        }
    
    @property
    def rate_limit_config(self) -> Dict[str, int]:
        """Get rate limiting configuration."""
        return {
            "requests_per_hour": self.requests_per_hour,
            "core_limit": 5000,
            "search_limit": 30
        }


@dataclass
class GitHubMCPConfig:
    """GitHub MCP Server configuration."""
    
    server_url: str
    token: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    
    @property
    def headers(self) -> Dict[str, str]:
        """Get HTTP headers for MCP Server requests."""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": f"{settings.app_name}/{settings.app_version}"
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers


@dataclass
class GoogleCloudConfig:
    """Google Cloud API configuration."""
    
    project_id: Optional[str]
    credentials_path: Optional[str]
    region: str = "us-central1"
    timeout: int = 60
    
    @property
    def is_configured(self) -> bool:
        """Check if Google Cloud is properly configured."""
        return bool(self.project_id and self.credentials_path)


class APIConfigManager:
    """Centralized API configuration manager."""
    
    def __init__(self):
        self._openai_config = None
        self._github_config = None
        self._github_mcp_config = None
        self._google_cloud_config = None
    
    @property
    def openai(self) -> OpenAIConfig:
        """Get OpenAI configuration."""
        if self._openai_config is None:
            self._openai_config = OpenAIConfig(
                api_key=settings.openai_api_key,
                requests_per_minute=settings.openai_requests_per_minute
            )
        return self._openai_config
    
    @property
    def github(self) -> GitHubConfig:
        """Get GitHub configuration."""
        if self._github_config is None:
            self._github_config = GitHubConfig(
                token=settings.github_personal_access_token,
                requests_per_hour=settings.github_requests_per_hour
            )
        return self._github_config
    
    @property
    def github_mcp(self) -> GitHubMCPConfig:
        """Get GitHub MCP Server configuration."""
        if self._github_mcp_config is None:
            self._github_mcp_config = GitHubMCPConfig(
                server_url=settings.github_mcp_server_url,
                token=settings.github_mcp_server_token
            )
        return self._github_mcp_config
    
    @property
    def google_cloud(self) -> GoogleCloudConfig:
        """Get Google Cloud configuration."""
        if self._google_cloud_config is None:
            self._google_cloud_config = GoogleCloudConfig(
                project_id=settings.google_cloud_project,
                credentials_path=settings.google_application_credentials
            )
        return self._google_cloud_config
    
    def validate_configurations(self) -> Dict[str, bool]:
        """
        Validate all API configurations.
        
        Returns:
            Dict mapping service names to validation status
        """
        validations = {}
        
        # Validate OpenAI
        try:
            validations["openai"] = bool(self.openai.api_key)
        except Exception:
            validations["openai"] = False
        
        # Validate GitHub
        try:
            validations["github"] = bool(self.github.token)
        except Exception:
            validations["github"] = False
        
        # Validate GitHub MCP
        try:
            validations["github_mcp"] = bool(self.github_mcp.server_url)
        except Exception:
            validations["github_mcp"] = False
        
        # Validate Google Cloud
        try:
            validations["google_cloud"] = self.google_cloud.is_configured
        except Exception:
            validations["google_cloud"] = False
        
        return validations


# Global API configuration manager
api_config = APIConfigManager()