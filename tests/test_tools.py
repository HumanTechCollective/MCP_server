"""Tests for tool functions."""

import json

from src.tools import execute_tool, get_talks_by_day

event_day = "2026-04-20"
test_data = [{"title":"Future of Programming: What's our place in the world of coding machines?",
              "start_time":"09:55"},
             {"title":"",
              "start_time":"11:05"}]


def test_get_talks_by_day_returns_all_talks():
    talks = get_talks_by_day(event_day)

    assert len(talks) == 38


def test_get_talks_by_day_ordered_by_start_time():
    talks = get_talks_by_day(event_day)

    assert talks[0]["start_time"] == test_data[0]["start_time"]
    assert talks[1]["start_time"] == test_data[1]["start_time"]


def test_execute_tool_calls_get_talks_by_day():
    result = execute_tool("get_talks_by_day", {"day": event_day})

    talks = json.loads(result)
    assert len(talks) == 38
    assert talks[0]["title"] == test_data[0]["title"]
