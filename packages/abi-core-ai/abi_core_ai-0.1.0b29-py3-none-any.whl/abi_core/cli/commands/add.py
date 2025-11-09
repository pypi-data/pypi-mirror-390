"""
Add commands for ABI Core CLI
"""

import click
from pathlib import Path
from rich.prompt import Prompt

from .utils import console, update_runtime_config, render_template_content


@click.group()
def add():
    """Add components to existing ABI project"""
    pass


@add.command("agent")
@click.option('--name', '-n', required=True, help='Agent name')
@click.option('--description', '-d', help='Agent description')
@click.option('--model', default='llama3.2:3b', help='LLM model to use')
@click.option('--with-web-interface', is_flag=True, help='Include web interface for HTTP/SSE access')
def add_agent(name, description, model, with_web_interface):
    """Add a new agent to the project"""
    
    # Check if we're in an ABI project
    if not Path('.abi').exists():
        console.print("❌ Not in an ABI project directory. Run 'abi-core create project' first.", style="red")
        return
    
    if not description:
        description = Prompt.ask("Agent description", default=f"Specialized agent for {name}")
    
    agent_dir = Path('agents') / name.lower().replace(' ', '_').replace('-', '_')
    
    if agent_dir.exists():
        console.print(f"❌ Agent '{name}' already exists", style="red")
        return
    
    from rich.progress import Progress, SpinnerColumn, TextColumn
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        task = progress.add_task("Creating agent...", total=None)
        
        # Create agent directory
        agent_dir.mkdir(parents=True)
        (agent_dir / '__init__.py').touch()
        
        # Auto-assign ports
        agent_port = _get_next_available_port(8000)
        web_interface_port = _get_next_available_port(agent_port + 1) if with_web_interface else None
        
        # Template context
        agent_file_name = f'agent_{name.lower().replace(" ", "_").replace("-", "_")}'
        context = {
            'agent_name': name.lower().replace(' ', '_').replace('-', '_'),
            'agent_class_name': name.replace(' ', '').replace('-', '').replace('_', '') + 'Agent',
            'agent_description': description,
            'agent_display_name': name,
            'agent_file_name': agent_file_name,
            'model_name': model,
            'agent_port': agent_port,
            'with_web_interface': with_web_interface,
            'web_interface_port': web_interface_port
        }
        
        # Generate agent file using template
        with open(agent_dir / f'{agent_file_name}.py', 'w') as f:
            f.write(render_template_content('agent/agent.py', context))
        
        # Generate main.py file
        with open(agent_dir / 'main.py', 'w') as f:
            f.write(render_template_content('agent/main.py', context))
        
        # Generate models.py file
        with open(agent_dir / 'models.py', 'w') as f:
            f.write(render_template_content('agent/models.py', context))
        
        # Generate Dockerfile
        with open(agent_dir / 'Dockerfile', 'w') as f:
            f.write(render_template_content('agent/Dockerfile', context))
        
        # Generate requirements.txt
        with open(agent_dir / 'requirements.txt', 'w') as f:
            f.write(render_template_content('agent/requirements.txt', context))
        
        # Note: common utilities are now available from abi_core.common
        # No need to generate local common directory
        
        # Generate web interface if requested
        if with_web_interface:
            with open(agent_dir / 'web_interface.py', 'w') as f:
                f.write(render_template_content('common/web_interface', context))
        
        # Update runtime configuration
        update_runtime_config('agents', {
            name.lower().replace(' ', '_').replace('-', '_'): {
                'name': name,
                'description': description,
                'model': model,
                'port': agent_port,
                'web_interface_port': web_interface_port,
                'path': str(agent_dir)
            }
        })
        
        # Update docker-compose.yml
        _update_compose_with_agent(context)
        
        progress.update(task, description="Agent created successfully!", completed=True)
    
    console.print(f"\n✅ Agent '{name}' added successfully!", style="green")
    console.print(f"📁 Location: {agent_dir}", style="blue")
    console.print(f"🚀 Port: {agent_port}", style="cyan")
    
    if with_web_interface:
        console.print(f"🌐 Web interface enabled on port {web_interface_port}", style="cyan")
        console.print(f"   Endpoints:", style="cyan")
        console.print(f"   - POST /stream - SSE streaming", style="cyan")
        console.print(f"   - POST /query - Single query", style="cyan")
        console.print(f"   - GET /health - Health check", style="cyan")
    
    console.print(f"📦 Docker service added to compose file", style="green")
    console.print(f"   Run: docker-compose up {context['agent_name']}-agent", style="blue")


