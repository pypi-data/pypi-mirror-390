"""
Remove commands for ABI Core CLI
"""

import click
import shutil
from pathlib import Path
from rich.prompt import Confirm

from .utils import console, update_runtime_config


@click.group()
def remove():
    """Remove components from ABI project
    
    Remove services, agents, and other components from your ABI project.
    This will delete files, update configurations, and clean up Docker Compose.
    
    \b
    Available subcommands:
      service    Remove a service (semantic-layer, guardian, etc.)
      agent      Remove an agent from the project
    
    Use --force to skip confirmation prompts.
    """
    pass


@remove.command("service")
@click.argument('service_name')
@click.option('--force', '-f', is_flag=True, help='Force removal without confirmation')
def remove_service(service_name, force):
    """Remove a service from the project
    
    Removes a service completely from your ABI project, including:
    - Service directory and all files
    - Docker Compose configuration
    - Runtime configuration
    
    \b
    SERVICE_NAME: Name of the service to remove
    
    \b
    Common service names:
      semantic_layer    AI agent discovery and routing service
      guardian          Security policy enforcement service
    
    \b
    Examples:
      abi-core remove service semantic_layer
      abi-core remove service guardian --force
    """
    
    # Check if we're in an ABI project
    if not Path('.abi').exists():
        console.print("❌ Not in an ABI project directory. Run 'abi-core create project' first.", style="red")
        return
    
    # Normalize service name
    service_name = service_name.lower().replace('-', '_')
    service_dir = Path('services') / service_name
    
    if not service_dir.exists():
        console.print(f"❌ Service '{service_name}' does not exist", style="red")
        console.print("📋 Available services:", style="blue")
        services_dir = Path('services')
        if services_dir.exists():
            for service_path in services_dir.iterdir():
                if service_path.is_dir():
                    console.print(f"  - {service_path.name}", style="dim")
        return
    
    # Show what will be removed
    console.print(f"🗑️  About to remove service: {service_name}", style="yellow")
    console.print(f"📁 Location: {service_dir}", style="blue")
    
    # Check if it's in compose file
    compose_files = ['compose.yaml', 'docker-compose.yml']
    compose_file = None
    for cf in compose_files:
        if Path(cf).exists():
            compose_file = Path(cf)
            break
    
    if compose_file:
        console.print(f"🐳 Will also remove from {compose_file.name}", style="blue")
    
    # Confirmation
    if not force:
        if not Confirm.ask("Are you sure you want to remove this service?", default=False):
            console.print("❌ Operation cancelled", style="yellow")
            return
    
    from rich.progress import Progress, SpinnerColumn, TextColumn
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        task = progress.add_task(f"Removing {service_name} service...", total=None)
        
        # Remove service directory
        progress.update(task, description="Removing service files...")
        shutil.rmtree(service_dir)
        
        # Remove from compose file
        if compose_file:
            progress.update(task, description="Updating Docker Compose...")
            _remove_service_from_compose(compose_file, service_name)
        
        # Remove from runtime configuration
        progress.update(task, description="Updating configuration...")
        _remove_from_runtime_config(service_name)
        
        progress.update(task, description="Service removed successfully!", completed=True)
    
    console.print(f"\n✅ Service '{service_name}' removed successfully!", style="green")
    console.print("💡 Run 'abi-core run' to restart remaining services", style="yellow")


@remove.command("agent")
@click.argument('agent_name')
@click.option('--force', '-f', is_flag=True, help='Force removal without confirmation')
def remove_agent(agent_name, force):
    """Remove an agent from the project
    
    Removes an agent completely from your ABI project, including:
    - Agent directory and all files
    - Runtime configuration
    - Agent cards (if any)
    
    \b
    AGENT_NAME: Name of the agent to remove
    
    \b
    Examples:
      abi-core remove agent my_agent
      abi-core remove agent planner --force
    """
    
    # Check if we're in an ABI project
    if not Path('.abi').exists():
        console.print("❌ Not in an ABI project directory. Run 'abi-core create project' first.", style="red")
        return
    
    # Normalize agent name
    agent_name = agent_name.lower().replace('-', '_')
    agent_dir = Path('agents') / agent_name
    
    if not agent_dir.exists():
        console.print(f"❌ Agent '{agent_name}' does not exist", style="red")
        console.print("📋 Available agents:", style="blue")
        agents_dir = Path('agents')
        if agents_dir.exists():
            for agent_path in agents_dir.iterdir():
                if agent_path.is_dir():
                    console.print(f"  - {agent_path.name}", style="dim")
        return
    
    # Show what will be removed
    console.print(f"🗑️  About to remove agent: {agent_name}", style="yellow")
    console.print(f"📁 Location: {agent_dir}", style="blue")
    
    # Confirmation
    if not force:
        if not Confirm.ask("Are you sure you want to remove this agent?", default=False):
            console.print("❌ Operation cancelled", style="yellow")
            return
    
    from rich.progress import Progress, SpinnerColumn, TextColumn
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        task = progress.add_task(f"Removing {agent_name} agent...", total=None)
        
        # Remove agent directory
        progress.update(task, description="Removing agent files...")
        shutil.rmtree(agent_dir)
        
        # Remove from runtime configuration
        progress.update(task, description="Updating configuration...")
        _remove_from_runtime_config(agent_name, config_type='agents')
        
        progress.update(task, description="Agent removed successfully!", completed=True)
    
    console.print(f"\n✅ Agent '{agent_name}' removed successfully!", style="green")


def _remove_service_from_compose(compose_file, service_name):
    """Remove service from docker-compose.yml"""
    import yaml
    
    try:
        with open(compose_file, 'r') as f:
            compose_data = yaml.safe_load(f) or {}
        
        services = compose_data.get('services', {})
        project_name = Path.cwd().name
        
        # Try different service name patterns
        service_keys_to_remove = []
        possible_keys = [
            service_name,
            service_name.replace('_', '-'),
            f"{project_name}-{service_name}",
            f"{project_name}-{service_name.replace('_', '-')}"
        ]
        
        for key in possible_keys:
            if key in services:
                service_keys_to_remove.append(key)
        
        # Remove found services
        for key in service_keys_to_remove:
            del services[key]
            console.print(f"🐳 Removed '{key}' from {compose_file.name}", style="green")
        
        # Write updated compose file
        if service_keys_to_remove:
            with open(compose_file, 'w') as f:
                yaml.dump(compose_data, f, default_flow_style=False, sort_keys=False)
        
    except Exception as e:
        console.print(f"⚠️  Warning: Could not update {compose_file.name}: {e}", style="yellow")


def _remove_from_runtime_config(item_name, config_type='services'):
    """Remove item from runtime configuration"""
    try:
        runtime_file = Path('.abi') / 'runtime.yaml'
        if not runtime_file.exists():
            return
        
        import yaml
        with open(runtime_file, 'r') as f:
            config = yaml.safe_load(f) or {}
        
        if config_type in config and item_name in config[config_type]:
            del config[config_type][item_name]
            
            with open(runtime_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
            
            console.print(f"🔧 Removed '{item_name}' from runtime configuration", style="green")
    
    except Exception as e:
        console.print(f"⚠️  Warning: Could not update runtime configuration: {e}", style="yellow")