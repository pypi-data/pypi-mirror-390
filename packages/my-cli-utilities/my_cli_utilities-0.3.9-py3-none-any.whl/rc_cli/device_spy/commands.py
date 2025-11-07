# -*- coding: utf-8 -*-

"""Enhanced CLI commands using returns library for better error handling."""

import typer
from typing import Dict, List
from returns.result import Success, Failure
import json
from rich.console import Console
from enum import Enum

from .result_types import (
    ResultHandler, ErrorDisplay, 
    validation_error, data_not_found_error, AppError, ErrorType
)
from .data_manager import (
    DataManager, 
    get_device_by_udid, 
    get_available_devices_by_platform,
    get_hosts_by_query,
    get_device_summary,
    get_devices_by_host
)
from .connection_services import ConnectionManager
from .display_managers import DeviceDisplayManager
from .host_display import HostDisplayManager


class Platform(str, Enum):
    """Supported device platforms."""
    ANDROID = "android"
    IOS = "ios"


class InputValidator:
    """Input validation utilities for CLI commands."""
    
    @staticmethod
    def validate_non_empty(value: str, field_name: str) -> str:
        """Validate that a string value is not empty after stripping."""
        value = value.strip()
        if not value:
            error = validation_error(f"{field_name} cannot be empty")
            ErrorDisplay.show_error(error)
            raise typer.Exit(1)
        return value
    
    @staticmethod
    def validate_platform(platform: str) -> str:
        """Validate that platform is one of the supported values."""
        platform = platform.lower().strip()
        if platform not in [p.value for p in Platform]:
            error = validation_error("Platform must be 'android' or 'ios'")
            ErrorDisplay.show_error(error)
            raise typer.Exit(1)
        return platform


