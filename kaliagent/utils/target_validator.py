"""
Target Validation Module
Validates targets before scanning to ensure they're in scope
"""

import socket
import ipaddress
import re
from typing import Tuple, Optional, List
from rich.console import Console
import subprocess
import shutil

console = Console()

class TargetValidator:
    """Validate scanning targets"""
    
    def __init__(self):
        self.private_ranges = [
            ipaddress.ip_network('10.0.0.0/8'),
            ipaddress.ip_network('172.16.0.0/12'),
            ipaddress.ip_network('192.168.0.0/16'),
            ipaddress.ip_network('127.0.0.0/8'),  # Localhost
        ]
    
    def validate_target(self, target: str, allow_private: bool = True) -> Tuple[bool, str, Dict]:
        """
        Validate a target before scanning
        
        Returns:
            Tuple[bool, str, Dict]: (is_valid, message, details)
        """
        details = {
            "target": target,
            "type": None,
            "ip_address": None,
            "is_private": None,
            "is_reachable": None,
            "dns_resolved": None
        }
        
        # Check if target is an IP address
        try:
            ip = ipaddress.ip_address(target)
            details["type"] = "ip"
            details["ip_address"] = str(ip)
            details["is_private"] = ip.is_private
            
            # Check if private IP is allowed
            if ip.is_private and not allow_private:
                return False, f"Target {target} is a private IP address and private IPs are not allowed", details
            
            # Check if target is reachable
            is_reachable = self._check_reachable(target)
            details["is_reachable"] = is_reachable
            
            return True, "Valid IP address", details
            
        except ValueError:
            # Not an IP, try as hostname
            details["type"] = "hostname"
            
            # Validate hostname format
            if not self._is_valid_hostname(target):
                return False, f"Invalid hostname format: {target}", details
            
            # Try to resolve DNS
            try:
                ip_address = socket.gethostbyname(target)
                details["dns_resolved"] = True
                details["ip_address"] = ip_address
                
                # Check if resolved IP is private
                ip = ipaddress.ip_address(ip_address)
                details["is_private"] = ip.is_private
                
                if ip.is_private and not allow_private:
                    return False, f"Target {target} resolves to private IP {ip_address} and private IPs are not allowed", details
                
                # Check if target is reachable
                is_reachable = self._check_reachable(ip_address)
                details["is_reachable"] = is_reachable
                
                return True, f"Valid hostname (resolves to {ip_address})", details
                
            except socket.gaierror:
                details["dns_resolved"] = False
                return False, f"Cannot resolve hostname: {target}", details
    
    def _is_valid_hostname(self, hostname: str) -> bool:
        """Check if hostname has valid format"""
        if len(hostname) > 255:
            return False
        
        # Remove trailing dot if present
        if hostname.endswith('.'):
            hostname = hostname[:-1]
        
        # Hostname regex pattern
        pattern = re.compile(
            r'^(?=.{1,253}$)'  # Total length check
            r'(?!-)'  # Cannot start with hyphen
            r'[a-zA-Z0-9-]{1,63}'  # First label
            r'(?<!-)'  # Cannot end with hyphen
            r'(\.[a-zA-Z0-9-]{1,63}(?<!-))*$'  # Additional labels
        )
        
        return bool(pattern.match(hostname))
    
    def _check_reachable(self, target: str, timeout: int = 2) -> bool:
        """Check if target is reachable via ping"""
        param = '-n' if shutil.which('ping') and 'Windows' in str(subprocess.check_output(['ver'], shell=True)) else '-c'
        
        try:
            # Use ping to check if host is reachable
            result = subprocess.run(
                ['ping', param, '1', '-w' if param == '-n' else '-W', str(timeout * 1000 if param == '-n' else timeout), target],
                capture_output=True,
                timeout=timeout + 1
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def validate_network_range(self, network: str) -> Tuple[bool, str, Optional[ipaddress.IPv4Network]]:
        """
        Validate a network range in CIDR notation
        
        Returns:
            Tuple[bool, str, Optional[IPv4Network]]: (is_valid, message, network_object)
        """
        try:
            net = ipaddress.ip_network(network, strict=False)
            
            # Warn about large networks
            num_hosts = net.num_addresses
            if num_hosts > 1024:
                message = f"Warning: Network {network} contains {num_hosts} addresses. This may take a long time to scan."
                return True, message, net
            
            return True, f"Valid network range with {num_hosts} addresses", net
            
        except ValueError as e:
            return False, f"Invalid network range: {str(e)}", None
    
    def get_scope_confirmation(self, target: str, details: Dict) -> bool:
        """
        Ask user to confirm target is in scope
        
        Returns:
            bool: True if user confirms, False otherwise
        """
        console.print("\n[bold yellow]Target Validation[/bold yellow]")
        console.print(f"[bold]Target:[/bold] {target}")
        console.print(f"[bold]Type:[/bold] {details['type']}")
        
        if details['ip_address']:
            console.print(f"[bold]IP Address:[/bold] {details['ip_address']}")
        
        if details['is_private'] is not None:
            status = "Private" if details['is_private'] else "Public"
            color = "yellow" if details['is_private'] else "green"
            console.print(f"[bold]Network:[/bold] [{color}]{status}[/{color}]")
        
        if details['is_reachable'] is not None:
            status = "Reachable" if details['is_reachable'] else "Not Reachable"
            color = "green" if details['is_reachable'] else "red"
            console.print(f"[bold]Status:[/bold] [{color}]{status}[/{color}]")
        
        console.print("\n[bold red]IMPORTANT:[/bold red] Only scan systems you have explicit permission to test.")
        console.print("[yellow]Unauthorized scanning may be illegal in your jurisdiction.[/yellow]")
        
        response = console.input("\n[bold]Do you have authorization to scan this target? (yes/no): [/bold]").lower()
        
        return response in ['yes', 'y']
    
    def check_common_issues(self, target: str) -> List[str]:
        """
        Check for common target specification issues
        
        Returns:
            List[str]: List of warnings/issues found
        """
        issues = []
        
        # Check for localhost variants
        localhost_variants = ['localhost', '127.0.0.1', '::1', '0.0.0.0']
        if target.lower() in localhost_variants:
            issues.append("Warning: Target is localhost. You're scanning your own machine.")
        
        # Check for common cloud provider IPs (should get explicit confirmation)
        if target.startswith(('3.', '13.', '18.', '52.', '54.')):
            issues.append("Warning: Target appears to be an AWS IP. Ensure you have proper authorization.")
        
        # Check for common internal/infrastructure IPs
        try:
            ip = ipaddress.ip_address(target)
            if str(ip).endswith('.1'):
                issues.append("Info: Target ends in .1, likely a gateway/router.")
            if str(ip).endswith('.254'):
                issues.append("Info: Target ends in .254, commonly used for routers.")
        except ValueError:
            pass
        
        return issues


from typing import Dict

def display_validation_result(is_valid: bool, message: str, details: Dict):
    """Display validation results in a nice format"""
    if is_valid:
        console.print(f"\n[green]✓ {message}[/green]")
    else:
        console.print(f"\n[red]✗ {message}[/red]")
    
    if details.get('ip_address'):
        console.print(f"[bold]Resolved IP:[/bold] {details['ip_address']}")
    
    if details.get('is_private') is not None:
        network_type = "Private Network" if details['is_private'] else "Public Network"
        console.print(f"[bold]Network Type:[/bold] {network_type}")
    
    if details.get('is_reachable') is not None:
        reachability = "Reachable" if details['is_reachable'] else "Not Reachable"
        color = "green" if details['is_reachable'] else "yellow"
        console.print(f"[bold]Reachability:[/bold] [{color}]{reachability}[/{color}]")
