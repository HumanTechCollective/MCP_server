"""Tests for split_for_telegram(), trim_conversation(), and question()."""

from types import SimpleNamespace

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from src import telegram_bot
from src.telegram_bot import split_for_telegram, trim_conversation


def test_under_limit_returns_input_unchanged_as_single_chunk():
    # Fast path: when text fits, the splitter should return it as-is in one
    # chunk, so the caller sends a single message.
    text = "anything\nfitting\nunder the limit"
    chunks = split_for_telegram(text, limit=100)

    assert chunks == [text]


def test_splits_at_line_boundaries():
    # "aaaa\nbbbb" is 9 chars and fits; adding "\ncccc" would reach 14, so
    # "cccc" starts a new chunk.
    chunks = split_for_telegram("aaaa\nbbbb\ncccc", limit=10)

    assert chunks == ["aaaa\nbbbb", "cccc"]


def test_hard_cuts_a_line_longer_than_limit():
    chunks = split_for_telegram("abcdefghij", limit=4)

    assert chunks == ["abcd", "efgh", "ij"]


def test_all_chunks_stay_within_limit():
    text = "short\n" + "x" * 30 + "\n" + "y" * 5 + "\n" + "z" * 25
    chunks = split_for_telegram(text, limit=20)

    assert all(len(c) <= 20 for c in chunks)


def test_multiline_text_under_limit_returns_single_chunk():
    text = "line one\nline two\nline three"
    chunks = split_for_telegram(text, limit=100)

    assert chunks == [text]


def test_over_limit_returns_multiple_chunks():
    # Slow path: when text doesn't fit, the splitter should produce more than
    # one chunk, so the caller sends multiple messages.
    text = "a" * 50 + "\n" + "b" * 50
    chunks = split_for_telegram(text, limit=40)

    assert len(chunks) > 1


def test_trim_conversation_shorter_than_limit_is_unchanged():
    # 2 messages = 1 interaction, well under the cap; nothing should be dropped.
    conversation = ["q1", "a1"]
    trim_conversation(conversation, max_interactions=3)

    assert conversation == ["q1", "a1"]


def test_trim_conversation_at_limit_is_unchanged():
    # Exactly 3 interactions (6 messages) should all be kept.
    conversation = ["q1", "a1", "q2", "a2", "q3", "a3"]
    trim_conversation(conversation, max_interactions=3)

    assert conversation == ["q1", "a1", "q2", "a2", "q3", "a3"]


def test_trim_conversation_drops_oldest_interactions():
    # 5 interactions but cap is 3, so the two oldest pairs should be dropped.
    conversation = ["q1", "a1", "q2", "a2", "q3", "a3", "q4", "a4", "q5", "a5"]
    trim_conversation(conversation, max_interactions=3)

    assert conversation == ["q3", "a3", "q4", "a4", "q5", "a5"]


def test_trim_conversation_modifies_in_place():
    # The Telegram handler relies on in-place mutation because the list is
    # stored in bot_data and shared with process_query.
    conversation = ["q1", "a1", "q2", "a2", "q3", "a3", "q4", "a4"]
    original = conversation
    trim_conversation(conversation, max_interactions=3)

    assert conversation is original


# --- question() tests ---------------------------------------------------------
#
# question() needs a live MCP session + LLM via process_query(), plus Telegram's
# `update` and `context` objects. We replace all of those with minimal stand-ins
# so we can observe how the per-user conversation buffer accumulates and trims
# across repeated calls.


async def fake_process_query(session, llm_with_tools, query, conversation):
    # Stand-in for the real LLM+MCP call. Mirrors the only side effect that the
    # test cares about: appending the (user, assistant) pair to `conversation`.
    answer = f"answer to {query}"
    conversation.append(HumanMessage(content=query))
    conversation.append(AIMessage(content=answer))
    return answer


def make_update(user_id, chat_id, text):
    # SimpleNamespace gives us a dotted-attribute object from kwargs, which is
    # all question() needs from `update` (it only reads three attributes).
    return SimpleNamespace(
        message=SimpleNamespace(text=text),
        effective_user=SimpleNamespace(id=user_id),
        effective_chat=SimpleNamespace(id=chat_id),
    )


def make_context(conversations):
    # Mirrors the shape main() sets up in application.bot_data. session and
    # llm_with_tools are unused because fake_process_query ignores them.
    async def send_message(**kwargs):
        pass

    return SimpleNamespace(
        bot=SimpleNamespace(send_message=send_message),
        bot_data={
            "session": None,
            "llm_with_tools": None,
            "conversations": conversations,
        },
    )


@pytest.fixture
def anyio_backend():
    # anyio's pytest plugin asks which async backend to run tests on. The rest
    # of the project runs on asyncio, so we pin to that.
    return "asyncio"


@pytest.mark.anyio
async def test_third_question_accumulates_three_pairs_for_that_user(monkeypatch):
    # After three questions from the same user, their conversation should hold
    # all three (query, answer) pairs — nothing trimmed yet since the cap is 3.
    monkeypatch.setattr(telegram_bot, "process_query", fake_process_query)
    conversations = {}
    user_id = 42
    ctx = make_context(conversations)

    for i in (1, 2, 3):
        await telegram_bot.question(make_update(user_id, 99, f"q{i}"), ctx)

    stored = conversations[user_id]
    assert [m.content for m in stored] == [
        "q1", "answer to q1",
        "q2", "answer to q2",
        "q3", "answer to q3",
    ]


@pytest.mark.anyio
async def test_fourth_question_drops_the_oldest_pair(monkeypatch):
    # The 4th question pushes past the cap of 3 interactions, so the (q1, a1)
    # pair should be dropped while q2..q4 remain for that user.
    monkeypatch.setattr(telegram_bot, "process_query", fake_process_query)
    conversations = {}
    user_id = 42
    ctx = make_context(conversations)

    for i in (1, 2, 3, 4):
        await telegram_bot.question(make_update(user_id, 99, f"q{i}"), ctx)

    stored = conversations[user_id]
    assert [m.content for m in stored] == [
        "q2", "answer to q2",
        "q3", "answer to q3",
        "q4", "answer to q4",
    ]
