"""
Template Manager for KaliAI Command Templates
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path
import json
from rich.console import Console
from rich.table import Table
from rich.markdown import Markdown

console = Console()

@dataclass
class Template:
    """Command template structure"""
    name: str
    category: str
    description: str
    command: str
    parameters: Dict[str, str]
    examples: List[str]
    notes: str
    risk_level: str  # low, medium, high

class TemplateManager:
    """Manage command templates"""
    
    def __init__(self):
        self.templates: Dict[str, Template] = {}
        self._load_default_templates()
    
    def _load_default_templates(self):
        """Load built-in templates"""
        
        # Reconnaissance Templates
        self.add_template(Template(
            name="network-discovery",
            category="reconnaissance",
            description="Basic network discovery scan",
            command="nmap -sn {network}",
            parameters={"network": "Target network (e.g., 192.168.1.0/24)"},
            examples=[
                "nmap -sn 192.168.1.0/24",
                "nmap -sn 10.0.0.0/24"
            ],
            notes="Quick host discovery without port scanning. Stealthy and fast.",
            risk_level="low"
        ))
        
        self.add_template(Template(
            name="port-scan-basic",
            category="reconnaissance",
            description="Standard port scan of common ports",
            command="nmap -sS -T4 -p- {target}",
            parameters={"target": "Target IP or hostname"},
            examples=[
                "nmap -sS -T4 -p- 192.168.1.10",
                "nmap -sS -T4 -p- example.com"
            ],
            notes="SYN scan of all ports. May be detected by IDS.",
            risk_level="medium"
        ))
        
        self.add_template(Template(
            name="service-version-detection",
            category="reconnaissance",
            description="Detect service versions on open ports",
            command="nmap -sV -p {ports} {target}",
            parameters={
                "ports": "Ports to scan (e.g., 80,443 or 1-1000)",
                "target": "Target IP or hostname"
            },
            examples=[
                "nmap -sV -p 80,443 192.168.1.10",
                "nmap -sV -p 1-1000 example.com"
            ],
            notes="Active service fingerprinting. Useful for vulnerability assessment.",
            risk_level="medium"
        ))
        
        self.add_template(Template(
            name="os-detection",
            category="reconnaissance",
            description="Operating system detection",
            command="nmap -O {target}",
            parameters={"target": "Target IP or hostname"},
            examples=[
                "nmap -O 192.168.1.10",
                "nmap -O example.com"
            ],
            notes="Requires root/admin privileges. May be noisy.",
            risk_level="medium"
        ))
        
        # Web Application Templates
        self.add_template(Template(
            name="web-scan-basic",
            category="web-application",
            description="Basic web server vulnerability scan",
            command="nikto -h {target}",
            parameters={"target": "Target URL (e.g., http://example.com)"},
            examples=[
                "nikto -h http://example.com",
                "nikto -h https://192.168.1.10"
            ],
            notes="Comprehensive but noisy. Generates many requests.",
            risk_level="medium"
        ))
        
        self.add_template(Template(
            name="web-scan-ssl",
            category="web-application",
            description="Web scan with SSL/TLS testing",
            command="nikto -h {target} -ssl",
            parameters={"target": "Target URL"},
            examples=[
                "nikto -h https://example.com -ssl"
            ],
            notes="Includes SSL/TLS vulnerability testing.",
            risk_level="medium"
        ))
        
        self.add_template(Template(
            name="directory-enumeration",
            category="web-application",
            description="Discover hidden directories and files",
            command="dirb {target} {wordlist}",
            parameters={
                "target": "Target URL",
                "wordlist": "Path to wordlist (optional, uses default if empty)"
            },
            examples=[
                "dirb http://example.com",
                "dirb http://example.com /usr/share/wordlists/dirb/common.txt"
            ],
            notes="Brute-force directory discovery. Can be time-consuming.",
            risk_level="low"
        ))
        
        self.add_template(Template(
            name="wordpress-scan",
            category="web-application",
            description="WordPress vulnerability scanner",
            command="wpscan --url {target} --enumerate {options}",
            parameters={
                "target": "WordPress site URL",
                "options": "Enumeration options (e.g., p,t,u for plugins,themes,users)"
            },
            examples=[
                "wpscan --url http://example.com --enumerate p,t,u",
                "wpscan --url http://example.com --enumerate vp"
            ],
            notes="Specialized for WordPress sites. Very thorough.",
            risk_level="medium"
        ))
        
        # Database Testing Templates
        self.add_template(Template(
            name="sql-injection-test",
            category="database",
            description="Test for SQL injection vulnerabilities",
            command="sqlmap -u {url} --batch",
            parameters={"url": "Target URL with parameter (e.g., http://example.com/page?id=1)"},
            examples=[
                "sqlmap -u 'http://example.com/page.php?id=1' --batch",
                "sqlmap -u 'http://example.com/login.php' --data='user=admin&pass=test' --batch"
            ],
            notes="Automated SQL injection testing. May modify database.",
            risk_level="high"
        ))
        
        self.add_template(Template(
            name="sql-injection-enumerate-dbs",
            category="database",
            description="Enumerate databases after SQL injection",
            command="sqlmap -u {url} --dbs --batch",
            parameters={"url": "Target URL with vulnerable parameter"},
            examples=[
                "sqlmap -u 'http://example.com/page.php?id=1' --dbs --batch"
            ],
            notes="Lists available databases. Only use if injection confirmed.",
            risk_level="high"
        ))
        
        # Password Attacks Templates
        self.add_template(Template(
            name="ssh-bruteforce",
            category="password-attack",
            description="SSH password brute force attack",
            command="hydra -l {username} -P {passwordlist} {target} ssh",
            parameters={
                "username": "Target username",
                "passwordlist": "Path to password list",
                "target": "Target IP or hostname"
            },
            examples=[
                "hydra -l root -P /usr/share/wordlists/rockyou.txt 192.168.1.10 ssh",
                "hydra -l admin -P passwords.txt example.com ssh"
            ],
            notes="Aggressive attack. May lock accounts or trigger alerts.",
            risk_level="high"
        ))
        
        self.add_template(Template(
            name="http-form-bruteforce",
            category="password-attack",
            description="HTTP form brute force attack",
            command="hydra -l {username} -P {passwordlist} {target} http-post-form '{path}:{params}:{failure}'",
            parameters={
                "username": "Target username",
                "passwordlist": "Path to password list",
                "target": "Target domain",
                "path": "Login page path",
                "params": "POST parameters with ^USER^ and ^PASS^ placeholders",
                "failure": "String in response indicating failed login"
            },
            examples=[
                "hydra -l admin -P pass.txt example.com http-post-form '/login.php:user=^USER^&pass=^PASS^:Invalid'"
            ],
            notes="Complex syntax. Test carefully to avoid false positives.",
            risk_level="high"
        ))
        
        # Wireless Templates
        self.add_template(Template(
            name="wifi-monitor-mode",
            category="wireless",
            description="Enable monitor mode on wireless interface",
            command="airmon-ng start {interface}",
            parameters={"interface": "Wireless interface (e.g., wlan0)"},
            examples=[
                "airmon-ng start wlan0",
                "airmon-ng start wlan1"
            ],
            notes="Required before wireless attacks. May kill network processes.",
            risk_level="low"
        ))
        
        self.add_template(Template(
            name="wifi-scan",
            category="wireless",
            description="Scan for wireless networks",
            command="airodump-ng {interface}",
            parameters={"interface": "Monitor mode interface (e.g., wlan0mon)"},
            examples=[
                "airodump-ng wlan0mon"
            ],
            notes="Passive scanning. Press Ctrl+C to stop.",
            risk_level="low"
        ))
        
        # Network Sniffing Templates
        self.add_template(Template(
            name="capture-traffic",
            category="sniffing",
            description="Capture network traffic to file",
            command="wireshark -i {interface} -k -w {output}",
            parameters={
                "interface": "Network interface (e.g., eth0, wlan0)",
                "output": "Output file path (.pcap)"
            },
            examples=[
                "wireshark -i eth0 -k -w capture.pcap",
                "wireshark -i wlan0 -k -w traffic.pcap"
            ],
            notes="Requires root/admin. Captures all traffic on interface.",
            risk_level="low"
        ))
        
        # Exploitation Templates
        self.add_template(Template(
            name="metasploit-console",
            category="exploitation",
            description="Start Metasploit Framework console",
            command="msfconsole",
            parameters={},
            examples=["msfconsole"],
            notes="Interactive exploitation framework. Powerful and complex.",
            risk_level="high"
        ))
    
    def add_template(self, template: Template):
        """Add a template to the library"""
        self.templates[template.name] = template
    
    def get_template(self, name: str) -> Optional[Template]:
        """Get a template by name"""
        return self.templates.get(name)
    
    def list_templates(self, category: Optional[str] = None) -> List[Template]:
        """List all templates, optionally filtered by category"""
        if category:
            return [t for t in self.templates.values() if t.category == category]
        return list(self.templates.values())
    
    def get_categories(self) -> List[str]:
        """Get all unique categories"""
        return sorted(list(set(t.category for t in self.templates.values())))
    
    def display_templates(self, category: Optional[str] = None):
        """Display templates in a nice table"""
        templates = self.list_templates(category)
        
        if not templates:
            console.print("[yellow]No templates found.[/yellow]")
            return
        
        table = Table(title=f"Available Templates{f' ({category})' if category else ''}")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Category", style="magenta")
        table.add_column("Description", style="white")
        table.add_column("Risk", style="yellow")
        
        for template in sorted(templates, key=lambda t: (t.category, t.name)):
            risk_color = {
                "low": "green",
                "medium": "yellow",
                "high": "red"
            }.get(template.risk_level, "white")
            
            table.add_row(
                template.name,
                template.category,
                template.description,
                f"[{risk_color}]{template.risk_level.upper()}[/{risk_color}]"
            )
        
        console.print(table)
    
    def display_template_details(self, name: str):
        """Display detailed information about a template"""
        template = self.get_template(name)
        
        if not template:
            console.print(f"[red]Template '{name}' not found.[/red]")
            return
        
        risk_color = {
            "low": "green",
            "medium": "yellow",
            "high": "red"
        }.get(template.risk_level, "white")
        
        console.print(f"\n[bold cyan]Template: {template.name}[/bold cyan]")
        console.print(f"[bold]Category:[/bold] {template.category}")
        console.print(f"[bold]Risk Level:[/bold] [{risk_color}]{template.risk_level.upper()}[/{risk_color}]")
        console.print(f"\n[bold]Description:[/bold]\n{template.description}")
        
        console.print(f"\n[bold]Command Template:[/bold]")
        console.print(f"[green]{template.command}[/green]")
        
        if template.parameters:
            console.print(f"\n[bold]Parameters:[/bold]")
            for param, desc in template.parameters.items():
                console.print(f"  • {{{param}}}: {desc}")
        
        if template.examples:
            console.print(f"\n[bold]Examples:[/bold]")
            for example in template.examples:
                console.print(f"  [cyan]{example}[/cyan]")
        
        if template.notes:
            console.print(f"\n[bold]Notes:[/bold]")
            console.print(f"[yellow]{template.notes}[/yellow]")
    
    def generate_command(self, name: str, params: Dict[str, str]) -> Optional[str]:
        """Generate a command from a template with given parameters"""
        template = self.get_template(name)
        
        if not template:
            return None
        
        command = template.command
        for param, value in params.items():
            command = command.replace(f"{{{param}}}", value)
        
        return command
    
    def save_custom_template(self, template: Template, filepath: Path):
        """Save a custom template to a file"""
        template_dict = {
            "name": template.name,
            "category": template.category,
            "description": template.description,
            "command": template.command,
            "parameters": template.parameters,
            "examples": template.examples,
            "notes": template.notes,
            "risk_level": template.risk_level
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(template_dict, f, indent=2)
        
        console.print(f"[green]Template saved to {filepath}[/green]")
    
    def load_custom_template(self, filepath: Path) -> Optional[Template]:
        """Load a custom template from a file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            template = Template(**data)
            self.add_template(template)
            console.print(f"[green]Template '{template.name}' loaded successfully[/green]")
            return template
            
        except Exception as e:
            console.print(f"[red]Error loading template: {str(e)}[/red]")
            return None
