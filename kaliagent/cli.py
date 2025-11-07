import click
from rich.console import Console
from rich.prompt import Prompt
from .core.agent import KaliAgent
from .config.settings import settings
from .templates import TemplateManager
import os
import sys

console = Console()

@click.group()
def cli():
    """KaliAI - Ethical Hacking Assistant for Kali Linux"""
    pass

@cli.command()
@click.option('--api-key', help='OpenAI API key')
@click.option('--safe-mode/--no-safe-mode', default=True, help='Enable/disable safe mode (no command execution)')
@click.option('--confirm/--no-confirm', default=True, help='Require confirmation before executing commands')
def configure(api_key, safe_mode, confirm):
    """Configure KaliAI settings"""
    if api_key:
        os.environ['OPENAI_API_KEY'] = api_key
        console.print("[green]API key configured successfully[/green]")
    
    # Update settings
    settings.SAFE_MODE = safe_mode
    settings.REQUIRE_CONFIRMATION = confirm
    
    console.print(f"[green]Safe mode: {'Enabled' if safe_mode else 'Disabled'}[/green]")
    console.print(f"[green]Command confirmation: {'Required' if confirm else 'Not required'}[/green]")

@cli.command()
def interactive():
    """Start interactive ethical hacking assistant"""
    try:
        if not os.getenv('OPENAI_API_KEY'):
            console.print("[red]Error: OpenAI API key not found. Use 'kaliagent configure --api-key YOUR_KEY' to set it.[/red]")
            sys.exit(1)
            
        console.print("[bold blue]KaliAI - Ethical Hacking Assistant[/bold blue]")
        console.print("[italic]Type 'exit' to quit[/italic]\n")
        
        agent = KaliAgent()
        
        while True:
            try:
                user_input = input("🛡️ > ")
                if user_input.lower() == 'exit':
                    break
                
                agent.chat(user_input)
                print()
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                console.print(f"[red]Error: {str(e)}[/red]")
        
        console.print("\n[bold blue]Goodbye! Happy ethical hacking![/bold blue]")
        
    except Exception as e:
        console.print(f"[red]Fatal error: {str(e)}[/red]")
        sys.exit(1)

@cli.command()
@click.argument('tool', type=click.Choice(settings.ALLOWED_TOOLS, case_sensitive=False))
def learn(tool):
    """Learn about a specific Kali Linux tool"""
    try:
        agent = KaliAgent()
        
        # Generate prompt to learn about the tool
        prompt = f"Teach me about the {tool} tool in Kali Linux, including its purpose, basic usage, common flags, and security considerations."
        
        # Process through the agent
        agent.chat(prompt)
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)

@cli.command()
@click.argument('command', type=str)
def analyze(command):
    """Analyze a Kali Linux command without executing it"""
    try:
        agent = KaliAgent()
        
        # Force safe mode for analysis
        settings.SAFE_MODE = True
        
        # Generate prompt to analyze the command
        prompt = f"Analyze this Kali Linux command: {command}"
        
        # Process through the agent
        agent.chat(prompt)
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)

@cli.group()
def templates():
    """Manage command templates"""
    pass

@templates.command('list')
@click.option('--category', '-c', help='Filter by category')
def list_templates(category):
    """List available command templates"""
    try:
        manager = TemplateManager()
        
        if category:
            console.print(f"\n[bold]Templates in category: {category}[/bold]\n")
        else:
            console.print("\n[bold]All Available Templates[/bold]\n")
            console.print("[italic]Use --category to filter by specific category[/italic]\n")
        
        manager.display_templates(category)
        
        console.print(f"\n[bold]Categories:[/bold] {', '.join(manager.get_categories())}")
        console.print("\n[italic]Use 'kaliagent templates show <name>' for details[/italic]")
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)

@templates.command('show')
@click.argument('name', type=str)
def show_template(name):
    """Show detailed information about a template"""
    try:
        manager = TemplateManager()
        manager.display_template_details(name)
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)

@templates.command('use')
@click.argument('name', type=str)
@click.option('--params', '-p', multiple=True, help='Parameters in format key=value')
@click.option('--execute', '-e', is_flag=True, help='Execute the command (respects safe mode)')
def use_template(name, params, execute):
    """Use a command template"""
    try:
        manager = TemplateManager()
        template = manager.get_template(name)
        
        if not template:
            console.print(f"[red]Template '{name}' not found.[/red]")
            console.print("[yellow]Use 'kaliagent templates list' to see available templates[/yellow]")
            sys.exit(1)
        
        # Show template details
        manager.display_template_details(name)
        
        # Parse parameters
        param_dict = {}
        for param in params:
            if '=' not in param:
                console.print(f"[red]Invalid parameter format: {param}[/red]")
                console.print("[yellow]Use format: key=value[/yellow]")
                sys.exit(1)
            key, value = param.split('=', 1)
            param_dict[key] = value
        
        # Check if all required parameters are provided
        missing_params = set(template.parameters.keys()) - set(param_dict.keys())
        if missing_params:
            console.print(f"\n[yellow]Missing required parameters:[/yellow]")
            for param in missing_params:
                console.print(f"  • {param}: {template.parameters[param]}")
            console.print(f"\n[italic]Example: kaliagent templates use {name} -p param1=value1 -p param2=value2[/italic]")
            sys.exit(1)
        
        # Generate command
        command = manager.generate_command(name, param_dict)
        
        console.print(f"\n[bold green]Generated Command:[/bold green]")
        console.print(f"[cyan]{command}[/cyan]")
        
        # Execute if requested
        if execute:
            console.print(f"\n[yellow]Executing command...[/yellow]")
            agent = KaliAgent()
            agent.chat(f"Execute this command: {command}")
        else:
            console.print(f"\n[yellow]Command not executed. Use --execute flag to run it.[/yellow]")
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)

@templates.command('categories')
def list_categories():
    """List all template categories"""
    try:
        manager = TemplateManager()
        categories = manager.get_categories()
        
        console.print("\n[bold]Template Categories:[/bold]\n")
        for cat in categories:
            count = len(manager.list_templates(cat))
            console.print(f"  • [cyan]{cat}[/cyan] ({count} templates)")
        
        console.print(f"\n[italic]Use 'kaliagent templates list --category <name>' to filter[/italic]")
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)

def main():
    """Main entry point for the CLI"""
    cli()
