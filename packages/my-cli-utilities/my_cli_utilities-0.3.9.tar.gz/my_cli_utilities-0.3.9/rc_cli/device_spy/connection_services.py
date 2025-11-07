# -*- coding: utf-8 -*-

"""Connection services with decomposed functions using returns library."""

import re
import subprocess
import logging
from typing import Dict, List, Tuple
from dataclasses import dataclass
from returns.result import Result, Success, Failure
from returns.pipeline import flow
from returns.pointfree import bind

from .result_types import (
    AppError, StringResult, 
    validation_error, connection_error, system_error, data_not_found_error,
    multiple_matches_error
)
from .data_manager import DataManager, get_device_by_udid

logger = logging.getLogger(__name__)


@dataclass
class SSHConnectionConfig:
    """SSH connection configuration."""
    host_ip: str
    username: str
    password: str
    timeout: int = 30
    
    def to_command(self) -> List[str]:
        """Convert to SSH command array."""
        return [
            "sshpass", "-p", self.password, "ssh",
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            "-o", "ServerAliveInterval=60",
            "-o", "ServerAliveCountMax=30",
            "-o", "TCPKeepAlive=yes",
            "-o", f"ConnectTimeout={self.timeout}",
            f"{self.username}@{self.host_ip}"
        ]


@dataclass
class ADBConnectionConfig:
    """ADB connection configuration."""
    ip_port: str
    timeout: int = 15
    
    def to_connect_command(self) -> List[str]:
        """Convert to ADB connect command."""
        return ["adb", "connect", self.ip_port]
    
    def to_disconnect_command(self) -> List[str]:
        """Convert to ADB disconnect command."""
        return ["adb", "disconnect", self.ip_port]


class HostResolver:
    """Resolves host queries to IP addresses."""
    
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
    
    def resolve_host_ip(self, query: str) -> StringResult:
        """Resolve host query to IP address."""
        return flow(
            self.data_manager.get_hosts(),
            bind(self._find_matching_host(query)),
            bind(self._extract_host_ip),
            bind(self._validate_ip)
        )
    
    def _find_matching_host(self, query: str):
        """Find matching host from list."""
        def find_host(hosts: List[Dict]) -> Result[Dict, AppError]:
            query_lower = query.lower()
            matching_hosts = [
                host for host in hosts
                if (query_lower in host.get("hostname", "").lower() or
                    query_lower in host.get("alias", "").lower())
            ]
            
            if not matching_hosts:
                return Failure(data_not_found_error(
                    f"No host found matching '{query}'"
                ))
            
            if len(matching_hosts) > 1:
                return Failure(multiple_matches_error(
                    f"Multiple hosts found matching '{query}'",
                    matching_hosts
                ))
            
            return Success(matching_hosts[0])
        
        return find_host
    
    def _extract_host_ip(self, host: Dict) -> StringResult:
        """Extract IP address from host data."""
        hostname = host.get("hostname")
        if not hostname:
            return Failure(data_not_found_error("Host has no hostname"))
        
        return Success(hostname)
    
    def _validate_ip(self, ip: str) -> StringResult:
        """Validate IP address format."""
        pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        if not re.match(pattern, ip):
            return Failure(validation_error(f"Invalid IP address format: {ip}"))
        
        return Success(ip)


class SSHCredentialProvider:
    """Provides SSH credentials."""
    
    @staticmethod
    def get_credentials(host_ip: str) -> Result[Tuple[str, str], AppError]:
        """Get SSH credentials for host."""
        try:
            from my_cli_utilities_common.system_helpers import SSHConfig
            ssh_config = SSHConfig()
            user, password, _ = ssh_config.get_ssh_credentials(host_ip)
            return Success((user, password))
        except Exception as e:
            return Failure(system_error(
                "Failed to get SSH credentials",
                str(e)
            ))


class ProcessExecutor:
    """Executes system processes with error handling."""
    
    @staticmethod
    def execute_ssh_command(config: SSHConnectionConfig) -> Result[int, AppError]:
        """Execute SSH command and return exit code."""
        try:
            result = subprocess.run(config.to_command(), check=False)
            return Success(result.returncode)
        
        except subprocess.TimeoutExpired:
            return Failure(connection_error(
                f"SSH connection timeout after {config.timeout}s"
            ))
        except FileNotFoundError:
            return Failure(system_error(
                "sshpass not found",
                "Install with: brew install sshpass"
            ))
        except KeyboardInterrupt:
            return Success(130)  # Ctrl+C exit code
        except Exception as e:
            return Failure(connection_error(
                "SSH connection failed",
                str(e)
            ))
    
    @staticmethod
    def execute_adb_command(command: List[str], timeout: int = 15) -> Result[subprocess.CompletedProcess, AppError]:
        """Execute ADB command with timeout."""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
                timeout=timeout
            )
            return Success(result)
        
        except subprocess.TimeoutExpired:
            return Failure(connection_error(
                f"ADB command timeout after {timeout}s"
            ))
        except FileNotFoundError:
            return Failure(system_error(
                "adb not found",
                "Install Android SDK Platform Tools"
            ))
        except Exception as e:
            return Failure(connection_error(
                "ADB command failed",
                str(e)
            ))


