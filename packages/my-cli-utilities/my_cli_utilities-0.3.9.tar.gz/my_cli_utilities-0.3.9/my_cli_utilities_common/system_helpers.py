"""
Simple system resources helper using third-party libraries.
Uses environment variables for SSH authentication.
"""

import json
import logging
import os
import platform
import socket
import subprocess
import tempfile
import time
import uuid
from typing import Optional, Dict, Any
from dataclasses import dataclass
from contextlib import contextmanager
from pathlib import Path

@dataclass
class SimpleSystemResources:
    cpu_brand: str
    cpu_physical_cores: int
    cpu_logical_cores: int
    cpu_usage_percent: float
    memory_total_gb: float
    memory_used_gb: float
    memory_available_gb: float
    memory_usage_percent: float
    disk_total_gb: float
    disk_used_gb: float
    disk_free_gb: float
    disk_usage_percent: float
    os_name: str
    os_version: str
    hostname: str
    uptime_hours: float
    load_average: str
    boot_time: str
    mode: str = "unknown"


class SSHConfig:
    """Simplified SSH configuration with environment variable authentication only"""

    def get_ssh_credentials(self, hostname: str) -> tuple:
        """Get SSH credentials from environment variables"""
        # Use hostname directly without complex parsing
        # Usually hostname is already an IP address
        
        # Look for host-specific environment variables first
        host_key = hostname.upper().replace('.', '_').replace('-', '_')
        user = os.getenv(f"SSH_USER_{host_key}") or os.getenv("SSH_USER", "rcadmin")
        password = os.getenv(f"SSH_PASSWORD_{host_key}") or os.getenv("SSH_PASSWORD")
        
        if not password:
            raise Exception(f"SSH password not found in environment variables. Set SSH_PASSWORD or SSH_PASSWORD_{host_key}")
        
        return user, password, hostname  # Return original hostname directly


