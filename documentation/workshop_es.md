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
pip install pytest python-dotenv langchain_core langchain_ollama
```

Crea una cuenta en [ollama.com](https://ollama.com) y obtén una clave de API (https://ollama.com/settings/keys).

Copia `.env.sample` a `.env` y rellena la URL de Ollama Cloud, la clave de API y el modelo:

```bash
cp .env.sample .env
```

Importa los datos de ejemplo en la base de datos:

```bash
python scripts/import_talks.py
```

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

Abre `src/client.py` y léelo. El cliente conecta el LLM con las herramientas:

- `create_llm()` — crea una conexión a un servidor Ollama usando la configuración
  de `src/config.py`.
- `process_query(query)` — el bucle principal:
  1. Envía tu consulta y los esquemas de herramientas al LLM.
  2. Si el LLM responde con una llamada a herramienta → la ejecuta → envía el resultado de vuelta.
  3. Si el LLM responde con texto → lo devuelve (fin).

Ejecuta los tests:

```bash
python -m pytest tests/test_client.py -v
```

Ejecuta el cliente de forma interactiva:

```bash
python -m src.client
```

Prueba algunas consultas:

- "¿Qué charlas hay el 2026-04-20?"
- "Cuéntame sobre la charla de Vibe Coding"
- "¿Qué charlas hay?"

Observa cómo el LLM decide qué herramienta llamar basándose en tu pregunta — tú no
le dices qué herramienta usar.

Escribe `quit` para salir.