@add.command("service")
@click.argument('service_type', type=click.Choice(['semantic-layer', 'guardian', 'guardian-native', 'mcp-api']))
@click.option('--name', '-n', help='Service name (optional, not used for semantic-layer)')
@click.option('--domain', help='Domain specialization')
def add_service(service_type, name, domain):
    """Add a service to the project
    
    SERVICE_TYPE options:
    
    \b
    semantic-layer    Add AI agent discovery and routing service (uses fixed name 'semantic_layer')
    guardian          Add security policy enforcement service (placeholder)
    guardian-native   Add native guardian service based on abi-core guardial
    mcp-api          Add FastMCP/API central connection point service
    
    Note: You can also use 'abi-core add semantic-layer' as a shortcut.
    """
    
    # Check if we're in an ABI project
    if not Path('.abi').exists():
        console.print("❌ Not in an ABI project directory. Run 'abi-core create project' first.", style="red")
        return
    
    # Handle semantic-layer special case - always use 'semantic_layer' as name
    if service_type == 'semantic-layer':
        name = 'semantic_layer'
        service_dir = Path('services') / 'semantic_layer'
    else:
        if not name:
            name = Prompt.ask(f"Service name", default=f"{service_type.replace('-', '_')}_service")
        service_dir = Path('services') / name.lower().replace(' ', '_').replace('-', '_')
    
    if not domain:
        domain = Prompt.ask("Domain specialization", default="general")
    
    # Special check for semantic-layer - also check for existing semantic layer services
    if service_type == 'semantic-layer':
        if service_dir.exists():
            console.print("❌ Semantic layer service already exists!", style="red")
            console.print(f"📁 Location: {service_dir}", style="blue")
            console.print("💡 Use 'abi-core remove service semantic_layer' to remove it first if you want to recreate it.", style="yellow")
            return
        
        # Check if there's any other semantic layer service with different name
        services_dir = Path('services')
        if services_dir.exists():
            for service_path in services_dir.iterdir():
                if service_path.is_dir() and service_path != service_dir:
                    # Check if it has semantic layer structure (layer/mcp_server directory)
                    if (service_path / 'layer' / 'mcp_server').exists():
                        console.print(f"❌ Semantic layer service already exists with name '{service_path.name}'!", style="red")
                        console.print(f"📁 Location: {service_path}", style="blue")
                        return
    else:
        # Regular check for other service types
        if service_dir.exists():
            console.print(f"❌ Service '{name}' already exists", style="red")
            return
    
    from rich.progress import Progress, SpinnerColumn, TextColumn
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        task = progress.add_task(f"Creating {service_type} service...", total=None)
        
        # Create service directory
        service_dir.mkdir(parents=True)
        (service_dir / '__init__.py').touch()
        
        if service_type == 'semantic-layer':
            _create_semantic_layer_service(service_dir, domain)
            
        elif service_type == 'guardian':
            # Create guardian placeholder structure
            (service_dir / 'guard_core').mkdir()
            (service_dir / 'guard_core' / '__init__.py').touch()
            
        elif service_type == 'guardian-native':
            _create_guardian_native_service(service_dir, name, domain)
            
        elif service_type == 'mcp-api':
            _create_mcp_api_service(service_dir, name, domain)
        
        # Determine default port based on service type
        default_port = {
            'semantic-layer': 10100,
            'guardian': 11438,
            'guardian-native': 11439,
            'mcp-api': 9000
        }.get(service_type, 8080)
        
        # Update runtime configuration
        update_runtime_config('services', {
            name.lower().replace(' ', '_').replace('-', '_'): {
                'name': name,
                'type': service_type,
                'domain': domain,
                'port': default_port,
                'path': str(service_dir)
            }
        })
        
        # Update docker-compose.yml if it exists
        compose_file = Path('compose.yaml')
        if not compose_file.exists():
            compose_file = Path('docker-compose.yml')
        
        if compose_file.exists():
            progress.update(task, description="Updating Docker Compose...")
            context = {
                'service_name': name,
                'service_type': service_type,
                'domain': domain,
                'project_name': Path.cwd().name
            }
            _update_compose_with_service(compose_file, name, service_type, default_port, context)
        
        progress.update(task, description="Service created successfully!", completed=True)
    
    console.print(f"\n✅ Service '{name}' added successfully!", style="green")
    console.print(f"📁 Location: {service_dir}", style="blue")
    console.print(f"🌐 Default port: {default_port}", style="blue")
    console.print(f"🏷️  Domain: {domain}", style="blue")
    console.print("\n📋 Next steps:", style="yellow")
    console.print("  1. Run 'abi-core run' to start all services", style="dim")
    console.print(f"  2. The service will be available at http://localhost:{default_port}", style="dim")