class CLICommands:
    """CLI commands with functional error handling."""
    
    def __init__(self):
        self.data_manager = DataManager()
        self.connection_manager = ConnectionManager(self.data_manager)
        self.result_handler = ResultHandler()
    
    def get_device_info(self, udid: str) -> None:
        """📱 Display detailed information for a specific device using functional approach."""
        # Validate input
        udid = InputValidator.validate_non_empty(udid, "UDID")
        
        # Show search info
        typer.echo(f"\n🔍 Looking up device information...")
        typer.echo(f"   UDID: {udid}")
        
        # Get device using functional composition
        device_result = get_device_by_udid(self.data_manager, udid)
        
        # Handle result or exit
        device = self.result_handler.handle_result(device_result)
        
        # Show success
        ErrorDisplay.show_success("Device found")
        
        # Get host alias by matching hostname
        host_alias = None
        hostname = device.get("hostname")
        if hostname:
            hosts_result = self.data_manager.get_hosts()
            if isinstance(hosts_result, Success):
                hosts = hosts_result.unwrap()
                matching_host = next((h for h in hosts if h.get("hostname") == hostname), None)
                if matching_host:
                    host_alias = matching_host.get("alias")
        
        # Display device with host alias
        DeviceDisplayManager.display_device_info(device, host_alias)
    
    def list_available_devices(self, platform: str) -> None:
        """📋 List available devices for a platform using functional approach."""
        # Validate input
        platform = InputValidator.validate_platform(platform)
        
        # Show search info
        typer.echo(f"\n🔍 Finding available devices...")
        typer.echo(f"   Platform: {platform}")
        
        # Get devices using functional composition
        devices_result = get_available_devices_by_platform(self.data_manager, platform)
        
        # Handle result or exit
        available_devices = self.result_handler.handle_result(devices_result)
        
        # Show results
        ErrorDisplay.show_success(f"Found {len(available_devices)} available {platform} devices")
        
        if available_devices:
            title = f"📱 Available {platform.capitalize()} Devices"
            DeviceDisplayManager.display_device_list(available_devices, title)
        else:
            ErrorDisplay.show_info(f"No available {platform} devices found")
            typer.echo(f"   💡 Tip: Try 'ds host <hostname> --detailed' to see all devices on a specific host")
    
    def find_host_info(self, query: str, detailed: bool = False) -> None:
        """🖥️ Find host information by query using functional approach."""
        # Validate input
        query = InputValidator.validate_non_empty(query, "Host query")
        
        # Search for hosts
        found_hosts = self._search_hosts(query)
        
        # Display results based on detailed flag and number of results
        self._display_host_results(found_hosts, query, detailed)
    
    def _search_hosts(self, query: str) -> List[Dict]:
        """Search for hosts and return results."""
        # Show search info
        typer.echo(f"\n🔍 Searching for hosts...")
        typer.echo(f"   Query: '{query}'")
        
        # Get hosts using functional composition
        hosts_result = get_hosts_by_query(self.data_manager, query)
        
        # Handle result or exit
        found_hosts = self.result_handler.handle_result(hosts_result)
        
        # Show results
        ErrorDisplay.show_success(f"Found {len(found_hosts)} matching host(s)")
        
        return found_hosts
    
    def _display_host_results(self, found_hosts: List[Dict], query: str, detailed: bool) -> None:
        """Display host results based on detailed flag and number of results."""
        if detailed and len(found_hosts) == 1:
            self._show_detailed_host_info(found_hosts[0])
        elif detailed and len(found_hosts) > 1:
            ErrorDisplay.show_warning("Multiple hosts found. Please be more specific for detailed view:")
            HostDisplayManager.display_host_results(found_hosts, query)
        else:
            HostDisplayManager.display_host_results(found_hosts, query)
            if len(found_hosts) == 1:
                typer.echo(f"\n💡 Use 'ds host {query} --detailed' for comprehensive host information")
    
    def _show_detailed_host_info(self, host: Dict) -> None:
        """Show detailed host information with consistent error handling."""
        hostname = host.get("hostname", "")
        devices_result = self.data_manager.get_devices()
        
        # Use consistent error handling - if we can't get devices, show error and exit
        if isinstance(devices_result, Success):
            devices = devices_result.unwrap()
            host_devices = get_devices_by_host(devices, hostname)
            HostDisplayManager.display_detailed_host_info(host, host_devices)
        else:
            ErrorDisplay.show_error(devices_result.failure())
            raise typer.Exit(1)
    
    def ssh_connect(self, query: str) -> None:
        """🔗 Connect to a host via SSH using functional approach."""
        # Validate input
        query = InputValidator.validate_non_empty(query, "Host query")
        
        # Show connection info
        typer.echo(f"\n🔍 Looking up host...")
        typer.echo(f"   Query: '{query}'")
        
        # Attempt SSH connection using functional composition
        connection_result = self.connection_manager.connect_ssh(query)
        
        # Handle custom error for multiple matches
        if isinstance(connection_result, Failure):
            error: AppError = connection_result.failure()
            if error.error_type == ErrorType.MULTIPLE_MATCHES_FOUND:
                ErrorDisplay.show_error(error)
                HostDisplayManager.display_host_results(error.context, query)
                raise typer.Exit(1)

        # Handle other results - if it fails, it will exit
        self.result_handler.handle_result(connection_result)
        
        # If we reach here, connection was successful or ended normally
        ErrorDisplay.show_success("SSH connection completed")
    
    def adb_connect(self, udid: str) -> None:
        """🤖 Connect to Android device via ADB using functional approach."""
        # Validate input
        udid = InputValidator.validate_non_empty(udid, "UDID")
        
        # Show connection info
        typer.echo(f"\n🔍 Looking up Android device...")
        typer.echo(f"   UDID: {udid}")
        
        # Attempt ADB connection using functional composition
        connection_result = self.connection_manager.connect_adb(udid)
        
        # Handle result - if it fails, it will exit
        self.result_handler.handle_result(connection_result)
        
        # If we reach here, connection was successful
        ErrorDisplay.show_success("ADB connection successful")
    
    def get_android_connection(self, udid: str) -> str:
        """🤖 Get Android device IP:Port for ADB connection (for script usage)."""
        device_result = get_device_by_udid(self.data_manager, udid)
        
        if isinstance(device_result, Failure):
            typer.echo("not_found")
            return "not_found"
        
        device = device_result.unwrap()
        
        if device.get("is_locked"):
            typer.echo("locked")
            return "locked"
        elif device.get("platform") == "android" and device.get("adb_port"):
            ip_port = f"{device.get('hostname')}:{device.get('adb_port')}"
            typer.echo(ip_port)
            return ip_port
        else:
            typer.echo("not_android")
            return "not_android"
    
    def get_host_ip_for_script(self, query: str) -> str:
        """🌐 Get host IP address for script usage."""
        host_ip_result = self.connection_manager.host_resolver.resolve_host_ip(query)
        
        if isinstance(host_ip_result, Failure):
            typer.echo("not_found")
            return "not_found"
        
        host_ip = host_ip_result.unwrap()
        typer.echo(host_ip)
        return host_ip
    
    def show_system_status(self) -> None:
        """📊 Show system status and cache information."""
        from .ds_data_manager import Config  # Import here to avoid circular import
        
        typer.echo(f"\n📊 Device Spy CLI Status")
        typer.echo("=" * Config.DISPLAY_WIDTH)
        
        # API connectivity
        typer.echo(f"🌐 API Connectivity:")
        typer.echo(f"   Base URL:     {Config.BASE_URL}")
        
        # Cache status
        devices_cached = self.data_manager.is_devices_cached()
        hosts_cached = self.data_manager.is_hosts_cached()
        
        typer.echo(f"\n💾 Cache Status:")
        typer.echo(f"   Devices:      {'✅ Cached' if devices_cached else '❌ Not cached'}")
        typer.echo(f"   Hosts:        {'✅ Cached' if hosts_cached else '❌ Not cached'}")
        
        if devices_cached:
            device_count = self.data_manager.get_cached_device_count()
            typer.echo(f"   Device Count: {device_count}")
            
            if device_count > 0:
                summary = get_device_summary(self.data_manager._devices_cache)
                typer.echo(f"   Android:      {summary['android']}")
                typer.echo(f"   iOS:          {summary['ios']}")
                typer.echo(f"   Available:    {summary['available']}")
                typer.echo(f"   Locked:       {summary['locked']}")
        
        if hosts_cached:
            host_count = self.data_manager.get_cached_host_count()
            typer.echo(f"   Host Count:   {host_count}")
        
        # Quick connectivity test using Result types
        typer.echo(f"\n🔍 Quick Connectivity Test:")
        
        devices_result = self.data_manager.get_devices(force_refresh=True)
        hosts_result = self.data_manager.get_hosts(force_refresh=True)
        
        if isinstance(devices_result, Success) and isinstance(hosts_result, Success):
            devices = devices_result.unwrap()
            hosts = hosts_result.unwrap()
            ErrorDisplay.show_success("Connected")
            typer.echo(f"   Devices:      {len(devices)} found")
            typer.echo(f"   Hosts:        {len(hosts)} found")
        else:
            ErrorDisplay.show_error("Connection failed")
        
        typer.echo("=" * Config.DISPLAY_WIDTH)
    
    def refresh_cache(self) -> None:
        """🔄 Refresh cached data from server using Result types."""
        typer.echo(f"\n🔄 Refreshing cached data...")
        
        devices_result = self.data_manager.get_devices(force_refresh=True)
        hosts_result = self.data_manager.get_hosts(force_refresh=True)
        
        if isinstance(devices_result, Success) and isinstance(hosts_result, Success):
            devices = devices_result.unwrap()
            hosts = hosts_result.unwrap()
            ErrorDisplay.show_success("Cache refreshed successfully")
            typer.echo(f"   📱 Devices: {len(devices)}")
            typer.echo(f"   🖥️  Hosts:   {len(hosts)}")
        else:
            # Show the actual error
            if isinstance(devices_result, Failure):
                ErrorDisplay.show_error(devices_result.failure())
            if isinstance(hosts_result, Failure):
                ErrorDisplay.show_error(hosts_result.failure())
            raise typer.Exit(1) 