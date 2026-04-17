"""Tests for tool functions."""

import json

from src.tools import execute_tool, get_all_talks, get_talk_details, get_talks_by_day

event_day = "2026-04-20"


def test_get_talks_by_day_returns_talks_with_expected_fields():
    talks = get_talks_by_day(event_day)

    assert len(talks) > 0
    first = talks[0]
    for key in ("title", "start_time", "speakers", "topic", "stage", "languages"):
        assert key in first


def test_get_talks_by_day_ordered_by_start_time():
    talks = get_talks_by_day(event_day)

    start_times = [t["start_time"] for t in talks]
    assert start_times == sorted(start_times)


def test_execute_tool_calls_get_talks_by_day():
    result = execute_tool("get_talks_by_day", {"day": event_day})

    talks = json.loads(result)
    assert len(talks) > 0
    assert "title" in talks[0]


def test_get_all_talks_covers_multiple_days():
    talks = get_all_talks()

    assert len(talks) > 0
    days = {t["day"] for t in talks}
    assert len(days) > 1


def test_get_talk_details_returns_all_expected_fields():
    # Search a known-stable talk title substring.
    result = get_talk_details("Vibe Coding")

    for key in ("day", "start_time", "end_time", "description", "speakers", "stage", "languages"):
        assert key in result


def test_get_talk_details_not_found():
    result = get_talk_details("nonexistent talk")

    assert "error" in result
