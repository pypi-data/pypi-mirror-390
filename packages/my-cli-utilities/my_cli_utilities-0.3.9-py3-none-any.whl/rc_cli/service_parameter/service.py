# -*- coding: utf-8 -*-

"""Service Parameter (SP) client service for RC CLI."""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any
import httpx
from .models import ServiceParameter, ServiceParameterValue, SPResult, SPConfig
from ..common import handle_http_error, create_error_result
from my_cli_utilities_common.config import BaseConfig, SPConfig as UnifiedSPConfig
from my_cli_utilities_common.http_helpers import HTTPClientFactory

logger = logging.getLogger(__name__)


class SPClientError(Exception):
    """Base exception for SP client errors."""
    pass


class SPConnectionError(SPClientError):
    """Exception raised when connection to SP service fails."""
    pass


class SPNotFoundError(SPClientError):
    """Exception raised when requested resource is not found."""
    pass


class SPService:
    """Service for interacting with Service Parameter API."""
    
    def __init__(self):
        """Initialize SP service with configuration."""
        self.gitlab_token: Optional[str] = None
        self.timeout = SPConfig.DEFAULT_TIMEOUT
        self._cache: Dict[str, Any] = {}
        self._cache_ttl = SPConfig.CACHE_TTL
        
    def _get_gitlab_token(self) -> str:
        """Get GitLab token from environment variable."""
        token = os.environ.get('GITLAB_TOKEN')
        if not token:
            raise SPClientError(
                "GitLab token not found. Please set GITLAB_TOKEN environment variable."
            )
        return token
    
    async def get_all_service_parameters(self) -> SPResult:
        """
        Get all service parameter definitions from GitLab.
        
        Returns:
            SPResult containing all service parameters
        """
        try:
            # Validate configuration
            if SPConfig.GITLAB_BASE_URL == "https://git.example.com/api/v4":
                return SPResult(
                    success=False,
                    error_message=(
                        "GitLab URL not configured. Please set SP_GITLAB_BASE_URL environment variable.\n"
                        "Example: export SP_GITLAB_BASE_URL='https://git.example.com/api/v4'"
                    ),
                    count=0
                )
            
            # Get GitLab token if not already cached
            if not self.gitlab_token:
                self.gitlab_token = self._get_gitlab_token()
            
            url = f"{SPConfig.GITLAB_BASE_URL}/projects/{SPConfig.GITLAB_PROJECT_ID}/repository/files/{SPConfig.GITLAB_FILE_PATH}/raw"
            params = {"ref": SPConfig.GITLAB_BRANCH}
            headers = {"PRIVATE-TOKEN": self.gitlab_token}
            
            async with HTTPClientFactory.create_async_client(
                timeout=self.timeout,
                headers=headers
            ) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                assembly_data = response.json()
                service_parameters = assembly_data.get("service-parameters", {})
                
                logger.info(f"Retrieved {len(service_parameters)} service parameters")
                
                return SPResult(
                    success=True,
                    data=service_parameters,
                    count=len(service_parameters)
                )
                
        except Exception as e:
            error_msg = handle_http_error(
                e, 
                "retrieving service parameters",
                not_found_message="Service parameters not found in GitLab"
            )
            return create_error_result(SPResult, error_msg)
    
    async def get_service_parameter_value(self, sp_id: str, account_id: str) -> SPResult:
        """
        Get service parameter value for a specific account.
        
        Args:
            sp_id: Service parameter ID
            account_id: Account ID
            
        Returns:
            SPResult containing SP value information
        """
        try:
            url = f"{SPConfig.INTAPI_BASE_URL}/restapi/v1.0/internal/service-parameter/{sp_id}"
            params = {"accountId": account_id}
            headers = {
                "Authorization": SPConfig.INTAPI_AUTH_HEADER,
                "RCBrandId": SPConfig.INTAPI_BRAND_ID
            }
            
            async with HTTPClientFactory.create_async_client(
                timeout=self.timeout,
                headers=headers
            ) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                sp_data = response.json()
                
                logger.info(f"Retrieved SP {sp_id} value for account {account_id}: {sp_data.get('value')}")
                
                return SPResult(
                    success=True,
                    data=sp_data,
                    count=1
                )
                
        except Exception as e:
            error_msg = handle_http_error(
                e,
                f"retrieving service parameter '{sp_id}' value for account '{account_id}'",
                not_found_message=f"Service parameter {sp_id} or account {account_id} not found"
            )
            return create_error_result(SPResult, error_msg)
    
    async def get_service_parameter_value_by_phone(self, sp_id: str, phone_number: str, env_name: str = "webaqaxmn") -> SPResult:
        """
        Get service parameter value by phone number.
        
        Args:
            sp_id: Service parameter ID
            phone_number: Phone number (with or without + prefix)
            env_name: Environment name (default: webaqaxmn)
            
        Returns:
            SPResult containing SP value information
        """
        try:
            # Resolve phone number to account ID
            account_id = await self._resolve_phone_to_account_id(phone_number, env_name)
            if not account_id:
                return create_error_result(
                    SPResult,
                    f"Phone number {phone_number} not found in environment {env_name}"
                )
            
            # Get SP value using account ID
            return await self.get_service_parameter_value(sp_id, account_id)
            
        except Exception as e:
            error_msg = handle_http_error(
                e,
                f"retrieving service parameter '{sp_id}' value for phone '{phone_number}'",
                not_found_message=f"Phone number {phone_number} not found"
            )
            return create_error_result(SPResult, error_msg)
    
    async def _resolve_phone_to_account_id(self, phone_number: str, env_name: str) -> Optional[str]:
        """Resolve phone number to account ID using account pool service."""
        try:
            from ..account_pool.data_manager import DataManager
            from returns.pipeline import is_successful
            
            data_manager = DataManager()
            
            # Get all accounts for the environment
            accounts_result = data_manager.get_all_accounts_for_env(env_name)
            
            if not is_successful(accounts_result):
                logger.error(f"Could not fetch accounts from account pool for env {env_name}")
                return None
            
            accounts = accounts_result.unwrap()
            # Normalize phone number with + prefix
            normalized_phone = "+" + phone_number if not phone_number.startswith("+") else phone_number
            
            # Find account by phone number
            for account in accounts:
                if account.get("mainNumber") == normalized_phone:
                    account_id = account.get("accountId")
                    logger.info(f"Resolved phone {phone_number} to account ID {account_id}")
                    return account_id
            
            logger.warning(f"Phone number {phone_number} not found in env {env_name}")
            return None
            
        except Exception as e:
            logger.error(f"Error resolving phone to account ID: {e}")
            return None
    
    async def search_service_parameters(self, query: str) -> SPResult:
        """
        Search service parameters by description.
        
        Args:
            query: Search query string
            
        Returns:
            SPResult containing matching service parameters
        """
        try:
            # Get all service parameters first
            all_sps_result = await self.get_all_service_parameters()
            if not all_sps_result.success:
                return all_sps_result
            
            all_sps = all_sps_result.data
            query_lower = query.lower()
            
            matching_sps = {
                sp_id: description 
                for sp_id, description in all_sps.items()
                if query_lower in description.lower()
            }
            
            logger.info(f"Found {len(matching_sps)} service parameters matching '{query}'")
            
            return SPResult(
                success=True,
                data=matching_sps,
                count=len(matching_sps)
            )
            
        except Exception as e:
            logger.error(f"Error searching service parameters: {e}")
            return SPResult(
                success=False,
                error_message=f"Search failed: {e}"
            )
    
    async def get_service_parameter_definition(self, sp_id: str) -> SPResult:
        """
        Get service parameter definition by ID.
        
        Args:
            sp_id: Service parameter ID
            
        Returns:
            SPResult containing SP definition information
        """
        try:
            # Get all service parameters first
            all_sps_result = await self.get_all_service_parameters()
            if not all_sps_result.success:
                return all_sps_result
            
            all_sps = all_sps_result.data
            
            if sp_id not in all_sps:
                return SPResult(
                    success=False,
                    error_message=f"Service parameter {sp_id} not found",
                    count=0
                )
            
            sp_definition = {
                "id": sp_id,
                "description": all_sps[sp_id]
            }
            
            logger.info(f"Retrieved SP definition for {sp_id}")
            
            return SPResult(
                success=True,
                data=sp_definition,
                count=1
            )
            
        except Exception as e:
            logger.error(f"Error getting service parameter definition: {e}")
            return SPResult(
                success=False,
                error_message=f"Failed to get SP definition: {e}"
            )
    
    def get_server_info(self) -> Dict[str, Any]:
        """
        Get server information including configuration and cache status.
        
        Returns:
            Dict containing server information
        """
        cache_size = len(self._cache)
        
        server_info = {
            "status": "connected",
            "server": {
                "intapiBaseUrl": SPConfig.INTAPI_BASE_URL,
                "gitlabBaseUrl": SPConfig.GITLAB_BASE_URL,
                "timeout": self.timeout
            },
            "cache": {
                "size": cache_size,
                "enabled": True,
                "ttlSeconds": self._cache_ttl
            }
        }
        
        return server_info
    
    def clear_cache(self):
        """Clear the service cache."""
        self._cache.clear()
        logger.info("SP service cache cleared")


# Global SP service instance (deprecated, use ServiceFactory.get_sp_service() instead)
# Kept for backward compatibility
def _get_sp_service():
    """Lazy import to avoid circular dependencies."""
    from ..common.service_factory import ServiceFactory
    return ServiceFactory.get_sp_service()

sp_service = _get_sp_service()