@add.command("semantic-layer")
@click.option('--domain', help='Domain specialization', default='general')
def add_semantic_layer(domain):
    """Add semantic layer service to the project
    
    The semantic layer provides:
    - AI agent discovery and routing via MCP server
    - Semantic search with embeddings
    - Access validation with OPA policies
    - Agent card management
    
    This is equivalent to 'abi-core add service semantic-layer'.
    """
    
    # Check if we're in an ABI project
    if not Path('.abi').exists():
        console.print("❌ Not in an ABI project directory. Run 'abi-core create project' first.", style="red")
        return
    
    # Check if semantic layer already exists
    services_dir = Path('services')
    semantic_layer_dir = services_dir / 'semantic_layer'
    
    if semantic_layer_dir.exists():
        console.print("❌ Semantic layer service already exists!", style="red")
        console.print(f"📁 Location: {semantic_layer_dir}", style="blue")
        console.print("💡 Use 'abi-core remove service semantic_layer' to remove it first if you want to recreate it.", style="yellow")
        return
    
    # Check if there's any other semantic layer service with different name
    if services_dir.exists():
        for service_path in services_dir.iterdir():
            if service_path.is_dir():
                # Check if it has semantic layer structure (layer/mcp_server directory)
                if (service_path / 'layer' / 'mcp_server').exists():
                    console.print(f"❌ Semantic layer service already exists with name '{service_path.name}'!", style="red")
                    console.print(f"📁 Location: {service_path}", style="blue")
                    return
    
    from rich.progress import Progress, SpinnerColumn, TextColumn
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        task = progress.add_task("Creating semantic layer service...", total=None)
        
        # Create services directory if it doesn't exist
        services_dir.mkdir(exist_ok=True)
        
        # Create semantic layer directory
        semantic_layer_dir.mkdir()
        
        # Get project name from current directory
        project_name = Path.cwd().name
        
        # Create context for templates
        context = {
            'project_name': project_name,
            'domain': domain,
            'service_name': 'semantic_layer'
        }
        
        # Generate complete semantic layer structure
        progress.update(task, description="Generating semantic layer files...")
        from .create import _create_semantic_layer_structure
        _create_semantic_layer_structure(semantic_layer_dir, context)
        
        # Update runtime configuration
        progress.update(task, description="Updating configuration...")
        update_runtime_config('services', {
            'semantic_layer': {
                'name': 'Semantic Layer',
                'type': 'semantic-layer',
                'domain': domain,
                'port': 10100,
                'path': str(semantic_layer_dir),
                'enabled': True
            }
        })
        
        # Update docker-compose.yml if it exists
        compose_file = Path('compose.yaml')
        if compose_file.exists():
            progress.update(task, description="Updating Docker Compose...")
            _update_compose_with_semantic_layer(compose_file, context)
        
        progress.update(task, description="Semantic layer created successfully!", completed=True)
    
    console.print(f"\n✅ Semantic layer service added successfully!", style="green")
    console.print(f"📁 Location: {semantic_layer_dir}", style="blue")
    console.print(f"🌐 Port: 10100", style="blue")
    console.print(f"🏷️  Domain: {domain}", style="blue")
    console.print("\n📋 Next steps:", style="yellow")
    console.print("  1. Run 'abi-core run' to start all services", style="dim")
    console.print("  2. The semantic layer will be available at http://localhost:10100", style="dim")
    console.print("  3. Add agent cards to enable semantic search", style="dim")


@add.command("agent-card")
@click.option('--name', '-n', required=True, help='Agent name')
@click.option('--description', '-d', help='Agent description')
@click.option('--model', default='llama3.2:3b', help='LLM model for the agent')
@click.option('--url', help='Agent URL (e.g., http://localhost:8000)')
@click.option('--tasks', help='Comma-separated list of supported tasks')
def add_agent_card(name, description, model, url, tasks):
    """Create an agent card for semantic layer registration"""
    
    # Check if we're in an ABI project
    if not Path('.abi').exists():
        console.print("❌ Not in an ABI project directory. Run 'abi-core create project' first.", style="red")
        return
    
    # Check if semantic layer service exists
    semantic_service_dir = None
    services_dir = Path('services')
    
    if services_dir.exists():
        for service_path in services_dir.iterdir():
            if service_path.is_dir():
                # Check for semantic layer structure (layer/mcp_server directory)
                mcp_server_dir = service_path / 'layer' / 'mcp_server'
                if mcp_server_dir.exists():
                    semantic_service_dir = service_path
                    break
    
    if not semantic_service_dir:
        console.print("❌ No semantic layer service found. Run 'abi-core add service semantic-layer' first.", style="red")
        return
    
    # Interactive prompts if not provided
    if not description:
        description = Prompt.ask("Agent description", default=f"Specialized agent for {name}")
    
    if not url:
        url = Prompt.ask("Agent URL", default=f"http://localhost:8000")
    
    if not tasks:
        tasks = Prompt.ask("Supported tasks (comma-separated)", default="process_request,analyze_data")
    
    # Parse tasks
    task_list = [task.strip() for task in tasks.split(',') if task.strip()]
    
    # Generate agent card filename
    agent_card_filename = f"{name.lower().replace(' ', '_').replace('-', '_')}_agent.json"
    
    # Define target directories for agent cards
    semantic_agent_cards_dir = semantic_service_dir / 'layer' / 'mcp_server' / 'agent_cards'
    semantic_agent_cards_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if agent card already exists in semantic layer
    semantic_agent_card_path = semantic_agent_cards_dir / agent_card_filename
    if semantic_agent_card_path.exists():
        console.print(f"❌ Agent card '{agent_card_filename}' already exists in semantic layer", style="red")
        return
    
    from rich.progress import Progress, SpinnerColumn, TextColumn
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        task = progress.add_task("Creating agent card...", total=None)
        
        # Generate agent card content
        agent_card = _generate_agent_card(name, description, model, url, task_list)
        
        # Write agent card to semantic layer
        progress.update(task, description="Writing agent card to semantic layer...")
        with open(semantic_agent_card_path, 'w') as f:
            import json
            json.dump(agent_card, f, indent=2)
        
        # Also create agent card in agent's directory if agent exists
        agent_name_normalized = name.lower().replace(' ', '_').replace('-', '_')
        agent_dir = Path('agents') / agent_name_normalized
        agent_card_locations = [str(semantic_agent_card_path)]
        
        if agent_dir.exists():
            progress.update(task, description="Writing agent card to agent directory...")
            agent_agent_cards_dir = agent_dir / 'agent_cards'
            agent_agent_cards_dir.mkdir(exist_ok=True)
            agent_agent_card_path = agent_agent_cards_dir / agent_card_filename
            
            with open(agent_agent_card_path, 'w') as f:
                json.dump(agent_card, f, indent=2)
            
            agent_card_locations.append(str(agent_agent_card_path))
        
        # Update runtime configuration
        update_runtime_config('agent_cards', {
            agent_name_normalized: {
                'name': name,
                'description': description,
                'model': model,
                'url': url,
                'tasks': task_list,
                'locations': agent_card_locations
            }
        })
        
        # Note: Docker Compose environment variables are set during project creation
        
        progress.update(task, description="Agent card created successfully!", completed=True)
    
    console.print(f"\n✅ Agent card '{name}' created successfully!", style="green")
    console.print(f"📁 Semantic layer: {semantic_agent_card_path}", style="blue")
    if len(agent_card_locations) > 1:
        console.print(f"📁 Agent directory: {agent_card_locations[1]}", style="blue")
    else:
        console.print("💡 Create an agent with the same name to also store the card in the agent directory", style="yellow")
    console.print(f"🔗 URL: {url}", style="cyan")
    console.print(f"📋 Tasks: {', '.join(task_list)}", style="yellow")