class SSHExitCodeInterpreter:
    """Interprets SSH exit codes."""
    
    @staticmethod
    def interpret_exit_code(exit_code: int) -> Tuple[str, str]:
        """Interpret SSH exit code and return status and message."""
        interpretations = {
            0: ("success", "SSH session ended normally"),
            130: ("interrupted", "SSH session interrupted by user"),
            255: ("connection_error", "SSH connection error")
        }
        
        status, message = interpretations.get(
            exit_code, 
            ("unknown", f"SSH connection ended (exit code: {exit_code})")
        )
        
        return status, message


class DeviceValidator:
    """Validates device for ADB connection."""
    
    @staticmethod
    def validate_for_adb(device: Dict) -> Result[Dict, AppError]:
        """Validate device is suitable for ADB connection."""
        if device.get("is_locked"):
            return Failure(validation_error(
                f"Device {device.get('udid', 'unknown')} is locked"
            ))
        
        if device.get("platform") != "android":
            return Failure(validation_error(
                "Device is not Android platform"
            ))
        
        if not device.get("adb_port"):
            return Failure(validation_error(
                "Device has no ADB port configured"
            ))
        
        return Success(device)


class ConnectionManager:
    """Enhanced connection manager with decomposed functions."""
    
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        self.host_resolver = HostResolver(data_manager)
        self.credential_provider = SSHCredentialProvider()
        self.process_executor = ProcessExecutor()
        self.exit_code_interpreter = SSHExitCodeInterpreter()
        self.device_validator = DeviceValidator()
    
    def connect_ssh(self, query: str) -> Result[None, AppError]:
        """Connect to host via SSH using functional composition."""
        return flow(
            self.host_resolver.resolve_host_ip(query),
            bind(self._create_ssh_config),
            bind(self._execute_ssh_connection),
            bind(self._handle_ssh_result)
        )
    
    def _create_ssh_config(self, host_ip: str) -> Result[SSHConnectionConfig, AppError]:
        """Create SSH configuration."""
        return self.credential_provider.get_credentials(host_ip).map(
            lambda creds: SSHConnectionConfig(
                host_ip=host_ip,
                username=creds[0],
                password=creds[1]
            )
        )
    
    def _execute_ssh_connection(self, config: SSHConnectionConfig) -> Result[int, AppError]:
        """Execute SSH connection."""
        return self.process_executor.execute_ssh_command(config)
    
    def _handle_ssh_result(self, exit_code: int) -> Result[None, AppError]:
        """Handle SSH connection result."""
        status, message = self.exit_code_interpreter.interpret_exit_code(exit_code)
        
        if status == "connection_error":
            return Failure(connection_error(
                message,
                "Check network connectivity, host availability, or SSH service status"
            ))
        
        # For all other cases (success, interrupted, unknown), we consider it successful
        return Success(None)
    
    def connect_adb(self, udid: str) -> Result[None, AppError]:
        """Connect to Android device via ADB using functional composition."""
        return flow(
            get_device_by_udid(self.data_manager, udid),
            bind(self.device_validator.validate_for_adb),
            bind(self._create_adb_config),
            bind(self._execute_adb_connection)
        )
    
    def _create_adb_config(self, device: Dict) -> Result[ADBConnectionConfig, AppError]:
        """Create ADB configuration from device."""
        hostname = device.get("hostname")
        adb_port = device.get("adb_port")
        
        if not hostname or not adb_port:
            return Failure(validation_error(
                "Device missing hostname or ADB port"
            ))
        
        return Success(ADBConnectionConfig(
            ip_port=f"{hostname}:{adb_port}"
        ))
    
    def _execute_adb_connection(self, config: ADBConnectionConfig) -> Result[None, AppError]:
        """Execute ADB connection sequence."""
        # First disconnect if connected
        disconnect_result = self.process_executor.execute_adb_command(
            config.to_disconnect_command(), timeout=5
        )
        # We don't check disconnect result as it's OK if it fails
        
        # Then connect
        return self.process_executor.execute_adb_command(
            config.to_connect_command(),
            config.timeout
        ).bind(self._validate_adb_result)
    
    def _validate_adb_result(self, result: subprocess.CompletedProcess) -> Result[None, AppError]:
        """Validate ADB connection result."""
        if result.returncode == 0:
            return Success(None)
        
        error_message = result.stderr.strip() if result.stderr else "Unknown ADB error"
        return Failure(connection_error(
            "ADB connection failed",
            error_message
        )) 