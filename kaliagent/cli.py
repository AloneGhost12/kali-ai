import click
from rich.console import Console
from rich.prompt import Prompt
from .core.agent import KaliAgent
from .config.settings import settings
from .config.config_manager import ConfigManager
from .templates import TemplateManager
import os
import sys

console = Console()
config_manager = ConfigManager()

@click.group()
def cli():
    """KaliAI - Ethical Hacking Assistant for Kali Linux"""
    pass

@cli.command()
@click.option('--api-key', help='API key (OpenAI or Google)')
@click.option('--provider', type=click.Choice(['openai', 'gemini'], case_sensitive=False), help='API provider (openai or gemini)')
@click.option('--safe-mode/--no-safe-mode', default=None, help='Enable/disable safe mode (no command execution)')
@click.option('--confirm/--no-confirm', default=None, help='Require confirmation before executing commands')
@click.option('--model', help='Model to use (e.g., gpt-3.5-turbo, gpt-4, gemini-2.0-flash-exp)')
@click.option('--show', is_flag=True, help='Show current configuration')
def configure(api_key, provider, safe_mode, confirm, model, show):
    """Configure KaliAI settings"""
    
    if show:
        # Show current configuration
        console.print("\n[bold cyan]Current Configuration:[/bold cyan]\n")
        
        # Check which provider is configured
        openai_key = config_manager.get('OPENAI_API_KEY') or os.getenv('OPENAI_API_KEY')
        google_key = config_manager.get('GOOGLE_API_KEY') or os.getenv('GOOGLE_API_KEY')
        
        if google_key:
            masked_key = google_key[:10] + '...' + google_key[-4:] if len(google_key) > 14 else '***'
            console.print(f"[bold]Provider:[/bold] Google Gemini")
            console.print(f"[bold]API Key:[/bold] {masked_key}")
        elif openai_key:
            masked_key = openai_key[:10] + '...' + openai_key[-4:] if len(openai_key) > 14 else '***'
            console.print(f"[bold]Provider:[/bold] OpenAI")
            console.print(f"[bold]API Key:[/bold] {masked_key}")
        else:
            console.print("[bold]API Key:[/bold] [red]Not configured[/red]")
        
        # Model
        current_model = config_manager.get('MODEL_ID', settings.MODEL_ID)
        console.print(f"[bold]Model:[/bold] {current_model}")
        
        # Safe Mode
        current_safe_mode = config_manager.get('SAFE_MODE', settings.SAFE_MODE)
        status = "[green]Enabled[/green]" if current_safe_mode else "[red]Disabled[/red]"
        console.print(f"[bold]Safe Mode:[/bold] {status}")
        
        # Confirmation
        current_confirm = config_manager.get('REQUIRE_CONFIRMATION', settings.REQUIRE_CONFIRMATION)
        status = "[green]Required[/green]" if current_confirm else "[yellow]Not Required[/yellow]"
        console.print(f"[bold]Command Confirmation:[/bold] {status}")
        
        console.print(f"\n[italic]Config file: {config_manager.config_file}[/italic]\n")
        return
    
    # Update API key
    if api_key:
        # Auto-detect provider if not specified
        if provider is None:
            if api_key.startswith('AIza'):
                provider = 'gemini'
            elif api_key.startswith('sk-'):
                provider = 'openai'
        
        if provider == 'gemini':
            # Clear OpenAI key if switching to Gemini
            config_manager.delete('OPENAI_API_KEY')
            config_manager.set('GOOGLE_API_KEY', api_key)
            os.environ['GOOGLE_API_KEY'] = api_key
            console.print("[green]✓ Google Gemini API key configured successfully[/green]")
        else:
            # Clear Gemini key if switching to OpenAI
            config_manager.delete('GOOGLE_API_KEY')
            config_manager.set('OPENAI_API_KEY', api_key)
            os.environ['OPENAI_API_KEY'] = api_key
            console.print("[green]✓ OpenAI API key configured successfully[/green]")
    
    # Update model
    if model:
        config_manager.set('MODEL_ID', model)
        console.print(f"[green]✓ Model set to: {model}[/green]")
    
    # Update settings
    if safe_mode is not None:
        config_manager.set('SAFE_MODE', safe_mode)
        settings.SAFE_MODE = safe_mode
        status = "Enabled" if safe_mode else "Disabled"
        console.print(f"[green]✓ Safe mode: {status}[/green]")
    
    if confirm is not None:
        config_manager.set('REQUIRE_CONFIRMATION', confirm)
        settings.REQUIRE_CONFIRMATION = confirm
        status = "Required" if confirm else "Not required"
        console.print(f"[green]✓ Command confirmation: {status}[/green]")
    
    # If no options provided, show help
    if not any([api_key, safe_mode is not None, confirm is not None, model, provider]):
        console.print("[yellow]No configuration changes specified.[/yellow]")
        console.print("[italic]Use 'kaliagent configure --show' to see current settings[/italic]")
        console.print("[italic]Use 'kaliagent configure --help' for options[/italic]")

@cli.command()
def interactive():
    """Start interactive ethical hacking assistant"""
    try:
        # Load API key from config or environment
        api_key = config_manager.get('OPENAI_API_KEY') or os.getenv('OPENAI_API_KEY')
        google_key = config_manager.get('GOOGLE_API_KEY') or os.getenv('GOOGLE_API_KEY')
        
        if not api_key and not google_key:
            console.print("[red]Error: No API key found.[/red]")
            console.print("[yellow]Use 'kaliagent configure --api-key YOUR_KEY --provider [openai|gemini]' to set it.[/yellow]")
            sys.exit(1)
        
        # Set environment variables for the session
        if google_key:
            os.environ['GOOGLE_API_KEY'] = google_key
        if api_key:
            os.environ['OPENAI_API_KEY'] = api_key
        
        # Load other settings from config
        model_id = config_manager.get('MODEL_ID')
        if model_id:
            settings.MODEL_ID = model_id
        safe_mode = config_manager.get('SAFE_MODE')
        if safe_mode is not None:
            settings.SAFE_MODE = safe_mode
        require_conf = config_manager.get('REQUIRE_CONFIRMATION')
        if require_conf is not None:
            settings.REQUIRE_CONFIRMATION = require_conf
            
        provider = "Google Gemini" if google_key else f"OpenAI ({settings.MODEL_ID})"
        console.print("[bold blue]KaliAI - Ethical Hacking Assistant[/bold blue]")
        console.print(f"[italic]Model: {provider} | Safe Mode: {'ON' if settings.SAFE_MODE else 'OFF'}[/italic]")
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