@add.command("policies")
@click.option('--name', '-n', required=True, help='Policy set name')
@click.option('--domain', help='Domain for policies')
def add_policies(name, domain):
    """Add custom security policies"""
    
    # Check if we're in an ABI project
    if not Path('.abi').exists():
        console.print("❌ Not in an ABI project directory. Run 'abi-core create project' first.", style="red")
        return
    
    if not domain:
        domain = Prompt.ask("Policy domain", default="custom")
    
    policies_dir = Path('policies')
    policies_dir.mkdir(exist_ok=True)
    
    policy_file = policies_dir / f"{name.lower().replace(' ', '_').replace('-', '_')}.rego"
    
    if policy_file.exists():
        console.print(f"❌ Policy '{name}' already exists", style="red")
        return
    
    from rich.progress import Progress, SpinnerColumn, TextColumn
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        task = progress.add_task("Creating custom policies...", total=None)
        
        # Generate basic policy file
        policy_content = f'''# {name} Custom Policies
# Domain: {domain}

package {name.lower().replace(' ', '_').replace('-', '_')}.custom

# Import ABI core policies
import data.abi.core

# Custom rules for {domain} domain
domain := "{domain}"

# Allow basic operations
allow if {{
    input.action in ["read", "query"]
    input.domain == domain
}}

# Deny dangerous operations
deny contains "Dangerous operation blocked" if {{
    input.action in ["delete", "destroy"]
}}
'''
        
        with open(policy_file, 'w') as f:
            f.write(policy_content)
        
        # Update runtime configuration
        update_runtime_config('policies', {
            name.lower().replace(' ', '_').replace('-', '_'): {
                'name': name,
                'domain': domain,
                'file': str(policy_file)
            }
        })
        
        progress.update(task, description="Policies created successfully!", completed=True)
    
    console.print(f"\n✅ Policies '{name}' added successfully!", style="green")
    console.print(f"📁 Location: {policy_file}", style="blue")


def _generate_agent_card(name, description, model, url, tasks):
    """Generate agent card JSON structure based on planner template"""
    import uuid
    from datetime import datetime
    
    # Generate unique agent ID
    agent_id = f"agent://{name.lower().replace(' ', '_').replace('-', '_')}"
    
    # Create skills from tasks
    skills = []
    for i, task in enumerate(tasks):
        skill_id = task.lower().replace(' ', '_').replace('-', '_')
        skill_name = task.replace('_', ' ').title()
        
        skills.append({
            "id": skill_id,
            "name": skill_name,
            "description": f"{skill_name} functionality for {name}",
            "tags": [task.lower(), "processing", "analysis"],
            "examples": [f"Execute {task.lower()} operation"],
            "inputModes": ["text/plain"],
            "outputModes": ["text/plain"]
        })
    
    # Generate agent card structure
    agent_card = {
        "@context": [
            "https://raw.githubusercontent.com/GoogleCloudPlatform/a2a-llm/main/a2a/ontology/a2a_context.jsonld"
        ],
        "@type": "Agent",
        "id": agent_id,
        "name": name,
        "description": description,
        "url": url,
        "version": "1.0.0",
        "capabilities": {
            "streaming": "True",
            "pushNotifications": "True",
            "stateTransitionHistory": "False"
        },
        "defaultInputModes": ["text/plain"],
        "defaultOutputModes": ["text/plain"],
        "supportedTasks": tasks,
        "llmConfig": {
            "provider": "ollama",
            "model": model,
            "temperature": 0.1
        },
        "tools": [],
        "functions": [],
        "embedding": False,
        "prompt": f"You are {name}, a specialized agent responsible for {description.lower()}. Process user requests efficiently and provide clear, structured responses.",
        "skills": skills,
        "metadata": {
            "created": datetime.utcnow().isoformat(),
            "generator": "abi-core-cli",
            "version": "1.0.0"
        }
    }
    
    return agent_card


