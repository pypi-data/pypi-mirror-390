# AI Agent Selector

Selector interactivo de agentes de IA con interfaz CLI.

## Descripción

Este proyecto permite gestionar y ejecutar múltiples agentes de IA que están organizados en carpetas separadas. Cada agente mantiene sus propias dependencias, configuración y archivos aislados del resto del sistema.

**El selector detecta automáticamente los agentes** buscando archivos `.env` en las subcarpetas del directorio de agentes.

## Instalación

1. Clona o descarga este repositorio
2. Instala las dependencias:

```bash
uv sync
```

## Configuración

### 1. Configurar el directorio de agentes

Copia el archivo de ejemplo y configúralo:

```bash
cp .env.example .env
```

Edita `.env` y establece la ruta a tu carpeta de agentes:

```bash
AI_AGENTS_DIR=~/ia
```

### 2. Configurar cada agente

Para que un agente sea detectado, debe tener un archivo `.env` en su carpeta con:

1. Variable **`ALIAS`** (obligatoria): comando a ejecutar
2. Variables de entorno adicionales (opcionales)

Crea un `.env` en cada carpeta de agente. Ejemplo para `~/ia/claude-code/.env`:

```bash
# Comando a ejecutar (OBLIGATORIO)
ALIAS=npx @anthropic-ai/claude-code

# Variables de entorno del agente (OPCIONAL)
ANTHROPIC_API_KEY=tu-clave-aqui
DEBUG=true
```

Puedes usar `agent.env.example` como plantilla.

## Uso

Ejecuta el selector:

```bash
uv run main.py
```

O crea un alias para ejecutarlo desde cualquier directorio:

```bash
alias ai-selector='uv run --project /ruta/a/ai-selector /ruta/a/ai-selector/main.py'
```

**Nota**: Usa `--project` en lugar de `--directory` para que el agente se ejecute en el directorio actual, no en el directorio del proyecto ai-selector. Debes especificar la ruta completa al script después de `--project`.

El selector mostrará un menú interactivo donde podrás:
- Navegar con las flechas ↑/↓
- Seleccionar con Enter
- Cancelar con Ctrl+C

El comando del agente **se ejecuta desde el directorio actual** (no cambia a la carpeta del agente). Las variables de entorno del `.env` del agente se cargan automáticamente.

### Funcionalidades adicionales

- **Limpieza de pantalla**: Antes de ejecutar el agente, se limpia la terminal
- **Registro de ejecuciones**: Cada ejecución se registra en `agent-execution.log` dentro del directorio del agente, incluyendo:
  - Fecha y hora de ejecución
  - Nombre del agente
  - Comando ejecutado
  - Directorio desde donde se ejecutó el selector
  - Variables de entorno cargadas

## Estructura de la carpeta de agentes

Ejemplo de estructura:

```
~/ia/
├── claude-code/
│   ├── node_modules/
│   ├── .env                    ← Contiene ALIAS y variables de entorno
│   ├── agent-execution.log     ← Log de ejecuciones (generado automáticamente)
│   ├── package.json
│   └── package-lock.json
├── crush/
│   ├── node_modules/
│   ├── .env                    ← Contiene ALIAS
│   ├── agent-execution.log     ← Log de ejecuciones
│   ├── package.json
│   └── package-lock.json
└── opencode/
    ├── node_modules/
    ├── .env                    ← Contiene ALIAS y variables de entorno
    ├── agent-execution.log     ← Log de ejecuciones
    ├── package.json
    └── bun.lockb
```

**Nota**: Solo las carpetas con archivo `.env` (que contenga `ALIAS`) serán detectadas como agentes.

## Características

- ✅ Detección automática de agentes mediante archivos `.env`
- ✅ Interfaz CLI interactiva con flechas
- ✅ Comandos configurables vía variable `ALIAS`
- ✅ Ruta configurable mediante variable de entorno
- ✅ Carga automática de variables de entorno del agente
- ✅ Ejecución desde directorio actual (sin cambiar de carpeta)
- ✅ Ejecución interactiva completa (stdin/stdout/stderr)
- ✅ Limpieza automática de pantalla antes de ejecutar
- ✅ Registro de ejecuciones con timestamp en archivo de log

## Desarrollo

### Estructura del código

```
ai-selector/
├── main.py              # Punto de entrada
├── src/
│   ├── __init__.py
│   ├── config.py        # Descubrimiento y modelo de agentes
│   ├── selector.py      # Interfaz interactiva CLI
│   └── executor.py      # Ejecución de agentes
├── agent.env.example    # Plantilla de .env para agentes
├── .env                 # Configuración del selector (crear desde .example)
└── pyproject.toml       # Dependencias del proyecto
```

### Agregar un nuevo agente

1. Crea una carpeta para el agente en `AI_AGENTS_DIR`
2. Instala las dependencias del agente en su carpeta
3. Crea un archivo `.env` con la variable `ALIAS` y cualquier variable de entorno necesaria
4. Ejecuta el selector - el agente será detectado automáticamente

## Licencia

MIT
