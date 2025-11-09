"""
Create commands for ABI Core CLI
"""

import click
from pathlib import Path
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn

from .utils import console, render_template_content


def _create_semantic_layer_structure(semantic_dir, context):
    """Create complete semantic layer structure with all templates"""
    
    # Create directory structure
    layer_dir = semantic_dir / 'layer'
    layer_dir.mkdir(exist_ok=True)
    
    mcp_server_dir = layer_dir / 'mcp_server'
    mcp_server_dir.mkdir(exist_ok=True)
    
    # Create agent_cards directory
    agent_cards_dir = mcp_server_dir / 'agent_cards'
    agent_cards_dir.mkdir(exist_ok=True)
    
    embedding_mesh_dir = layer_dir / 'embedding_mesh'
    embedding_mesh_dir.mkdir(exist_ok=True)
    
    models_dir = embedding_mesh_dir / 'models'
    models_dir.mkdir(exist_ok=True)
    
    # Root level files
    files_to_create = [
        ('__init__.py', 'service_semantic_layer/__init__.py'),
        ('main.py', 'service_semantic_layer/main.py'),
        ('requirements.txt', 'service_semantic_layer/requirements.txt'),
        ('Dockerfile', 'service_semantic_layer/Dockerfile'),
        ('SEMANTIC_ACCESS_VALIDATION.md', 'service_semantic_layer/SEMANTIC_ACCESS_VALIDATION.md'),
    ]
    
    # Layer package files
    layer_files = [
        ('layer/__init__.py', 'service_semantic_layer/layer/__init__.py'),
    ]
    
    # MCP Server files
    mcp_server_files = [
        ('layer/mcp_server/__init__.py', 'service_semantic_layer/layer/mcp_server/__init__.py'),
        ('layer/mcp_server/main.py', 'service_semantic_layer/layer/mcp_server/main.py'),
        ('layer/mcp_server/server.py', 'service_semantic_layer/layer/mcp_server/server.py'),
        ('layer/mcp_server/semantic_access_validator.py', 'service_semantic_layer/layer/mcp_server/semantic_access_validator.py'),
    ]
    
    # Embedding Mesh files
    embedding_mesh_files = [
        ('layer/embedding_mesh/__init__.py', 'service_semantic_layer/layer/embedding_mesh/__init__.py'),
        ('layer/embedding_mesh/api.py', 'service_semantic_layer/layer/embedding_mesh/api.py'),
        ('layer/embedding_mesh/embeddings_abi.py', 'service_semantic_layer/layer/embedding_mesh/embeddings_abi.py'),
        ('layer/embedding_mesh/models/__init__.py', 'service_semantic_layer/layer/embedding_mesh/models/__init__.py'),
        ('layer/embedding_mesh/models/models.py', 'service_semantic_layer/layer/embedding_mesh/models/models.py'),
    ]
    
    # Create all files
    all_files = files_to_create + layer_files + mcp_server_files + embedding_mesh_files
    
    for file_path, template_path in all_files:
        full_path = semantic_dir / file_path
        with open(full_path, 'w') as f:
            f.write(render_template_content(template_path, context))


@click.group()
def create():
    """Create new ABI projects and components
    
    Available commands:
    
    \b
    project    Create a new ABI project with agents, services, and configuration
    
    \b
    Examples:
      abi-core create project my-app --with-semantic-layer
      abi-core create project fintech --domain finance --with-guardian
    
    Use 'abi-core create COMMAND --help' for more information on a command.
    """
    pass


