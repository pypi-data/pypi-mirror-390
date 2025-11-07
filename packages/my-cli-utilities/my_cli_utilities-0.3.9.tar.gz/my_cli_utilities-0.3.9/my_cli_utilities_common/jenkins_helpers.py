"""
Jenkins API integration helpers for fetching agent information.
"""

import os
import logging
from typing import Dict, List, Optional, Union
import httpx
from .http_helpers import make_sync_request

logger = logging.getLogger(__name__)


class JenkinsHelper:
    """Helper class for Jenkins API integration."""
    
    def __init__(self, base_url: str = None):
        self.base_url = (base_url or os.environ.get(
            "JENKINS_BASE_URL",
            "https://jenkins.example.com"
        )).rstrip('/')
        self.timeout = 10.0
    
    def get_agent_info(self, agent_name: str) -> Optional[Dict]:
        """
        Get detailed Jenkins agent information
        
        Args:
            agent_name: Jenkins agent name (e.g., XMNA106)
            
        Returns:
            Dictionary containing agent information, or None if failed
        """
        try:
            # Jenkins API endpoint with tree parameter to get detailed executor info
            base_url = f"{self.base_url}/computer/{agent_name}/api/json"
            tree_params = "?tree=offline,assignedLabels[name],executors[number,idle,currentExecutable[displayName,number,url],progress],description"
            url = f"{base_url}{tree_params}"
            
            with httpx.Client(timeout=self.timeout, verify=False) as client:
                response = client.get(url)
                response.raise_for_status()
                return response.json()
                
        except httpx.TimeoutException:
            logger.warning(f"Jenkins API timeout for agent {agent_name}")
            return None
        except httpx.HTTPStatusError as e:
            logger.warning(f"Jenkins API HTTP error for agent {agent_name}: {e.response.status_code}")
            return None
        except Exception as e:
            logger.warning(f"Jenkins API error for agent {agent_name}: {e}")
            return None
    
    def get_agent_labels(self, agent_name: str) -> List[str]:
        """
        Get Jenkins agent labels list
        
        Args:
            agent_name: Jenkins agent name
            
        Returns:
            List of labels
        """
        agent_info = self.get_agent_info(agent_name)
        if not agent_info:
            return []
        
        # Parse label information from Jenkins API response
        labels = []
        assigned_labels = agent_info.get('assignedLabels', [])
        
        for label in assigned_labels:
            if isinstance(label, dict):
                name = label.get('name', '')
                if name and name != agent_name:  # Exclude agent name itself as label
                    labels.append(name)
            elif isinstance(label, str):
                if label != agent_name:
                    labels.append(label)
        
        return labels
    
    def get_executor_status(self, agent_name: str) -> List[Dict]:
        """
        Get Jenkins agent executor status
        
        Args:
            agent_name: Jenkins agent name
            
        Returns:
            List of executor status info including number, idle state, current build info, etc.
        """
        agent_info = self.get_agent_info(agent_name)
        if not agent_info:
            return []
        
        executors = []
        executors_data = agent_info.get('executors', [])
        
        for executor in executors_data:
            executor_info = {
                'number': executor.get('number', 0),  # Use actual executor number from Jenkins API
                'idle': executor.get('idle', True),
                'current_executable': None,
                'progress': executor.get('progress', -1)  # Get progress directly
            }
            
            # If executor is running a job
            current_executable = executor.get('currentExecutable')
            if current_executable:
                executor_info['current_executable'] = {
                    'display_name': current_executable.get('displayName', 'Unknown Job'),
                    'url': current_executable.get('url', ''),
                    'number': current_executable.get('number', 'N/A')
                }
            
            executors.append(executor_info)
        
        return executors
    
    def get_agent_summary(self, agent_name: str) -> Dict[str, Union[str, List, int, bool]]:
        """
        Get Jenkins agent summary information
        
        Args:
            agent_name: Jenkins agent name
            
        Returns:
            Dictionary containing labels, executor status, online status, etc.
        """
        agent_info = self.get_agent_info(agent_name)
        
        if not agent_info:
            return {
                'online': False,
                'labels': [],
                'executors': [],
                'total_executors': 0,
                'busy_executors': 0,
                'error': 'Unable to fetch Jenkins information'
            }
        
        labels = self.get_agent_labels(agent_name)
        executors = self.get_executor_status(agent_name)
        busy_executors = [e for e in executors if not e['idle']]
        
        return {
            'online': not agent_info.get('offline', True),
            'labels': labels,
            'executors': executors,
            'total_executors': len(executors),
            'busy_executors': len(busy_executors),
            'description': agent_info.get('description', ''),
            'jenkins_url': f"{self.base_url}/computer/{agent_name}/"
        }


# Global Jenkins helper instance
jenkins_helper = JenkinsHelper()


def get_jenkins_info_for_host(hostname: str) -> Optional[Dict]:
    """
    Convenience function to get Jenkins information by hostname
    
    Args:
        hostname: Hostname (e.g., XMNA106, 10.32.46.106)
        
    Returns:
        Jenkins summary info dictionary, or None if no corresponding Jenkins agent found
    """
    # Try to extract Jenkins agent name from hostname
    agent_name = extract_jenkins_agent_name(hostname)
    if not agent_name:
        return None
    
    return jenkins_helper.get_agent_summary(agent_name)


def extract_jenkins_agent_name(hostname: str) -> Optional[str]:
    """
    Extract Jenkins agent name from hostname
    
    Args:
        hostname: Hostname or IP address
        
    Returns:
        Jenkins agent name, or None if unable to extract
    """
    # If already in XMNA format, return directly
    if hostname.upper().startswith('XMNA'):
        return hostname.upper()
    
    # If it's an IP address, try to convert to XMNA format
    # This needs to be implemented based on actual IP to XMNA mapping rules
    # Currently using simple processing, can be extended later
    if '.' in hostname:
        # Extract last part of IP, e.g., 10.32.46.106 -> 106
        parts = hostname.split('.')
        if len(parts) == 4:
            try:
                last_octet = int(parts[-1])
                return f"XMNA{last_octet:03d}"  # e.g., 106 -> XMNA106
            except ValueError:
                pass
    
    return None 