# ABI Core CLI - Estructura Modular

## 📁 Estructura

```
cli/
├── main.py              # CLI principal con configuración base
├── banner.py            # Banner ASCII de ABI
├── commands/            # Comandos modulares
│   ├── __init__.py     # Exports de comandos
│   ├── utils.py        # Utilidades compartidas
│   ├── create.py       # Comandos 'create'
│   ├── add.py          # Comandos 'add'
│   ├── run.py          # Comando 'run'
│   ├── status.py       # Comando 'status'
│   └── info.py         # Comando 'info'
└── README.md           # Esta documentación
```

## 🔧 Arquitectura Modular

### **main.py**
- Configuración base del CLI con Click
- Registro de comandos modulares
- Banner personalizado con Rich
- Entry point principal

### **commands/utils.py**
- Funciones compartidas entre comandos
- Templates de generación de código
- Utilidades de configuración
- Console de Rich compartida

### **Comandos Modulares**

#### **create.py**
- `create project` - Crear nuevos proyectos ABI
- Scaffolding completo de proyectos
- Generación de servicios opcionales

#### **add.py**
- `add agent` - Agregar agentes al proyecto
- `add service` - Agregar servicios (semantic-layer, guardian)
- `add policies` - Agregar políticas de seguridad

#### **run.py**
- `run` - Ejecutar proyecto con Docker Compose
- Soporte para diferentes modos (dev, prod, test)
- Información del sistema y estado

#### **status.py**
- `status` - Estado del proyecto y servicios
- Información de agentes, servicios y políticas
- Estado de contenedores Docker

#### **info.py**
- `info` - Información detallada del proyecto
- Configuración y estructura
- Sugerencias de próximos pasos

## 🚀 Ventajas de la Modularización

### **Mantenibilidad**
- Cada comando en su propio archivo
- Responsabilidades claramente separadas
- Fácil localización de funcionalidad

### **Escalabilidad**
- Agregar nuevos comandos es simple
- Reutilización de utilidades comunes
- Estructura consistente

### **Testabilidad**
- Cada módulo se puede probar independientemente
- Imports específicos para testing
- Mocking más granular

### **Colaboración**
- Múltiples desarrolladores pueden trabajar en paralelo
- Menos conflictos de merge
- Código más legible

## 📝 Agregar Nuevos Comandos

### 1. Crear nuevo archivo de comando
```python
# commands/nuevo_comando.py
import click
from .utils import console

@click.command()
def nuevo_comando():
    """Descripción del nuevo comando"""
    console.print("¡Nuevo comando funcionando!")
```

### 2. Registrar en __init__.py
```python
# commands/__init__.py
from .nuevo_comando import nuevo_comando

__all__ = ['create', 'add', 'run', 'status', 'info', 'nuevo_comando']
```

### 3. Registrar en main.py
```python
# main.py
from .commands import nuevo_comando

cli.add_command(nuevo_comando)
```

## 🧪 Testing

```bash
# Probar imports
python3 test_modular_cli.py

# Probar comandos específicos
python3 -c "import sys; sys.path.append('src'); from abi_core.cli.main import cli; cli(['--help'])"
```

## 🔄 Migración Completada

✅ **Antes**: Todo en `main.py` (1118+ líneas)
✅ **Después**: Modular y organizado
- `main.py`: 37 líneas (solo configuración)
- `commands/`: 5 archivos especializados
- `utils.py`: Funciones compartidas

## 📋 Comandos Disponibles

| Comando | Archivo | Descripción |
|---------|---------|-------------|
| `create project` | `create.py` | Crear nuevo proyecto ABI |
| `add agent` | `add.py` | Agregar agente |
| `add service` | `add.py` | Agregar servicio |
| `add policies` | `add.py` | Agregar políticas |
| `run` | `run.py` | Ejecutar proyecto |
| `status` | `status.py` | Estado del proyecto |
| `info` | `info.py` | Información del proyecto |