@create.command("project")
@click.option('--name', '-n', required=True, help='Project name')
@click.option('--description', '-d', help='Project description')
@click.option('--domain', help='Domain/industry (e.g., finance, healthcare)')
@click.option('--with-semantic-layer', is_flag=True, help='Include AI agent discovery and routing service')
@click.option('--with-guardian', is_flag=True, help='Include security policy enforcement service')
@click.option('--model-serving', type=click.Choice(['centralized', 'distributed']), default=None, help='Model serving strategy: centralized (shared Ollama) or distributed (each agent has own Ollama)')
def create_project(name, description, domain, with_semantic_layer, with_guardian, model_serving):
    """Create a new ABI project with agents, services, and configuration
    
    Creates a complete ABI project structure including:
    - Project configuration and metadata
    - Docker Compose setup for containerization
    - Optional semantic layer for agent discovery
    - Optional guardian service for security policies
    
    \b
    Examples:
      abi-core create project my-app --name my-app
      abi-core create project fintech --name fintech --domain finance --with-semantic-layer
      abi-core create project secure-app --name secure-app --with-guardian --with-semantic-layer
    
    The project will be created in a new directory with the specified name.
    """
    
    # Interactive prompts if not provided
    if not description:
        description = Prompt.ask("Project description", default=f"ABI-powered {name} project")
    
    if not domain:
        domain = Prompt.ask("Domain/Industry", default="general")
    
    if not with_semantic_layer:
        with_semantic_layer = Confirm.ask("Include semantic layer service?", default=True)
    
    if not with_guardian:
        with_guardian = Confirm.ask("Include guardian security service?", default=True)
    
    # Ask about model serving strategy if not provided
    if not model_serving:
        console.print("\n💡 Model Serving Strategy:", style="cyan bold")
        console.print("  • centralized: Single shared Ollama for all agents (recommended for production)", style="dim")
        console.print("  • distributed: Each agent has its own Ollama (recommended for development)", style="dim")
        model_serving = Prompt.ask(
            "\nChoose model serving strategy",
            choices=["centralized", "distributed"],
            default="distributed"
        )
    
    project_dir = Path(name.lower().replace(' ', '_').replace('-', '_'))
    
    if project_dir.exists():
        console.print(f"❌ Directory '{project_dir}' already exists", style="red")
        return
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        task = progress.add_task("Creating project structure...", total=None)
        
        # Template context
        context = {
            'project_name': name,
            'project_dir': project_dir.name,
            'description': description,
            'domain': domain,
            'with_semantic_layer': with_semantic_layer,
            'with_guardian': with_guardian,
            'model_serving': model_serving,
            'is_centralized': model_serving == 'centralized',
            'is_distributed': model_serving == 'distributed',
            'service_name': name,  # Add service_name
            'service_class_name': name.replace(' ', '').replace('-', '').replace('_', ''),  # Add service_class_name
            'version': '1.0.0',
            'timestamp': '2024-01-01T00:00:00Z'
        }
        
        # Create project structure
        project_dir.mkdir()
        
        # Config
        (project_dir / 'config').mkdir()
        (project_dir / 'config' / '__init__.py').touch()
        with open(project_dir / 'config' / 'config.py', 'w') as f:
            f.write(render_template_content('project/config/config.py', context))
        
        # Agents directory
        (project_dir / 'agents').mkdir()
        (project_dir / 'agents' / '__init__.py').touch()
        
        # Services directory
        (project_dir / 'services').mkdir()
        (project_dir / 'services' / '__init__.py').touch()
        
        if with_semantic_layer:
            console.print("🔄 Creating semantic layer service...")
            semantic_dir = project_dir / 'services' / 'semantic_layer'
            semantic_dir.mkdir()
            
            # Generate complete semantic layer structure
            _create_semantic_layer_structure(semantic_dir, context)
        
        if with_guardian:
            guardian_dir = project_dir / 'services' / 'guardian'
            guardian_dir.mkdir()
            (guardian_dir / '__init__.py').touch()
            (guardian_dir / 'guard_core').mkdir()
            (guardian_dir / 'guard_core' / '__init__.py').touch()
            
            # Generate guardian files with security validation
            with open(guardian_dir / 'agent_guardian.py', 'w') as f:
                f.write(render_template_content('service_guardian/agent_guardian', context))
            with open(guardian_dir / 'mcp_interface.py', 'w') as f:
                f.write(render_template_content('service_guardian/mcp_interface', context))
            with open(guardian_dir / 'main.py', 'w') as f:
                f.write(_get_guardian_main_template(context))
            with open(guardian_dir / 'requirements.txt', 'w') as f:
                f.write(_get_guardian_requirements_template())
            with open(guardian_dir / 'Dockerfile', 'w') as f:
                f.write(_get_guardian_dockerfile_template())
            
            # Generate OPA policies
            opa_dir = guardian_dir / 'opa' / 'policies'
            opa_dir.mkdir(parents=True)
            with open(opa_dir / 'semantic_access.rego', 'w') as f:
                f.write(render_template_content('service_guardian/opa/policies/semantic_access.rego', context))
            
            # Generate custom policies
            with open(guardian_dir / 'guard_core' / 'custom_policies.py', 'w') as f:
                f.write(render_template_content('service_guardian/guard_core/custom_policies', context))
        
        # Policies directory
        (project_dir / 'policies').mkdir()
        
        # ABI directory
        (project_dir / '.abi').mkdir()
        with open(project_dir / '.abi' / 'runtime.yaml', 'w') as f:
            f.write(render_template_content('project/.abi/runtime.yaml', context))
        
        # Root files
        with open(project_dir / 'requirements.txt', 'w') as f:
            f.write(render_template_content('project/requirements.txt', context))
        
        with open(project_dir / 'compose.yaml', 'w') as f:
            f.write(render_template_content('project/compose.yaml', context))
        
        with open(project_dir / 'Dockerfile', 'w') as f:
            f.write(render_template_content('project/Dockerfile', context))
        
        with open(project_dir / 'README.md', 'w') as f:
            f.write(render_template_content('project/README.md', context))
        
        # Generate main application file
        with open(project_dir / 'main.py', 'w') as f:
            f.write(render_template_content('project/main.py', context))
        
        progress.update(task, description="Project created successfully!", completed=True)
    
    console.print(f"\n✅ Project '{name}' created successfully!", style="green")
    console.print(f"📁 Location: {project_dir.absolute()}", style="blue")
    
    # Show next steps
    console.print("\n📋 Next steps:", style="cyan")
    console.print(f"   cd {project_dir}")
    console.print("   abi-core add agent --name YourAgent")
    console.print("   abi-core run")


