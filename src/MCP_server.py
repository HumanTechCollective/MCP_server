import os
import json
import sqlite3
from mcp.server.fastmcp import FastMCP
from src.config import database_file, mcp_host, mcp_port


# Initialize FastMCP server
mcp = FastMCP("agenda", host=mcp_host, port=mcp_port)

# --- Tool functions ---
"""Tool functions that query the agenda database."""

@mcp.tool()
def get_talks_by_day(day) -> list[dict]:
    """Return all talks for a given day, including title, start time, speakers, topic, stage, and languages."""
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

@mcp.tool()
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

@mcp.tool()
def get_talk_details(title) -> dict:
    """Return full details for a talk matching the given title: day, start time, end time, description, speakers, stage, and languages."""
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


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='streamable-http')