## 🆕 **Nuevas Funcionalidades: Agent Cards**

### **Agent Cards Management**

#### **Creación Automática de Agent Cards**
Cuando se agrega un servicio semantic-layer, se crea automáticamente:
- Directorio `services/{service_name}/mcp_server/agent_cards/`
- Agent card de ejemplo con la configuración del proyecto

#### **Comando: `add agent-card`**
Crea agent cards para registro en la capa semántica.

**Sintaxis:**
```bash
abi-core add agent-card --name "AgentName" [OPTIONS]
```

**Opciones:**
- `--name, -n` *(requerido)* - Nombre del agente
- `--description, -d` - Descripción del agente
- `--model` - Modelo LLM (default: llama3.2:3b)
- `--url` - URL del agente (default: http://localhost:8000)
- `--tasks` - Tareas soportadas separadas por comas

**Ejemplo:**
```bash
abi-core add agent-card \
  --name "DataAnalyzer" \
  --description "Agent specialized in data analysis" \
  --model "llama3.2:3b" \
  --url "http://localhost:8001" \
  --tasks "analyze_data,generate_report,process_metrics"
```

#### **Estructura de Agent Card Generada**
```json
{
  "@context": ["https://raw.githubusercontent.com/GoogleCloudPlatform/a2a-llm/main/a2a/ontology/a2a_context.jsonld"],
  "@type": "Agent",
  "id": "agent://dataanalyzer",
  "name": "DataAnalyzer",
  "description": "Agent specialized in data analysis",
  "url": "http://localhost:8001",
  "version": "1.0.0",
  "capabilities": {
    "streaming": "True",
    "pushNotifications": "True",
    "stateTransitionHistory": "False"
  },
  "supportedTasks": ["analyze_data", "generate_report", "process_metrics"],
  "llmConfig": {
    "provider": "ollama",
    "model": "llama3.2:3b",
    "temperature": 0.1
  },
  "skills": [
    {
      "id": "analyze_data",
      "name": "Analyze Data",
      "description": "Analyze Data functionality for DataAnalyzer",
      "tags": ["analyze_data", "processing", "analysis"],
      "examples": ["Execute analyze_data operation"],
      "inputModes": ["text/plain"],
      "outputModes": ["text/plain"]
    }
  ]
}
```

### **Semantic Layer Mejorado**

El semantic layer ahora incluye:

#### **APIs de Gestión de Agentes**
- `GET /v1/agents` - Listar agentes registrados
- `POST /v1/register_agent` - Registrar nuevo agente
- `DELETE /v1/agents/{agent_id}` - Desregistrar agente
- `POST /v1/tools/find_agent` - Buscar agente por query
- `POST /v1/tools/get_agent` - Obtener agente específico

#### **Funcionalidades de Seguridad**
- **Verificación de Disponibilidad**: Solo agentes con agent cards pueden acceder
- **Autorización**: Solo agentes autorizados en el directorio agent_cards
- **Gestión Dinámica**: Registro/desregistro en tiempo real

### **Flujo de Trabajo con Agent Cards**

1. **Crear Proyecto con Semantic Layer**
   ```bash
   abi-core create project --name "MyProject" --with-semantic-layer
   ```

2. **Registrar Agentes**
   ```bash
   abi-core add agent-card --name "MyAgent" --url "http://localhost:8001"
   ```

3. **El Semantic Layer Automáticamente**
   - Carga agent cards al iniciar
   - Proporciona búsqueda semántica
   - Valida disponibilidad de agentes
   - Gestiona registro dinámico

### **Beneficios**

✅ **Control de Acceso**: Solo agentes autorizados  
✅ **Verificación de Disponibilidad**: Detección automática de agentes offline  
✅ **Búsqueda Semántica**: Encuentra el mejor agente para cada tarea  
✅ **Gestión Centralizada**: Un solo punto de registro  
✅ **Seguridad**: Validación de agentes antes del acceso  

La modularización está completa y funcionando correctamente! 🎉