class SimpleSystemHelper:
    """Simplified system helper"""
    
    # Python script template
    SYSTEM_SCRIPT_TEMPLATE = '''import json,platform,socket,os,time,sys
try:
    import psutil,cpuinfo,distro
    
    cpu_interval = {cpu_interval}
    cpu_info = cpuinfo.get_cpu_info()
    memory = psutil.virtual_memory()
    
    # Enhanced disk usage for macOS
    if platform.system() == 'Darwin':
        try:
            root_disk = psutil.disk_usage('/')
            try:
                data_disk = psutil.disk_usage('/System/Volumes/Data')
                total_gb = root_disk.total / (1024**3)
                used_gb = (root_disk.used + data_disk.used) / (1024**3)
            except:
                total_gb = root_disk.total / (1024**3)
                used_gb = root_disk.used / (1024**3)
        except:
            total_gb = used_gb = 0
    else:
        try:
            disk = psutil.disk_usage('/')
            total_gb = disk.total / (1024**3)
            used_gb = disk.used / (1024**3)
        except:
            total_gb = used_gb = 0
    
    # System info
    try:
        boot_time = psutil.boot_time()
        uptime_hours = (time.time() - boot_time) / 3600
        load_avg = os.getloadavg()
        load_str = f"{{load_avg[0]:.2f}} {{load_avg[1]:.2f}} {{load_avg[2]:.2f}}"
        boot_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(boot_time))
    except:
        uptime_hours = 0
        load_str = "0.00 0.00 0.00"
        boot_time_str = "N/A"
    
    # CPU usage
    try:
        cpu_percent = psutil.cpu_percent(interval=cpu_interval)
    except:
        cpu_percent = 0.0
    
    result = {{
        'cpu_brand': cpu_info.get('brand_raw', 'N/A'),
        'cpu_physical_cores': psutil.cpu_count(logical=False) or 0,
        'cpu_logical_cores': psutil.cpu_count(logical=True) or 0,
        'cpu_usage_percent': round(cpu_percent, 1),
        'memory_total_gb': round(memory.total / (1024**3), 1),
        'memory_available_gb': round(memory.available / (1024**3), 1),
        'memory_used_gb': round(memory.used / (1024**3), 1),
        'memory_usage_percent': round(memory.percent, 1),
        'disk_total_gb': round(total_gb, 1),
        'disk_used_gb': round(used_gb, 1),
        'disk_free_gb': round(total_gb - used_gb, 1),
        'disk_usage_percent': round((used_gb / total_gb) * 100, 1) if total_gb > 0 else 0,
        'os_name': distro.name() if hasattr(distro, 'name') else platform.system(),
        'os_version': distro.version() if hasattr(distro, 'version') else platform.release(),
        'hostname': socket.gethostname(),
        'uptime_hours': round(uptime_hours, 1),
        'load_average': load_str,
        'boot_time': boot_time_str,
        'mode': '{mode}'
    }}
    print(json.dumps(result))
except ImportError:
    result = {{'cpu_brand': 'Third-party libraries not available', 'hostname': socket.gethostname()}}
    print(json.dumps(result))
except Exception as e:
    result = {{'error': str(e), 'hostname': 'N/A'}}
    print(json.dumps(result))
'''

    def __init__(self, mode: str = "fast"):
        self.ssh_config = SSHConfig()
        self.mode = mode

    def _get_script(self) -> str:
        """Generate script"""
        intervals = {"ultra_fast": 0, "fast": 0.1, "accurate": 1.0}
        cpu_interval = intervals.get(self.mode, 0.1)
        return self.SYSTEM_SCRIPT_TEMPLATE.format(
            cpu_interval=cpu_interval, 
            mode=self.mode
        )

    @contextmanager
    def _temp_script_file(self):
        temp_file = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(self._get_script())
                temp_file = f.name
            yield temp_file
        finally:
            if temp_file and os.path.exists(temp_file):
                os.unlink(temp_file)

    def _auto_install_dependencies(self, hostname: str) -> bool:
        """Auto install dependency libraries"""
        try:
            user, password, actual_hostname = self.ssh_config.get_ssh_credentials(hostname)
            ssh_opts = "-o StrictHostKeyChecking=no -o ConnectTimeout=2 -o UserKnownHostsFile=/dev/null"
            ssh_cmd = f'sshpass -p "{password}" ssh {ssh_opts} {user}@{actual_hostname}'
            
            # Check dependencies
            check_cmd = f'{ssh_cmd} "python3 -c \'import psutil,cpuinfo,distro; print(\\\"OK\\\")\'"'
            result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                return True
                
            # Install dependencies
            logger = logging.getLogger(__name__)
            logger.info(f"Installing dependencies on {hostname}...")
            
            install_cmd = f'{ssh_cmd} "pip3 install psutil py-cpuinfo distro"'
            result = subprocess.run(install_cmd, shell=True, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                logger.info(f"✅ Dependencies installed successfully on {hostname}")
                return True
            else:
                logger.warning(f"⚠️  Failed to install dependencies on {hostname}")
                return False
                
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.warning(f"⚠️  Could not auto-install dependencies on {hostname}: {e}")
            return False

    def _execute_remote_script(self, hostname: str, script_path: str) -> Optional[dict]:
        try:
            user, password, actual_hostname = self.ssh_config.get_ssh_credentials(hostname)
            remote_script = f"/tmp/system_check_{uuid.uuid4().hex[:8]}.py"
            
            ssh_opts = "-o StrictHostKeyChecking=no -o ConnectTimeout=2 -o UserKnownHostsFile=/dev/null"
            copy_cmd = f'sshpass -p "{password}" scp {ssh_opts} {script_path} {user}@{actual_hostname}:{remote_script}'
            exec_cmd = f'sshpass -p "{password}" ssh {ssh_opts} {user}@{actual_hostname} "python3 {remote_script} && rm {remote_script}"'
            
            # Copy and execute script
            subprocess.run(copy_cmd, shell=True, capture_output=True, check=True, timeout=3)
            
            timeout = 8 if self.mode == "accurate" else 5
            result = subprocess.run(exec_cmd, shell=True, capture_output=True, text=True, timeout=timeout)
            
            if result.returncode == 0:
                try:
                    data = json.loads(result.stdout.strip())
                    # Check if dependencies are missing
                    if data.get('cpu_brand') == 'Third-party libraries not available':
                        if self._auto_install_dependencies(hostname):
                            result = subprocess.run(exec_cmd, shell=True, capture_output=True, text=True, timeout=timeout)
                            if result.returncode == 0:
                                return json.loads(result.stdout.strip())
                    return data
                except json.JSONDecodeError:
                    pass
            
            return None
            
        except Exception as e:
            logger = logging.getLogger(__name__)
            error_msg = str(e)
            if "sshpass" in error_msg and "not found" in error_msg:
                logger.error("sshpass not found. Install: brew install hudochenkov/sshpass/sshpass")
                raise Exception("sshpass not installed. Run: brew install hudochenkov/sshpass/sshpass")
            elif "returned non-zero exit status 5" in error_msg:
                logger.error(f"SSH authentication failed for {hostname}")
                raise Exception(f"SSH authentication failed for {hostname}. Check password.")
            else:
                logger.error(f"SSH execution failed: {e}")
                raise Exception(f"SSH connection failed: {error_msg[:50]}")

    def _parse_system_data(self, data: dict) -> Optional[SimpleSystemResources]:
        if not data or 'error' in data or data.get('cpu_brand') == 'Third-party libraries not available':
            return None

        return SimpleSystemResources(
            cpu_brand=data.get('cpu_brand', 'N/A'),
            cpu_physical_cores=data.get('cpu_physical_cores', 0),
            cpu_logical_cores=data.get('cpu_logical_cores', 0),
            cpu_usage_percent=data.get('cpu_usage_percent', 0.0),
            memory_total_gb=data.get('memory_total_gb', 0.0),
            memory_used_gb=data.get('memory_used_gb', 0.0),
            memory_available_gb=data.get('memory_available_gb', 0.0),
            memory_usage_percent=data.get('memory_usage_percent', 0.0),
            disk_total_gb=data.get('disk_total_gb', 0.0),
            disk_used_gb=data.get('disk_used_gb', 0.0),
            disk_free_gb=data.get('disk_free_gb', 0.0),
            disk_usage_percent=data.get('disk_usage_percent', 0.0),
            os_name=data.get('os_name', 'N/A'),
            os_version=data.get('os_version', 'N/A'),
            hostname=data.get('hostname', 'N/A'),
            uptime_hours=data.get('uptime_hours', 0.0),
            load_average=data.get('load_average', '0.00 0.00 0.00'),
            boot_time=data.get('boot_time', 'N/A'),
            mode=data.get('mode', 'unknown')
        )
    
    def get_system_resources(self, hostname: str) -> Optional[SimpleSystemResources]:
        try:
            with self._temp_script_file() as script_path:
                data = self._execute_remote_script(hostname, script_path)
            return self._parse_system_data(data) if data else None
        except Exception as e:
            # Propagate exception to caller to display specific error message
            raise e


def get_simple_system_resources(hostname: str, fast_mode: bool = True) -> Optional[SimpleSystemResources]:
    """Get system resource information"""
    mode = "ultra_fast" if fast_mode else "accurate"
    helper = SimpleSystemHelper(mode=mode)
    return helper.get_system_resources(hostname)


def main():
    """CLI management tool"""
    import sys
    
    if len(sys.argv) < 2:
        print("🔧 My CLI Utilities - System Helper")
        print("Usage:")
        print("  python -m my_cli_utilities_common.system_helpers test <hostname> [--accurate]")
        print("")
        print("🔐 Environment Variables:")
        print("  SSH_USER=rcadmin")
        print("  SSH_PASSWORD=your_password")
        print("  SSH_USER_XMNA030=special_user    # Host-specific")
        print("  SSH_PASSWORD_XMNA030=special_pwd # Host-specific")
        return
    
    command = sys.argv[1]
    
    if command == "test" and len(sys.argv) > 2:
        hostname = sys.argv[2]
        accurate_mode = "--accurate" in sys.argv
        mode_str = "accurate" if accurate_mode else "fast"
        
        print(f"🧪 Testing {hostname} ({mode_str} mode)...")
        resources = get_simple_system_resources(hostname, fast_mode=not accurate_mode)
        if resources:
            print("✅ Connection successful!")
            print(f"   CPU: {resources.cpu_brand}")
            print(f"   CPU Usage: {resources.cpu_usage_percent}%")
            print(f"   Memory: {resources.memory_used_gb:.1f}GB / {resources.memory_total_gb:.1f}GB")
            print(f"   OS: {resources.os_name} {resources.os_version}")
        else:
            print("❌ Connection failed")
    else:
        print("❌ Invalid command")


if __name__ == "__main__":
    main() 