def _get_semantic_main_template(context):
    """Get semantic layer main template"""
    return f'''#!/usr/bin/env python3
"""
Semantic Layer Service Main
{context.get('project_name', 'ABI Project')} - {context.get('domain', 'general')} Domain
"""

import os
import json
import logging
import numpy as np
from pathlib import Path
from typing import Optional, List, Dict, Any

import uvicorn
from fastapi import FastAPI, HTTPException
from fastmcp import FastMCP

logger = logging.getLogger(__name__)

# Configuration
AGENT_CARDS_DIR = os.getenv("AGENT_CARDS_BASE", "./mcp_server/agent_cards")
MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text:v1.5")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")

app = FastAPI(
    title="Semantic Layer Service",
    description="Semantic layer for {context.get('project_name', 'ABI Project')} - {context.get('domain', 'general')} domain",
    version="1.0.0"
)

# Global agent cards cache
_agent_cards_cache: Optional[List[Dict[str, Any]]] = None

def load_agent_cards() -> List[Dict[str, Any]]:
    """Load all agent cards from the agent_cards directory"""
    global _agent_cards_cache
    
    if _agent_cards_cache is not None:
        return _agent_cards_cache
    
    cards_dir = Path(AGENT_CARDS_DIR)
    agent_cards = []
    
    if not cards_dir.exists():
        logger.warning(f"Agent cards directory not found: {{cards_dir}}")
        return []
    
    for card_file in cards_dir.glob("*.json"):
        try:
            with open(card_file, 'r') as f:
                card_data = json.load(f)
                agent_cards.append(card_data)
                logger.info(f"Loaded agent card: {{card_data.get('name', 'Unknown')}}")
        except Exception as e:
            logger.error(f"Error loading agent card {{card_file}}: {{e}}")
    
    _agent_cards_cache = agent_cards
    logger.info(f"Loaded {{len(agent_cards)}} agent cards")
    return agent_cards

def find_best_agent(query: str) -> Optional[Dict[str, Any]]:
    """Find the best matching agent for a query using simple text matching"""
    agent_cards = load_agent_cards()
    
    if not agent_cards:
        return None
    
    query_lower = query.lower()
    best_match = None
    best_score = 0
    
    for card in agent_cards:
        score = 0
        
        # Check name match
        if query_lower in card.get('name', '').lower():
            score += 3
        
        # Check description match
        if query_lower in card.get('description', '').lower():
            score += 2
        
        # Check supported tasks
        for task in card.get('supportedTasks', []):
            if query_lower in task.lower():
                score += 2
        
        # Check skills
        for skill in card.get('skills', []):
            if query_lower in skill.get('name', '').lower():
                score += 1
            if query_lower in skill.get('description', '').lower():
                score += 1
        
        if score > best_score:
            best_score = score
            best_match = card
    
    return best_match

@app.get("/")
async def root():
    agent_count = len(load_agent_cards())
    return {{
        "message": "Semantic Layer Service",
        "status": "running",
        "project": "{context.get('project_name', 'ABI Project')}",
        "domain": "{context.get('domain', 'general')}",
        "registered_agents": agent_count
    }}

@app.get("/health")
async def health():
    agent_cards = load_agent_cards()
    return {{
        "status": "healthy",
        "service": "semantic_layer",
        "agent_cards_loaded": len(agent_cards),
        "agent_cards_directory": AGENT_CARDS_DIR
    }}

@app.get("/v1/agents")
async def list_agents():
    """List all registered agents"""
    agent_cards = load_agent_cards()
    return {{
        "agents": [
            {{
                "id": card.get("id"),
                "name": card.get("name"),
                "description": card.get("description"),
                "url": card.get("url"),
                "tasks": card.get("supportedTasks", [])
            }}
            for card in agent_cards
        ],
        "total": len(agent_cards)
    }}

@app.get("/v1/tools")
async def get_tools():
    return {{
        "tools": [
            {{
                "name": "find_agent",
                "description": "Find agents by natural language query",
                "parameters": {{"query": "string"}}
            }},
            {{
                "name": "list_agents",
                "description": "List all registered agents",
                "parameters": {{}}
            }},
            {{
                "name": "get_agent",
                "description": "Get specific agent by ID",
                "parameters": {{"agent_id": "string"}}
            }}
        ]
    }}

@app.post("/v1/tools/find_agent")
async def find_agent_tool(request: dict):
    """Find agent tool for MCP protocol"""
    query = request.get("query", "")
    
    if not query:
        raise HTTPException(status_code=400, detail="Query parameter is required")
    
    best_agent = find_best_agent(query)
    
    if not best_agent:
        return {{
            "content": [
                {{
                    "type": "text",
                    "text": f"No suitable agent found for query: {{query}}"
                }}
            ]
        }}
    
    return {{
        "content": [
            {{
                "type": "text", 
                "text": f"Found agent: {{best_agent.get('name')}} - {{best_agent.get('description')}}"
            }}
        ],
        "agent_card": best_agent
    }}

@app.post("/v1/tools/get_agent")
async def get_agent_tool(request: dict):
    """Get specific agent by ID"""
    agent_id = request.get("agent_id", "")
    
    if not agent_id:
        raise HTTPException(status_code=400, detail="agent_id parameter is required")
    
    agent_cards = load_agent_cards()
    
    for card in agent_cards:
        if card.get("id") == agent_id:
            return {{
                "content": [
                    {{
                        "type": "text",
                        "text": f"Agent: {{card.get('name')}} - {{card.get('description')}}"
                    }}
                ],
                "agent_card": card
            }}
    
    raise HTTPException(status_code=404, detail=f"Agent not found: {{agent_id}}")

@app.post("/v1/register_agent")
async def register_agent(agent_card: dict):
    """Register a new agent (for dynamic registration)"""
    global _agent_cards_cache
    
    # Validate required fields
    required_fields = ["id", "name", "description", "url"]
    for field in required_fields:
        if field not in agent_card:
            raise HTTPException(status_code=400, detail=f"Missing required field: {{field}}")
    
    # Save to file
    agent_id = agent_card["id"].replace("agent://", "").replace("/", "_")
    card_file = Path(AGENT_CARDS_DIR) / f"{{agent_id}}_agent.json"
    
    try:
        with open(card_file, 'w') as f:
            json.dump(agent_card, f, indent=2)
        
        # Clear cache to force reload
        _agent_cards_cache = None
        
        logger.info(f"Registered new agent: {{agent_card.get('name')}}")
        
        return {{
            "message": "Agent registered successfully",
            "agent_id": agent_card["id"],
            "file": str(card_file)
        }}
    
    except Exception as e:
        logger.error(f"Error registering agent: {{e}}")
        raise HTTPException(status_code=500, detail=f"Failed to register agent: {{str(e)}}")

@app.delete("/v1/agents/{{agent_id}}")
async def unregister_agent(agent_id: str):
    """Unregister an agent (remove from registry)"""
    global _agent_cards_cache
    
    # Find and remove the agent card file
    cards_dir = Path(AGENT_CARDS_DIR)
    agent_file_id = agent_id.replace("agent://", "").replace("/", "_")
    
    for card_file in cards_dir.glob(f"*{{agent_file_id}}*.json"):
        try:
            card_file.unlink()
            _agent_cards_cache = None  # Clear cache
            logger.info(f"Unregistered agent: {{agent_id}}")
            
            return {{
                "message": "Agent unregistered successfully",
                "agent_id": agent_id,
                "file_removed": str(card_file)
            }}
        except Exception as e:
            logger.error(f"Error unregistering agent: {{e}}")
            raise HTTPException(status_code=500, detail=f"Failed to unregister agent: {{str(e)}}")
    
    raise HTTPException(status_code=404, detail=f"Agent not found: {{agent_id}}")

if __name__ == "__main__":
    # Load agent cards on startup
    load_agent_cards()
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=10100,
        reload=True
    )
'''


