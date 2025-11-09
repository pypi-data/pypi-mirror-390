# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Model Serving Options**: New `--model-serving` flag for `create project` command
  - `centralized`: Single shared Ollama service for all agents (recommended for production)
  - `distributed`: Each agent has its own Ollama instance (default, current behavior)
- Centralized Ollama service template in `compose.yaml.j2` with healthcheck
- `model_serving` configuration field in `runtime.yaml` for persistent project settings
- Dynamic agent configuration in `add agent` command based on project's model serving mode
- Automatic detection and configuration of Ollama connectivity per agent

### Changed
- `add agent` command now reads `model_serving` from `runtime.yaml` to configure agents appropriately
- Agent Docker Compose configuration adapts automatically to centralized/distributed mode
- Improved feedback messages showing which model serving mode is being used

### Removed
- **abi_mcp module**: Removed unused MCP client wrapper (not integrated in codebase)
- **agents_d directory**: Removed duplicate scripts (real scripts are in abi-image Docker base)

### Fixed
- Cleaned up unused code and duplicate files in package structure

## [0.1.0b28] - 2025-01-XX

### Added
- Initial beta release
- Project scaffolding with `create project` command
- Agent creation with `add agent` command
- Semantic layer service support
- Guardian security service support
- OPA policy integration
- A2A protocol support
- MCP server integration
- Docker Compose orchestration
- Agent cards for semantic discovery

### Documentation
- Comprehensive README with examples
- CLI command documentation
- Architecture overview
- Quick start guide

---

## Migration Guide

### Upgrading from 0.1.0b28 to 0.1.0b29

**No breaking changes** - All existing projects will continue to work as before.

#### New Projects

When creating new projects, you can now choose the model serving strategy:

```bash
# Centralized mode (recommended for production)
abi-core create project my-app --model-serving centralized

# Distributed mode (default, same as before)
abi-core create project my-app --model-serving distributed
# or simply
abi-core create project my-app
```

#### Existing Projects

Existing projects without `model_serving` in their `runtime.yaml` will automatically use `distributed` mode (current behavior). No changes needed.

To migrate an existing project to centralized mode:

1. Edit `.abi/runtime.yaml` and add:
   ```yaml
   project:
     # ... existing fields
     model_serving: "centralized"
   ```

2. Add the centralized Ollama service to your `compose.yaml`:
   ```yaml
   services:
     myproject-ollama:
       image: ollama/ollama:latest
       container_name: myproject-ollama
       ports:
         - "11434:11434"
       volumes:
         - ollama_data:/root/.ollama
       environment:
         - OLLAMA_HOST=0.0.0.0
       networks:
         - myproject-network
       restart: unless-stopped
   
   volumes:
     ollama_data:
       driver: local
   ```

3. Update existing agents to use the centralized service (optional, but recommended):
   - Remove individual Ollama ports (e.g., `11435:11434`)
   - Change `OLLAMA_HOST` to `http://myproject-ollama:11434`
   - Set `START_OLLAMA=false` and `LOAD_MODELS=false`
   - Add `depends_on: [myproject-ollama]`
   - Remove individual `ollama_data` volumes

---

## Model Serving Comparison

| Feature | Centralized | Distributed |
|---------|-------------|-------------|
| Ollama instances | 1 shared | 1 per agent |
| Resource usage | Lower | Higher |
| Model management | Centralized | Per-agent |
| Isolation | Shared | Complete |
| Recommended for | Production | Development |
| Port conflicts | None | Possible |
| Startup time | Faster (agents) | Slower |

---

**Note**: Guardian service always maintains its own Ollama instance for security isolation, regardless of the chosen mode.
