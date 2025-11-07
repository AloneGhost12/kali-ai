"""
Playbook System for KaliAI
Save, load, and replay command sequences
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import json
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

@dataclass
class PlaybookStep:
    """Single step in a playbook"""
    command: str
    description: str
    expected_outcome: str
    notes: str = ""
    timestamp: Optional[str] = None
    output: Optional[str] = None
    success: Optional[bool] = None

@dataclass
class Playbook:
    """Collection of security testing steps"""
    name: str
    description: str
    author: str
    created: str
    category: str
    target_type: str  # network, web-app, database, wireless, etc.
    steps: List[PlaybookStep] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    notes: str = ""
    
    def add_step(self, step: PlaybookStep):
        """Add a step to the playbook"""
        self.steps.append(step)
    
    def to_dict(self) -> Dict:
        """Convert playbook to dictionary"""
        return {
            "name": self.name,
            "description": self.description,
            "author": self.author,
            "created": self.created,
            "category": self.category,
            "target_type": self.target_type,
            "tags": self.tags,
            "notes": self.notes,
            "steps": [
                {
                    "command": step.command,
                    "description": step.description,
                    "expected_outcome": step.expected_outcome,
                    "notes": step.notes,
                    "timestamp": step.timestamp,
                    "output": step.output,
                    "success": step.success
                }
                for step in self.steps
            ]
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Playbook':
        """Create playbook from dictionary"""
        steps = [PlaybookStep(**step_data) for step_data in data.get('steps', [])]
        playbook = cls(
            name=data['name'],
            description=data['description'],
            author=data['author'],
            created=data['created'],
            category=data['category'],
            target_type=data['target_type'],
            tags=data.get('tags', []),
            notes=data.get('notes', '')
        )
        playbook.steps = steps
        return playbook


class PlaybookManager:
    """Manage security testing playbooks"""
    
    def __init__(self, playbook_dir: Path):
        self.playbook_dir = playbook_dir
        self.playbook_dir.mkdir(parents=True, exist_ok=True)
        self.current_playbook: Optional[Playbook] = None
    
    def create_playbook(self, name: str, description: str, author: str, 
                       category: str, target_type: str, tags: List[str] = None) -> Playbook:
        """Create a new playbook"""
        playbook = Playbook(
            name=name,
            description=description,
            author=author,
            created=datetime.now().isoformat(),
            category=category,
            target_type=target_type,
            tags=tags or []
        )
        self.current_playbook = playbook
        console.print(f"[green]Created new playbook: {name}[/green]")
        return playbook
    
    def save_playbook(self, playbook: Playbook, filename: Optional[str] = None):
        """Save playbook to file"""
        if filename is None:
            filename = f"{playbook.name.replace(' ', '_').lower()}.json"
        
        filepath = self.playbook_dir / filename
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(playbook.to_dict(), f, indent=2)
            console.print(f"[green]Playbook saved to: {filepath}[/green]")
        except Exception as e:
            console.print(f"[red]Error saving playbook: {str(e)}[/red]")
    
    def load_playbook(self, filename: str) -> Optional[Playbook]:
        """Load playbook from file"""
        filepath = self.playbook_dir / filename
        
        if not filepath.exists():
            console.print(f"[red]Playbook file not found: {filepath}[/red]")
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            playbook = Playbook.from_dict(data)
            self.current_playbook = playbook
            console.print(f"[green]Loaded playbook: {playbook.name}[/green]")
            return playbook
            
        except Exception as e:
            console.print(f"[red]Error loading playbook: {str(e)}[/red]")
            return None
    
    def list_playbooks(self) -> List[Path]:
        """List all available playbooks"""
        return list(self.playbook_dir.glob('*.json'))
    
    def display_playbooks(self):
        """Display all available playbooks in a table"""
        playbooks = self.list_playbooks()
        
        if not playbooks:
            console.print("[yellow]No playbooks found.[/yellow]")
            console.print(f"[italic]Playbooks are stored in: {self.playbook_dir}[/italic]")
            return
        
        table = Table(title="Available Playbooks")
        table.add_column("Filename", style="cyan", no_wrap=True)
        table.add_column("Name", style="magenta")
        table.add_column("Category", style="yellow")
        table.add_column("Steps", style="green")
        
        for filepath in playbooks:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                table.add_row(
                    filepath.name,
                    data.get('name', 'Unknown'),
                    data.get('category', 'N/A'),
                    str(len(data.get('steps', [])))
                )
            except Exception:
                continue
        
        console.print(table)
    
    def display_playbook_details(self, playbook: Playbook):
        """Display detailed information about a playbook"""
        console.print(f"\n[bold cyan]Playbook: {playbook.name}[/bold cyan]")
        console.print(f"[bold]Description:[/bold] {playbook.description}")
        console.print(f"[bold]Author:[/bold] {playbook.author}")
        console.print(f"[bold]Created:[/bold] {playbook.created}")
        console.print(f"[bold]Category:[/bold] {playbook.category}")
        console.print(f"[bold]Target Type:[/bold] {playbook.target_type}")
        
        if playbook.tags:
            console.print(f"[bold]Tags:[/bold] {', '.join(playbook.tags)}")
        
        if playbook.notes:
            console.print(f"\n[bold]Notes:[/bold]\n{playbook.notes}")
        
        console.print(f"\n[bold]Steps ({len(playbook.steps)}):[/bold]")
        for i, step in enumerate(playbook.steps, 1):
            console.print(f"\n[bold yellow]{i}. {step.description}[/bold yellow]")
            console.print(f"   [cyan]Command:[/cyan] {step.command}")
            console.print(f"   [green]Expected:[/green] {step.expected_outcome}")
            if step.notes:
                console.print(f"   [italic]Notes: {step.notes}[/italic]")
    
    def add_step_to_current(self, command: str, description: str, 
                           expected_outcome: str, notes: str = ""):
        """Add a step to the current playbook"""
        if not self.current_playbook:
            console.print("[red]No active playbook. Create or load one first.[/red]")
            return False
        
        step = PlaybookStep(
            command=command,
            description=description,
            expected_outcome=expected_outcome,
            notes=notes
        )
        self.current_playbook.add_step(step)
        console.print(f"[green]Added step {len(self.current_playbook.steps)} to playbook[/green]")
        return True
    
    def execute_playbook(self, playbook: Playbook, agent, start_step: int = 1, 
                        interactive: bool = True):
        """Execute a playbook"""
        console.print(f"\n[bold]Executing Playbook: {playbook.name}[/bold]")
        console.print(f"[italic]{playbook.description}[/italic]\n")
        
        if interactive:
            console.print("[yellow]Interactive mode: You'll be prompted before each step[/yellow]\n")
        
        for i, step in enumerate(playbook.steps[start_step-1:], start_step):
            console.print(f"\n[bold cyan]Step {i}/{len(playbook.steps)}:[/bold cyan] {step.description}")
            console.print(f"[bold]Command:[/bold] [green]{step.command}[/green]")
            console.print(f"[bold]Expected Outcome:[/bold] {step.expected_outcome}")
            
            if step.notes:
                console.print(f"[italic]Notes: {step.notes}[/italic]")
            
            if interactive:
                choice = console.input("\n[yellow]Execute this step? (y/n/s=skip/q=quit): [/yellow]").lower()
                
                if choice == 'q':
                    console.print("[yellow]Playbook execution cancelled.[/yellow]")
                    break
                elif choice == 's':
                    console.print("[yellow]Skipping step...[/yellow]")
                    continue
                elif choice != 'y':
                    console.print("[yellow]Skipping step...[/yellow]")
                    continue
            
            # Execute the step
            try:
                console.print("\n[bold]Executing...[/bold]")
                step.timestamp = datetime.now().isoformat()
                
                # Use the agent to execute
                agent.chat(f"Execute this command: {step.command}")
                
                step.success = True
                console.print("[green]✓ Step completed successfully[/green]")
                
            except Exception as e:
                step.success = False
                step.output = str(e)
                console.print(f"[red]✗ Step failed: {str(e)}[/red]")
                
                if interactive:
                    cont = console.input("[yellow]Continue with next step? (y/n): [/yellow]").lower()
                    if cont != 'y':
                        break
        
        console.print(f"\n[bold green]Playbook execution completed![/bold green]")
    
    def export_playbook_to_markdown(self, playbook: Playbook, filepath: Path):
        """Export playbook to markdown format"""
        md_content = f"# {playbook.name}\n\n"
        md_content += f"**Description:** {playbook.description}\n\n"
        md_content += f"**Author:** {playbook.author}\n\n"
        md_content += f"**Created:** {playbook.created}\n\n"
        md_content += f"**Category:** {playbook.category}\n\n"
        md_content += f"**Target Type:** {playbook.target_type}\n\n"
        
        if playbook.tags:
            md_content += f"**Tags:** {', '.join(playbook.tags)}\n\n"
        
        if playbook.notes:
            md_content += f"## Notes\n\n{playbook.notes}\n\n"
        
        md_content += f"## Steps\n\n"
        
        for i, step in enumerate(playbook.steps, 1):
            md_content += f"### Step {i}: {step.description}\n\n"
            md_content += f"**Command:**\n```bash\n{step.command}\n```\n\n"
            md_content += f"**Expected Outcome:** {step.expected_outcome}\n\n"
            
            if step.notes:
                md_content += f"**Notes:** {step.notes}\n\n"
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(md_content)
            console.print(f"[green]Playbook exported to: {filepath}[/green]")
        except Exception as e:
            console.print(f"[red]Error exporting playbook: {str(e)}[/red]")


def create_default_playbooks(manager: PlaybookManager):
    """Create some default playbooks"""
    
    # Web Application Penetration Test Playbook
    web_app_playbook = manager.create_playbook(
        name="Web Application Pentest",
        description="Standard web application security assessment workflow",
        author="KaliAI",
        category="web-application",
        target_type="web-app",
        tags=["web", "owasp", "standard"]
    )
    
    web_app_playbook.add_step(PlaybookStep(
        command="nmap -sV -p 80,443,8080,8443 {target}",
        description="Identify web services and versions",
        expected_outcome="List of open web ports and running services",
        notes="Replace {target} with actual target IP or domain"
    ))
    
    web_app_playbook.add_step(PlaybookStep(
        command="nikto -h {target}",
        description="Scan for web server vulnerabilities",
        expected_outcome="List of potential vulnerabilities and misconfigurations",
        notes="This scan is noisy and will be logged"
    ))
    
    web_app_playbook.add_step(PlaybookStep(
        command="dirb http://{target}",
        description="Enumerate directories and files",
        expected_outcome="Discovery of hidden directories, files, and endpoints",
        notes="Can take time depending on wordlist size"
    ))
    
    web_app_playbook.add_step(PlaybookStep(
        command="sqlmap -u '{target_url}' --batch --risk=1 --level=1",
        description="Test for SQL injection vulnerabilities",
        expected_outcome="Identification of SQL injection points",
        notes="Start with low risk/level, increase if needed"
    ))
    
    manager.save_playbook(web_app_playbook)
    
    # Network Reconnaissance Playbook
    network_recon_playbook = manager.create_playbook(
        name="Network Reconnaissance",
        description="Comprehensive network discovery and mapping",
        author="KaliAI",
        category="reconnaissance",
        target_type="network",
        tags=["recon", "network", "discovery"]
    )
    
    network_recon_playbook.add_step(PlaybookStep(
        command="nmap -sn {network}/24",
        description="Discover live hosts on the network",
        expected_outcome="List of active IP addresses",
        notes="Replace {network} with target network (e.g., 192.168.1.0)"
    ))
    
    network_recon_playbook.add_step(PlaybookStep(
        command="nmap -sS -p- {target}",
        description="Scan all TCP ports on discovered hosts",
        expected_outcome="Complete list of open ports",
        notes="This can take a while for all 65535 ports"
    ))
    
    network_recon_playbook.add_step(PlaybookStep(
        command="nmap -sV -sC -p {ports} {target}",
        description="Service version and script scanning",
        expected_outcome="Detailed service information and vulnerability hints",
        notes="Use ports discovered in previous step"
    ))
    
    network_recon_playbook.add_step(PlaybookStep(
        command="nmap -O {target}",
        description="Operating system detection",
        expected_outcome="OS identification and version",
        notes="Requires root/admin privileges"
    ))
    
    manager.save_playbook(network_recon_playbook)
    
    console.print("[green]Default playbooks created successfully![/green]")
