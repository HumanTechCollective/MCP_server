"""Tests for split_for_telegram()."""

from src.telegram_bot import split_for_telegram


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