def _get_next_available_port(start_port=8000):
    """Get next available port starting from start_port"""
    import yaml
    
    used_ports = set()
    
    # Check docker-compose.yml for used ports
    compose_file = Path('compose.yaml')
    if not compose_file.exists():
        compose_file = Path('docker-compose.yml')
    
    if compose_file.exists():
        try:
            with open(compose_file, 'r') as f:
                compose_data = yaml.safe_load(f)
                
            services = compose_data.get('services', {})
            for service_name, service_config in services.items():
                ports = service_config.get('ports', [])
                for port_mapping in ports:
                    if isinstance(port_mapping, str):
                        external_port = int(port_mapping.split(':')[0])
                        used_ports.add(external_port)
        except Exception as e:
            console.print(f"Warning: Could not parse compose file: {e}", style="yellow")
    
    # Find next available port
    current_port = start_port
    while current_port in used_ports:
        current_port += 1
    
    return current_port


def _update_compose_with_agent(context):
    """Update docker-compose.yml with new agent service
    
    Reads model_serving configuration from runtime.yaml and configures
    the agent accordingly:
    - centralized: Agent uses shared Ollama service
    - distributed: Agent has its own Ollama instance (default)
    """
    import yaml
    
    compose_file = Path('compose.yaml')
    if not compose_file.exists():
        compose_file = Path('docker-compose.yml')
    
    if not compose_file.exists():
        console.print("Warning: No compose file found to update", style="yellow")
        return
    
    try:
        # Read runtime.yaml to get model_serving configuration
        runtime_file = Path('.abi/runtime.yaml')
        model_serving = 'distributed'  # default
        
        if runtime_file.exists():
            try:
                with open(runtime_file, 'r') as f:
                    runtime_data = yaml.safe_load(f)
                    model_serving = runtime_data.get('project', {}).get('model_serving', 'distributed')
            except Exception as e:
                console.print(f"Warning: Could not read runtime.yaml, using default 'distributed': {e}", style="yellow")
        
        with open(compose_file, 'r') as f:
            compose_data = yaml.safe_load(f)
        
        # Add agent service
        agent_service_name = f"{context['agent_name']}-agent"
        
        # Detect existing services and networks
        services = compose_data.get('services', {})
        existing_networks = []
        depends_on_services = []
        
        # Get project name from current directory
        project_name = Path.cwd().name
        
        # Find networks from existing services
        for service_config in services.values():
            service_networks = service_config.get('networks', [])
            if service_networks:
                existing_networks.extend(service_networks)
        
        # Use first network found or default
        network_name = existing_networks[0] if existing_networks else 'default'
        
        # Base agent service configuration
        agent_service = {
            'build': f"./agents/{context['agent_name']}",
            'container_name': f"{agent_service_name}",
            'environment': [
                f"ABI_ROLE={context['agent_display_name']} Agent",
                "ABI_NODE=ABI Node",
                f"MODEL_NAME={context['model_name']}",
                "LOG_LEVEL=INFO",
                "SERVICE_MODULE=agent.main",
                f"SERVICE_PORT={context['agent_port']}"
            ],
            'volumes': ["./logs:/app/logs"],
            'networks': [network_name]
        }
        
        # Configure based on model_serving mode
        if model_serving == 'centralized':
            # Centralized mode: Use shared Ollama service
            console.print(f"📡 Configuring agent in centralized mode (shared Ollama)", style="cyan")
            
            # Check if centralized ollama service exists
            ollama_service_name = f'{project_name}-ollama'
            if ollama_service_name in services:
                depends_on_services.append(ollama_service_name)
            
            agent_service['ports'] = [f"{context['agent_port']}:{context['agent_port']}"]
            agent_service['environment'].extend([
                f"OLLAMA_HOST=http://{project_name}-ollama:11434",
                "START_OLLAMA=false",
                "LOAD_MODELS=false"
            ])
            # No Ollama port, no Ollama volume
            
        else:
            # Distributed mode: Each agent has its own Ollama
            console.print(f"🔧 Configuring agent in distributed mode (own Ollama)", style="cyan")
            
            ollama_port = _get_next_available_port(11434)
            agent_service['ports'] = [
                f"{context['agent_port']}:{context['agent_port']}",
                f"{ollama_port}:11434"
            ]
            agent_service['environment'].extend([
                f"OLLAMA_HOST=http://localhost:{ollama_port}",
                "START_OLLAMA=true",
                "LOAD_MODELS=true"
            ])
            agent_service['volumes'].append("ollama_data:/root/.ollama")
        
        # Add depends_on if services exist
        if depends_on_services:
            agent_service['depends_on'] = depends_on_services
        
        # Add web interface port if enabled
        if context.get('with_web_interface') and context.get('web_interface_port'):
            agent_service['ports'].append(f"{context['web_interface_port']}:{context['web_interface_port']}")
            agent_service['environment'].append(f"WEB_INTERFACE_PORT={context['web_interface_port']}")
        
        # Add to services
        if 'services' not in compose_data:
            compose_data['services'] = {}
        
        compose_data['services'][agent_service_name] = agent_service
        
        # Ensure volumes section exists (for distributed mode)
        if 'volumes' not in compose_data:
            compose_data['volumes'] = {}
        
        # Add ollama_data volume if needed (distributed mode or if not exists)
        if model_serving == 'distributed' and 'ollama_data' not in compose_data['volumes']:
            compose_data['volumes']['ollama_data'] = {'driver': 'local'}
        
        # Write back to file
        with open(compose_file, 'w') as f:
            yaml.dump(compose_data, f, default_flow_style=False, sort_keys=False)
        
        console.print(f"✅ Updated {compose_file.name} with agent service ({model_serving} mode)", style="green")
        
    except Exception as e:
        console.print(f"Warning: Could not update compose file: {e}", style="yellow")


