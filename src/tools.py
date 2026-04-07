"""Tool functions that query the agenda database."""

import json
import sqlite3

from src.config import database_file


# --- Tool functions ---


def get_talks_by_day(day) -> list[dict]:
    """Return all talks for a given day."""
    connection = sqlite3.connect(database_file)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT title, start_time, speakers, topic FROM talks WHERE day = ? ORDER BY start_time",
        (day,)
    )
    rows = cursor.fetchall()
    connection.close()

    results = [
        {
            "title": row[0],
            "start_time": row[1],
            "speakers": row[2],
            "topic": row[3],
        }
        for row in rows
    ]
    return results


# --- Tool schema ---
# This tells the LLM what tools are available, what they do,
# and what parameters they expect.

tools = [
    {
        "name": "get_talks_by_day",
        "description": "Get all talks scheduled for a given day. Returns a list with each talk's title, start time, speakers, and topic.",
        "input_schema": {
            "type": "object",
            "properties": {
                "day": {
                    "type": "string",
                    "description": "The date to search for, in YYYY-MM-DD format (e.g. '2026-04-20')"
                }
            },
            "required": ["day"]
        }
    }
]


# --- Tool mapping and execution ---
# The mapping connects tool names (strings) to the actual Python functions.
# execute_tool looks up the function by name and calls it.

tool_functions = {
    "get_talks_by_day": get_talks_by_day
}


def execute_tool(tool_name, tool_args) -> str:
    """Execute a tool by name and return the result as a string."""
    result = tool_functions[tool_name](**tool_args)

    if isinstance(result, list):
        result = json.dumps(result, indent=2)
    elif isinstance(result, dict):
        result = json.dumps(result, indent=2)
    else:
        result = str(result)

    return result
