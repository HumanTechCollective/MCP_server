# Construye un servidor MCP con Python

También disponible en: [English](workshop.md)

> Taller práctico donde construiremos paso a paso un chatbot que responde preguntas
> sobre una agenda de charlas. Empezaremos conectando herramientas (tools) a un LLM
> y terminaremos encapsulándolas en un servidor Model Context Protocol (MCP)
> reutilizable.

## Qué vamos a construir

Un servidor Model Context Protocol (MCP) que permite a un asistente de IA responder
preguntas sobre los datos almacenados.

## Requisitos previos

- Python 3.10 o superior
- Un editor de texto o IDE
- Conocimientos básicos de Python
- Comprensión básica de los Large Language Models (LLMs) — qué son y qué hacen

## 0. Configuración

Clona el repositorio e instala las dependencias:

```bash
git clone https://github.com/HumanTechCollective/MCP_server.git
cd MCP_server
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install pytest python-dotenv langchain_core langchain_ollama "mcp[cli]"
```

### Configuración del LLM

Copia `.env.sample` a `.env`:

```bash
cp .env.sample .env
```

Tienes dos opciones para el backend del LLM:

#### Opción 1: Ollama Cloud

Crea una cuenta en [ollama.com](https://ollama.com) y obtén una [clave de API](https://ollama.com/settings/keys).

Rellena tu `.env`:

```
OLLAMA_URL=https://ollama.com
OLLAMA_API_KEY=<tu clave de API>
```

#### Opción 2: Tu propio servidor Ollama

Instala Ollama y descarga un modelo:

```bash
sudo apt install curl
curl -fsSL https://ollama.com/install.sh | sh
ollama pull gemma4
```

Rellena tu `.env`:

```
OLLAMA_URL=http://localhost:11434
OLLAMA_API_KEY=
```

> **Nota:** Puedes usar un modelo más pequeño en lugar de `gemma4`. Consulta los
> [modelos disponibles con soporte de herramientas](https://ollama.com/search?c=tools).
> Para usar un modelo diferente, descárgalo con `ollama pull <modelo>` y actualiza
> el nombre del modelo en [src/config.py](src/config.py).

## 1. Herramientas (Tools)

Las herramientas son funciones que pones a disposición de un LLM. El LLM no puede
ejecutarlas — solo puede pedirle a tu cliente que las ejecute.

El flujo de uso de herramientas funciona así: describes cada herramienta (nombre, qué
hace, qué entradas necesita). Cuando el LLM decide que necesita una, envía una
solicitud. Tu código ejecuta la función y devuelve el resultado. El LLM entonces usa
ese resultado para responder al usuario.

Más información en: `documentation/tools.md`

### Funciones de herramientas

Abre `src/tools.py` y léelo. El archivo tiene tres secciones:

**Funciones de herramientas** — funciones Python que consultan una base de datos con
datos de la agenda. Cada función tiene una entrada y salida claras:

- `get_all_talks()` — devuelve todas las charlas de la agenda.
- `get_talks_by_day(day)` — devuelve las charlas de un día específico.
- `get_talk_details(title)` — devuelve los detalles de una charla que coincida con el título dado.

**Esquema de herramientas** — una lista de diccionarios que describen cada herramienta
al LLM: su nombre, qué hace y qué parámetros espera. Esto es lo que el LLM lee para
decidir qué herramienta llamar.

**Mapeo y ejecución de herramientas** — un diccionario que conecta los nombres de las
herramientas (cadenas de texto del LLM) con las funciones Python reales, y una función
`execute_tool` que busca la función por nombre, la ejecuta y devuelve el resultado
como cadena de texto.

Ejecuta los tests para verificar que todo funciona:

```bash
python -m pytest tests/test_tools.py -v
```

## 2. El cliente (v1)

Para invocar las herramientas necesitamos un cliente LLM. El cliente es la pieza que
se sitúa entre el usuario y el LLM, gestionando el ir y venir de las llamadas a
herramientas.

Abre `src/tools_client.py` y léelo. El cliente conecta el LLM con las herramientas:

- `create_llm()` — crea una conexión a un servidor Ollama usando la configuración
  de `src/config.py`.
- `process_query(query)` — el bucle principal:
  1. Envía tu consulta y los esquemas de herramientas al LLM.
  2. Si el LLM responde con una llamada a herramienta → la ejecuta → envía el resultado de vuelta.
  3. Si el LLM responde con texto → lo devuelve (fin).

Ejecuta los tests:

```bash
python -m pytest tests/test_tools_client.py -v
```

Ejecuta el cliente de forma interactiva:

```bash
python -m src.tools_client
```

Prueba algunas consultas:

- "¿Qué charlas hay el 2026-04-20?"
- "Cuéntame sobre la charla de Vibe Coding"
- "¿Qué charlas hay?"

Observa cómo el LLM decide qué herramienta llamar basándose en tu pregunta — tú no
le dices qué herramienta usar.

Escribe `quit` para salir.


## 3. Servidor MCP

Para compartir nuestras herramientas con cualquier aplicación compatible con
Model Context Protocol (MCP), las encapsulamos en un servidor MCP.

Abre [src/MCP_server.py](../src/MCP_server.py). Es una copia de
[src/tools.py](../src/tools.py) con unos pocos cambios:

**1. Crear el servidor**

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("agenda")
```

`FastMCP` es la clase principal del servidor del SDK de MCP. El nombre
(`"agenda"`) identifica este servidor a los clientes.

**2. Registrar cada herramienta usando un decorador**

```python
@mcp.tool()
def get_all_talks() -> list[dict]:
    """Return all talks in the agenda."""
    ...
```

El decorador `@mcp.tool()` registra la función como una herramienta MCP.
FastMCP genera el esquema de la herramienta automáticamente — por lo que la
lista manual `tools_schema` y el diccionario `tool_mapping` de `src/tools.py`
ya no son necesarios.

**3. Ejecutar el servidor**

MCP admite dos transportes principales: **stdio** (más simple, solo local) y
**HTTP** (para servidores remotos). Mostraremos ambos.

### 3.1 Transporte stdio

```python
if __name__ == "__main__":
    mcp.run(transport='stdio')
```

`stdio` significa que el servidor se comunica con su cliente a través de la
entrada/salida estándar. El cliente lanza el servidor como un subproceso e
intercambia mensajes MCP a través de sus tuberías (pipes). Este es el método más simple.

Inicia el servidor:

```bash
python -m src.MCP_server
```

Se quedará esperando a que un cliente MCP se conecte. Pulsa `Ctrl+C` para detenerlo.

#### Opcional: conectarlo a Claude Code

Si usas Claude Code, puedes permitirle llamar a estas herramientas directamente.
Crea `.mcp.json` en la raíz del repositorio:

```json
{
  "mcpServers": {
    "agenda": {
      "command": "${HOME}/MCP_server/.venv/bin/python",
      "args": ["-m", "src.MCP_server"],
      "cwd": "${HOME}/MCP_server"
    }
  }
}
```

Ajusta las rutas para que coincidan con el lugar donde clonaste el repositorio.
Reinicia Claude Code y pregúntale sobre la agenda — lanzará el servidor y
llamará a las herramientas MCP para responder.

### 3.2 Transporte HTTP

Cambia el transporte:

```python
if __name__ == "__main__":
    mcp.run(transport='streamable-http')
```

Con `streamable-http`, el servidor se ejecuta como un proceso web autónomo que
escucha en `http://127.0.0.1:8000/mcp`, y los clientes se conectan por HTTP.
Esto es lo que permite tener servidores MCP *remotos* (alojados en otro sitio,
compartidos entre clientes).

> **Nota:** El host y el puerto están definidos en [src/config.py](../src/config.py)
> como `mcp_host` y `mcp_port`, y la URL completa como `mcp_server_url`.
> Cámbialos ahí si necesitas un host o puerto diferente.

Inicia el servidor:

```bash
python -m src.MCP_server
```

> **Nota:** Visitar `http://127.0.0.1:8000/mcp` en un navegador devolverá un
> error `406 Not Acceptable`. Es lo esperado — el endpoint requiere cabeceras
> MCP (`Accept: application/json, text/event-stream`) que los navegadores no
> envían. El 406 indica que el servidor está funcionando correctamente.

#### Opcional: conectarlo a Claude Code

Actualiza `.mcp.json`:

```json
{
  "mcpServers": {
    "agenda": {
      "type": "http",
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}
```

Asegúrate de que el servidor esté en ejecución antes de que Claude Code se conecte.


## 4. El cliente (v2): cliente MCP

En la sección 2 construimos un cliente que importaba `tools_schema` y `tool_mapping` desde `src/tools.py`. 

Ahora que las herramientas (tools) estan en el servidor MCP, podemos escribir un cliente que **descubra las herramientas en tiempo de ejecución**. Le pregunta al servidor
"¿qué herramientas tienes?", recibe los esquemas y se los pasa al LLM. El
cliente ya no necesita saber nada sobre la agenda — solo necesita saber hablar
MCP.

Abre [src/mcp_client.py](../src/mcp_client.py). Comparado con el cliente v1, hay cuatro diferencias clave:

- **Conectarse al servidor.** `streamable_http_client` + `ClientSession` abren
  una conexión con el servidor MCP que se ejecuta en `http://127.0.0.1:8000/mcp`.
- **Descubrir las herramientas.** `session.list_tools()` le pide al servidor sus
  herramientas en lugar de importarlas desde un módulo de Python.
- **Adaptar el esquema.** `mcp_tool_to_schema()` convierte cada definición de
  herramienta MCP al formato de diccionario que `bind_tools` espera.
- **Usar a las herramientas.** `session.call_tool(name, args)` ejecuta la
  herramienta en el servidor por MCP — el cliente nunca importa ni ejecuta la
  función Python.

El descubrimiento de las herramientas, la adaptación del esquema y la llamada a
`bind_tools` están agrupados en la funcion auxiliar `setup_llm_with_tools(session)`, 
que devuelve un LLM listo para usar. Mantenerlo como una función aparte permite que 
otros puntos de entrada (un bot de Telegram, una aplicación web, …) reutilicen la misma 
configuración sin duplicar código.

### Ejecútalo

Necesitas **dos terminales**: uno para el servidor y otro para el cliente.

En el primer terminal, inicia el servidor MCP con HTTP (de la sección 3.2):

```bash
python -m src.MCP_server
```

En el segundo terminal, inicia el cliente:

```bash
python -m src.mcp_client
```