def _create_semantic_layer_service(service_dir, domain):
    """Create semantic layer service structure"""
    # Import the helper function from create.py
    from .create import _create_semantic_layer_structure
    
    context = {'domain': domain or 'general', 'project_name': service_dir.parent.parent.name}
    _create_semantic_layer_structure(service_dir, context)


def _update_compose_with_service(compose_file, service_name, service_type, service_port, context):
    """Update docker-compose.yml to include new service with port conflict detection"""
    import yaml
    
    try:
        # Read current compose file
        with open(compose_file, 'r') as f:
            compose_data = yaml.safe_load(f) or {}
        
        services = compose_data.get('services', {})
        
        # Check if service already exists (try different naming patterns)
        service_key = service_name.replace('_', '-')
        project_name = context.get('project_name', Path.cwd().name)
        project_service_key = f"{project_name}-{service_key}"
        
        if service_key in services or project_service_key in services:
            return  # Already exists
        
        # Use project-prefixed service name for consistency with template
        final_service_key = project_service_key
        
        # Find available port to avoid conflicts
        used_ports = set()
        for svc_name, svc_config in services.items():
            ports = svc_config.get('ports', [])
            for port_mapping in ports:
                if isinstance(port_mapping, str) and ':' in port_mapping:
                    external_port = int(port_mapping.split(':')[0])
                    used_ports.add(external_port)
        
        # Find next available port starting from the requested port
        available_port = service_port
        while available_port in used_ports:
            available_port += 1
        
        # Generate service definition based on type
        if service_type == 'semantic-layer':
            service_definition = {
                'build': f'./services/{service_name}',
                'container_name': f'{project_name}-{service_key}',
                'ports': [f'{available_port}:{available_port}'],
                'environment': [
                    'ABI_ROLE=Semantic Layer',
                    'ABI_NODE=ABI Node',
                    'AGENT_CARDS_BASE=/app/layer/mcp_server/agent_cards',
                    f'ABI_LLM_BASE=http://{project_name}-guardian:11438',
                    'EMBEDDING_MODEL=nomic-embed-text:v1.5',
                    f'GUARDIAN_URL=http://{project_name}-guardian:11438',
                    f'OPA_URL=http://{project_name}-opa:8181',
                    'SEMANTIC_LAYER_HOST=0.0.0.0',
                    f'SEMANTIC_LAYER_PORT={available_port}'
                ],
                'volumes': [f'./services/{service_name}/layer/mcp_server/agent_cards:/app/layer/mcp_server/agent_cards:ro', './logs:/app/logs'],
                'networks': [f'{project_name}-network'],
                'depends_on': []
            }
        elif service_type == 'guardian':
            service_definition = {
                'build': f'./services/{service_name}',
                'container_name': f'{project_name}-{service_key}',
                'ports': [f'{available_port}:{available_port}'],
                'environment': [
                    'ABI_ROLE=Guardian Service',
                    'ABI_NODE=ABI Node',
                    f'OPA_URL=http://{project_name}-opa:8181',
                    'GUARDIAN_PORT=' + str(available_port),
                    # Entrypoint variables for Ollama (embeddings)
                    'START_OLLAMA=true',
                    'LOAD_MODELS=true',
                    'SERVICE_MODULE=main',
                    f'SERVICE_PORT={available_port}'
                ],
                'volumes': ['./logs:/app/logs'],
                'networks': [f'{project_name}-network'],
                'depends_on': []
            }
        elif service_type == 'guardian-native':
            service_definition = {
                'build': f'./services/{service_name}',
                'container_name': f'{project_name}-{service_key}',
                'ports': [f'{available_port}:{available_port}'],
                'environment': [
                    f'OPA_URL=http://{project_name}-opa:8181',
                    'GUARDIAN_PORT=' + str(available_port),
                    'AGENT_CARDS_BASE=/app/agent_cards'
                ],
                'volumes': ['./agent_cards:/app/agent_cards:ro', './logs:/app/logs'],
                'networks': [f'{project_name}-network'],
                'depends_on': []
            }
        elif service_type == 'mcp-api':
            service_definition = {
                'build': f'./services/{service_name}',
                'container_name': f'{project_name}-{service_key}',
                'ports': [f'{available_port}:{available_port}'],
                'environment': [
                    'MCP_API_HOST=0.0.0.0',
                    f'MCP_API_PORT={available_port}',
                    f'SEMANTIC_LAYER_URL=http://{project_name}-semantic-layer:10100'
                ],
                'volumes': ['./logs:/app/logs'],
                'networks': [f'{project_name}-network'],
                'depends_on': []
            }
        else:
            # Generic service
            service_definition = {
                'build': f'./services/{service_name}',
                'container_name': f'{project_name}-{service_key}',
                'ports': [f'{available_port}:{available_port}'],
                'volumes': ['./logs:/app/logs'],
                'networks': [f'{project_name}-network']
            }
        
        # Add service to compose data
        services[final_service_key] = service_definition
        compose_data['services'] = services
        
        # Ensure networks section exists
        if 'networks' not in compose_data:
            compose_data['networks'] = {f'{project_name}-network': {'driver': 'bridge'}}
        
        # Write updated compose file
        with open(compose_file, 'w') as f:
            yaml.dump(compose_data, f, default_flow_style=False, sort_keys=False)
        
        # Show port information
        if available_port != service_port:
            console.print(f"⚠️  Port {service_port} was in use, assigned port {available_port} instead", style="yellow")
        
        console.print(f"✅ Updated {compose_file.name} with {service_name} service on port {available_port}", style="green")
        
    except Exception as e:
        console.print(f"⚠️  Warning: Could not update {compose_file.name}: {e}", style="yellow")


