# Update core/utils.py
"""
Utility Functions
"""

import os
import time
import json
import psutil
import subprocess
import yaml
import logging

def run_command(command, timeout=600):
    """Run a shell command with timeout"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Command timed out",
            "returncode": -1
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "returncode": -1
        }

# Update resource_monitor in core/utils.py
def resource_monitor(history, interval=5):
    """Monitor system resources"""
    try:
        while True:
            cpu = psutil.cpu_percent(interval=1)
            ram = psutil.virtual_memory().percent
            disk = psutil.disk_usage("/").percent
            
            net = psutil.net_io_counters()
            net_usage = (net.bytes_sent + net.bytes_recv) / (1024 * 1024)  # in MB
            
            history.append({
                "timestamp": time.time(),
                "cpu": cpu,
                "ram": ram,
                "disk": disk,
                "network": net_usage
            })
            
            time.sleep(interval)
    except Exception as e:
        logging.error(f"Resource monitor failed: {str(e)}")

def load_config():
    """Load configuration file"""
    try:
        with open("config/config.yaml", "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        return {}
    except Exception as e:
        logging.error(f"Error loading config: {str(e)}")
        return {}

def load_api_keys():
    """Load API keys configuration"""
    try:
        with open("config/api_keys.yaml", "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        return {}
    except Exception as e:
        logging.error(f"Error loading API keys: {str(e)}")
        return {}

def setup_logging(debug=False):
    """Configure logging system"""
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("reconmaster.log"),
            logging.StreamHandler()
        ]
    )