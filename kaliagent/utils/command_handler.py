import subprocess
import shlex
import shutil
from typing import Dict, Tuple, List, Optional
from pathlib import Path
import logging
from ..config.settings import settings

logger = logging.getLogger("kaliagent.commands")

def check_tool_installed(tool_name: str) -> bool:
    """Check if a security tool is installed on the system
    
    Uses shutil.which() for cross-platform compatibility (Windows/Linux/Mac)
    """
    try:
        # shutil.which() is cross-platform and returns None if not found
        return shutil.which(tool_name) is not None
    except Exception as e:
        logger.error(f"Error checking tool installation: {str(e)}")
        return False

def validate_command(command: str) -> Tuple[bool, str]:
    """Validate if a command is safe to execute
    
    Returns:
        Tuple[bool, str]: (is_valid, reason)
    """
    if not command or not command.strip():
        return False, "Empty command"
    
    # Parse command to get the base command
    try:
        args = shlex.split(command)
        if not args:
            return False, "Unable to parse command"
            
        base_cmd = args[0]
        
        # Check if in allowed tools list
        if base_cmd not in settings.ALLOWED_TOOLS:
            return False, f"Tool '{base_cmd}' is not in the allowed tools list"
            
        # Check if tool is installed
        if not check_tool_installed(base_cmd):
            return False, f"Tool '{base_cmd}' is not installed on this system"
            
        return True, "Command is valid"
        
    except Exception as e:
        logger.error(f"Error validating command: {str(e)}")
        return False, f"Error validating command: {str(e)}"

def execute_command(command: str) -> Dict:
    """Execute a security-related command safely
    
    Returns:
        Dict containing execution results
    """
    # First validate the command
    is_valid, reason = validate_command(command)
    
    if not is_valid:
        return {
            "success": False,
            "error": reason,
            "stdout": "",
            "stderr": "",
            "returncode": -1
        }
    
    try:
        # Parse command securely
        try:
            cmd_args = shlex.split(command)
        except ValueError as e:
            return {
                "success": False,
                "error": f"Invalid command syntax: {str(e)}",
                "stdout": "",
                "stderr": "",
                "returncode": -1
            }
        
        # Execute the command with shell=False for security
        process = subprocess.run(
            cmd_args,
            shell=False,  # Security: Never use shell=True with user input
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        return {
            "success": process.returncode == 0,
            "stdout": process.stdout,
            "stderr": process.stderr,
            "returncode": process.returncode,
            "command": command
        }
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Command execution timed out (5 minute limit)",
            "stdout": "",
            "stderr": "Timeout",
            "returncode": -1,
            "command": command
        }
    except FileNotFoundError:
        return {
            "success": False,
            "error": f"Command not found: {cmd_args[0] if cmd_args else 'unknown'}",
            "stdout": "",
            "stderr": "Command not found",
            "returncode": -1,
            "command": command
        }
    except Exception as e:
        logger.error(f"Error executing command: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "stdout": "",
            "stderr": str(e),
            "returncode": -1,
            "command": command
        }

def get_installed_security_tools() -> List[str]:
    """Get a list of security tools that are installed on the system"""
    installed_tools = []
    
    for tool in settings.ALLOWED_TOOLS:
        if check_tool_installed(tool):
            installed_tools.append(tool)
            
    return installed_tools
