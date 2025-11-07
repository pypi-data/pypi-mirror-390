# -*- coding: utf-8 -*-

"""Data models for Service Parameter (SP) operations."""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass
from ..common import Result, DEFAULT_HTTP_TIMEOUT, DEFAULT_CACHE_TTL


@dataclass
class ServiceParameter:
    """Service parameter definition."""
    
    id: str
    description: str
    possible_values: Optional[str] = None


@dataclass
class ServiceParameterValue:
    """Service parameter value for a specific account."""
    
    id: int
    value: str
    account_id: str


# Use common Result class for consistency
SPResult = Result


class SPConfig:
    """Configuration for SP operations."""
    
    # GitLab API settings - use environment variable or default
    # Note: BASE_URL should include /api/v4
    GITLAB_BASE_URL = os.environ.get("SP_GITLAB_BASE_URL", "https://git.example.com/api/v4")
    GITLAB_PROJECT_ID = os.environ.get("SP_GITLAB_PROJECT_ID", "24890")
    GITLAB_FILE_PATH = "assembly.json"
    GITLAB_BRANCH = "master"
    
    # Internal API settings
    INTAPI_BASE_URL = os.environ.get(
        "SP_INTAPI_BASE_URL", 
        "http://intapi.example.com:8082"
    )
    INTAPI_AUTH_HEADER = os.environ.get(
        "SP_INTAPI_AUTH_HEADER",
        "IntApp your-auth-header-here"
    )
    INTAPI_BRAND_ID = os.environ.get("SP_INTAPI_BRAND_ID", "1210")
    
    # Request settings - use common constants
    DEFAULT_TIMEOUT = DEFAULT_HTTP_TIMEOUT
    CACHE_TTL = DEFAULT_CACHE_TTL
    
    # Display settings
    MAX_DESCRIPTION_LENGTH = 80
    SEARCH_RESULTS_LIMIT = 20