def _get_semantic_requirements_template():
    """Get semantic layer requirements template"""
    return '''# Semantic Layer Service Requirements
fastapi>=0.100.0
uvicorn>=0.20.0
pydantic>=2.0.0
requests>=2.31.0
httpx>=0.25.0
fastmcp>=0.1.0
weaviate-client>=4.0.0
sentence-transformers>=2.2.0
numpy>=1.24.0
pandas>=2.0.0
ollama>=0.1.0
starlette>=0.27.0
'''


def _get_semantic_dockerfile_template():
    """Get semantic layer Dockerfile template"""
    return '''# Semantic Layer Service Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy service files
COPY . .

# Create agent_cards directory if it doesn't exist
RUN mkdir -p /app/mcp_server/agent_cards

# Expose port
EXPOSE 10100

# Environment variables
ENV ABI_ROLE="Semantic Layer"
ENV ABI_NODE="ABI Node"
ENV PYTHONPATH=/app
ENV AGENT_CARDS_BASE="/app/mcp_server/agent_cards"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:10100/health || exit 1

# Run
CMD ["python", "main.py"]
'''


def _get_guardian_main_template(context):
    """Get guardian main template"""
    return f'''#!/usr/bin/env python3
"""
Guardian Security Service Main
"""

import uvicorn
from fastapi import FastAPI

app = FastAPI(
    title="Guardian Security Service",
    description="Security service for {context.get('project_name', 'ABI Project')}",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {{"message": "Guardian Security Service", "status": "running"}}

@app.get("/health")
async def health():
    return {{"status": "healthy", "service": "guardian"}}

@app.post("/v1/security/evaluate")
async def evaluate_security(request: dict):
    """Evaluate security policy"""
    action = request.get("action", "unknown")
    resource = request.get("resource_type", "unknown")
    
    # Simple security evaluation
    risk_score = 0.1 if action in ["read", "query"] else 0.5
    allowed = risk_score < 0.7
    
    return {{
        "allowed": allowed,
        "risk_score": risk_score,
        "message": f"{{action}} on {{resource}} evaluated by Guardian",
        "policy_version": "1.0.0"
    }}

@app.get("/v1/policies")
async def get_policies():
    return {{
        "policies": [
            "core_security_policies",
            "{context.get('domain', 'general')}_domain_policies"
        ],
        "status": "active"
    }}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=11438,
        reload=True
    )
'''


