"""Tests for the client."""

from langchain_ollama import ChatOllama

from src.client import create_llm, process_query


def test_create_llm_returns_chat_ollama():
    llm = create_llm()

    assert isinstance(llm, ChatOllama)


def test_process_query_without_tools():
    result = process_query("Say hello")

    assert isinstance(result, str)
    assert len(result) > 0


def test_process_query_with_tool_all_talks(capsys):
    result = process_query("Que charlas hay?")

    captured = capsys.readouterr()
    assert "Calling tool: get_all_talks" in captured.out
    assert isinstance(result, str)
    assert len(result) > 0


def test_process_query_with_tool_day_talks(capsys):
    result = process_query("What talks are on 2026-04-20?")

    captured = capsys.readouterr()
    assert "Calling tool: get_talks_by_day" in captured.out
    assert isinstance(result, str)
    assert len(result) > 0