def _update_compose_with_semantic_layer(compose_file, context):
    """Update docker-compose.yml to include semantic layer service (legacy function)"""
    _update_compose_with_service(compose_file, 'semantic_layer', 'semantic-layer', 10100, context)


def _create_guardian_native_service(service_dir, name, domain):
    """Create native guardian service based on abi-core guardial"""
    console.print("🛡️ Creating native Guardian service...", style="blue")
    
    # Copy structure from abi-core guardial
    import shutil
    import os
    
    # Source path (abi-core guardial)
    source_guardial = Path("../abi-core/agents/guardial")
    
    if not source_guardial.exists():
        console.print("❌ abi-core guardial not found. Creating basic guardian structure.", style="yellow")
        _create_basic_guardian_structure(service_dir, name, domain)
        return
    
    try:
        # Copy agent directory
        agent_dir = service_dir / 'agent'
        agent_dir.mkdir()
        
        # Copy main files
        for file_name in ['main.py', 'guardial_secure.py', 'mcp_interface.py']:
            src_file = source_guardial / 'agent' / file_name
            if src_file.exists():
                shutil.copy2(src_file, agent_dir / file_name)
        
        # Copy opa directory
        opa_dir = service_dir / 'opa'
        if (source_guardial / 'opa').exists():
            shutil.copytree(source_guardial / 'opa', opa_dir)
        
        # Copy common directory if exists
        common_dir = service_dir / 'common'
        if (source_guardial / 'common').exists():
            shutil.copytree(source_guardial / 'common', common_dir)
        
        # Create Dockerfile
        with open(service_dir / 'Dockerfile', 'w') as f:
            f.write(_get_guardian_dockerfile(domain))
        
        # Create requirements.txt
        with open(service_dir / 'requirements.txt', 'w') as f:
            f.write(_get_guardian_requirements())
        
        console.print("✅ Native Guardian service created successfully", style="green")
        
    except Exception as e:
        console.print(f"❌ Error copying guardian files: {e}", style="red")
        _create_basic_guardian_structure(service_dir, name, domain)


def _create_basic_guardian_structure(service_dir, name, domain):
    """Create basic guardian structure when abi-core is not available"""
    console.print("Creating basic guardian structure...", style="blue")
    
    # Create basic structure
    (service_dir / 'agent').mkdir()
    (service_dir / 'opa' / 'policies').mkdir(parents=True)
    
    # Create basic main.py
    with open(service_dir / 'agent' / 'main.py', 'w') as f:
        f.write(_get_basic_guardian_main(name, domain))
    
    # Create basic Dockerfile
    with open(service_dir / 'Dockerfile', 'w') as f:
        f.write(_get_guardian_dockerfile(domain))
    
    # Create requirements.txt
    with open(service_dir / 'requirements.txt', 'w') as f:
        f.write(_get_guardian_requirements())


def _get_guardian_dockerfile(domain):
    """Get Dockerfile for guardian service"""
    return f'''FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose ports
EXPOSE 8003
EXPOSE 8080

# Set environment variables
ENV ABI_ROLE="Guardian Security"
ENV ABI_NODE="ABI Node"
ENV DOMAIN="{domain or 'general'}"

# Run the application
CMD ["python", "agent/main.py"]
'''