def _get_guardian_requirements_template():
    """Get guardian requirements template"""
    return '''# Guardian Security Service Requirements
fastapi>=0.100.0
uvicorn>=0.20.0
pydantic>=2.0.0
requests>=2.31.0
httpx>=0.25.0
cryptography>=41.0.0
fastmcp>=0.1.0
starlette>=0.27.0
'''


def _generate_example_agent_card(context):
    """Generate example agent card for the project"""
    from datetime import datetime
    
    project_name = context.get('project_name', 'ABI Project')
    domain = context.get('domain', 'general')
    
    return {
        "@context": [
            "https://raw.githubusercontent.com/GoogleCloudPlatform/a2a-llm/main/a2a/ontology/a2a_context.jsonld"
        ],
        "@type": "Agent",
        "id": f"agent://example_{domain}",
        "name": f"Example {domain.title()} Agent",
        "description": f"Example agent for {project_name} - {domain} domain operations",
        "url": "http://localhost:8000",
        "version": "1.0.0",
        "capabilities": {
            "streaming": "True",
            "pushNotifications": "True",
            "stateTransitionHistory": "False"
        },
        "defaultInputModes": ["text/plain"],
        "defaultOutputModes": ["text/plain"],
        "supportedTasks": [
            "process_request",
            "analyze_data",
            "generate_response"
        ],
        "llmConfig": {
            "provider": "ollama",
            "model": "llama3.2:3b",
            "temperature": 0.1
        },
        "tools": [],
        "functions": [],
        "embedding": False,
        "prompt": f"You are an example agent for {project_name} in the {domain} domain. Process user requests and provide helpful responses.",
        "skills": [
            {
                "id": "process_request",
                "name": "Request Processing",
                "description": "Process and understand user requests",
                "tags": ["processing", "analysis", domain],
                "examples": ["Process user query", "Analyze request intent"],
                "inputModes": ["text/plain"],
                "outputModes": ["text/plain"]
            }
        ],
        "metadata": {
            "created": datetime.utcnow().isoformat(),
            "generator": "abi-core-cli",
            "version": "1.0.0",
            "project": project_name,
            "domain": domain
        }
    }


def _get_guardian_dockerfile_template():
    """Get guardian Dockerfile template"""
    return '''# Guardian Security Service Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy service
COPY . .

# Expose port
EXPOSE 11438

# Environment variables
ENV ABI_ROLE="Guardian Security"
ENV ABI_NODE="ABI Node"
ENV PYTHONPATH=/app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:11438/health || exit 1

# Run
CMD ["python", "main.py"]
'''