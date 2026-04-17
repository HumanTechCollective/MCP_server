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
        "SELECT title, start_time, speakers, topic, stage, languages "
        "FROM talks WHERE day = ? ORDER BY start_time",
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
            "stage": row[4],
            "languages": row[5],
        }
        for row in rows
    ]
    return results


def get_all_talks() -> list[dict]:
    """Return all talks in the agenda."""
    connection = sqlite3.connect(database_file)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT title, day, start_time, speakers, topic FROM talks ORDER BY day, start_time"
    )
    rows = cursor.fetchall()
    connection.close()

    results = [
        {
            "title": row[0],
            "day": row[1],
            "start_time": row[2],
            "speakers": row[3],
            "topic": row[4],
        }
        for row in rows
    ]
    return results


def get_talk_details(title) -> dict:
    """Return full details for a talk matching the given title."""
    connection = sqlite3.connect(database_file)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT day, start_time, end_time, description, speakers, stage, languages "
        "FROM talks WHERE title LIKE ?",
        (f"%{title}%",),
    )
    row = cursor.fetchone()
    connection.close()

    if not row:
        return {"error": f"No talk found matching '{title}'"}

    return {
        "day": row[0],
        "start_time": row[1],
        "end_time": row[2],
        "description": row[3],
        "speakers": row[4],
        "stage": row[5],
        "languages": row[6],
    }


# --- Tool schema ---
# This tells the LLM what tools are available, what they do,
# and what parameters they expect.

tools = [
    {
        "name": "get_talks_by_day",
        "description": "Get all talks scheduled for a given day. Returns a list with each talk's title, start time, speakers, topic, stage (room), and languages.",
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
    },
    {
        "name": "get_all_talks",
        "description": "Get all talks in the agenda. Returns a list with each talk's day, title, start time, speakers, and topic.",
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "get_talk_details",
        "description": "Get details of a specific talk by title. Returns the day, start time, end time, description, speakers, stage (room), and languages. Supports partial title matching.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "The title (or part of the title) of the talk to search for"
                }
            },
            "required": ["title"]
        }
    }
]


# --- Tool mapping and execution ---
# The mapping connects tool names (strings) to the actual Python functions.
# execute_tool looks up the function by name and calls it.

tool_functions = {
    "get_talks_by_day": get_talks_by_day,
    "get_all_talks": get_all_talks,
    "get_talk_details": get_talk_details
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