def _get_guardian_requirements():
    """Get requirements.txt for guardian service"""
    return '''fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
requests==2.31.0
pyyaml==6.0.1
'''


def _get_basic_guardian_main(name, domain):
    """Get basic main.py for guardian when abi-core is not available"""
    return f'''#!/usr/bin/env python3
"""
{name or 'Guardian'} Security Service
Domain: {domain or 'general'}
"""

import os
import logging
from typing import Dict, Any
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
PORT = int(os.getenv("GUARDIAN_PORT", "8003"))
HOST = os.getenv("GUARDIAN_HOST", "0.0.0.0")
DOMAIN = os.getenv("DOMAIN", "{domain or 'general'}")

app = FastAPI(
    title="Guardian Security Service",
    description="Security service for {domain or 'general'} domain",
    version="1.0.0"
)

# Models
class SecurityRequest(BaseModel):
    action: str
    resource: str
    context: Dict[str, Any] = {{}}

class SecurityResponse(BaseModel):
    allowed: bool
    reason: str
    risk_level: str = "low"

@app.get("/")
async def root():
    """Health check endpoint"""
    return {{
        "service": "guardian_security",
        "status": "healthy",
        "domain": DOMAIN
    }}

@app.post("/validate", response_model=SecurityResponse)
async def validate_security(request: SecurityRequest):
    """Validate security request"""
    try:
        # Basic security validation
        if request.action in ["delete", "destroy"]:
            return SecurityResponse(
                allowed=False,
                reason="Dangerous operation blocked",
                risk_level="high"
            )
        
        return SecurityResponse(
            allowed=True,
            reason="Operation allowed",
            risk_level="low"
        )
    except Exception as e:
        logger.error(f"Security validation error: {{e}}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Guardian health check"""
    return {{
        "status": "healthy",
        "service": "guardian",
        "domain": DOMAIN,
        "security_level": "active"
    }}

if __name__ == "__main__":
    logger.info(f"Starting Guardian Security Service on {{HOST}}:{{PORT}}")
    uvicorn.run(app, host=HOST, port=PORT)
'''


def _get_agent_template(context):
    """Get agent template"""
    return f'''"""
{context.get('agent_name', 'ABI Agent')} Agent
Generated by ABI-Core scaffolding
"""

import logging
import os
from typing import Dict, Any, AsyncIterable
from abc import ABC, abstractmethod

from langchain_ollama import ChatOllama

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Base class for ABI agents"""
    
    def __init__(self, agent_name: str, description: str, content_types: list):
        self.agent_name = agent_name
        self.description = description
        self.content_types = content_types
    
    @abstractmethod
    async def stream(self, query: str, context_id: str, task_id: str) -> AsyncIterable[Dict[str, Any]]:
        """Process query and stream responses"""
        pass

class {context.get('agent_class_name', 'ABIAgent')}(BaseAgent):
    """
    {context.get('agent_description', 'Specialized ABI agent')}
    """
    
    def __init__(self):
        super().__init__(
            agent_name='{context.get('agent_name', 'ABI Agent')}',
            description='{context.get('agent_description', 'Specialized ABI agent')}',
            content_types=['text', 'application/json']
        )
        
        self.llm = ChatOllama(
            model=os.getenv('MODEL_NAME', '{context.get('model_name', 'llama3.2:3b')}'),
            base_url=os.getenv('OLLAMA_HOST', 'http://localhost:11434')
        )
    
    async def stream(self, query: str, context_id: str, task_id: str) -> AsyncIterable[Dict[str, Any]]:
        """Process query and stream responses"""
        try:
            # Simple response for now
            response = f"Agent {context.get('agent_name', 'ABI Agent')} processed: {{query}}"
            
            yield {{
                'content': response,
                'response_type': 'text',
                'is_task_completed': True,
                'require_user_input': False
            }}
        except Exception as e:
            yield {{
                'content': f'Error: {{str(e)}}',
                'response_type': 'text',
                'is_task_completed': True,
                'require_user_input': False
            }}

# Agent instance
agent = {context.get('agent_class_name', 'ABIAgent')}()
'''


def _create_mcp_api_service(service_dir, name, domain):
    """Create MCP API service structure"""
    console.print("🔌 Creating MCP API service...", style="blue")
    
    # Create main.py
    context = {
        'project_name': Path.cwd().name,
        'service_name': name,
        'domain': domain
    }
    
    with open(service_dir / 'main.py', 'w') as f:
        f.write(render_template_content('service_mcp_api/main.py', context))
    
    # Create requirements.txt
    with open(service_dir / 'requirements.txt', 'w') as f:
        f.write(render_template_content('service_mcp_api/requirements.txt', context))
    
    # Create Dockerfile
    with open(service_dir / 'Dockerfile', 'w') as f:
        f.write(render_template_content('service_mcp_api/Dockerfile', context))
    
    console.print("✅ MCP API service created successfully", style="green")