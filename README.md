# MCP Server 

A Model Context Protocol (MCP) server built with Python that serves agenda data for an event. 
This project is also a reusable template for building MCP servers.

## Goals

- Learn to build MCP servers with Python.
- Create a template project that can be reused for other MCP servers.
- Provide a step-by-step workshop for the attendees.
- Build a demo MCP server that answers questions about the event agenda.

## Repository layout

```
├── data/                  # Data sources and agenda files
├── documentation/         # Workshop instructions, slides, and reference docs
│   ├── slides.md          # Slide descriptions for the workshop presentation
│   ├── tools.md           # Tool use comparison across LLM providers
│   └── workshop.md        # Step-by-step workshop instructions
├── scripts/               # Utility scripts (data download, etc.)
├── learning.md            # Learning tracker — concepts and reading list
├── ROADMAP.md             # Project iterations and plan
└── CLAUDE.md              # AI assistant working conventions
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install pytest dotenv langchain_core langchain_ollama
```
