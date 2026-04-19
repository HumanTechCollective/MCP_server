import asyncio
import logging

logging.basicConfig(
    format="%(asctime)s %(name)s %(levelname)s: %(message)s",
    level=logging.INFO,
)

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

from src.config import mcp_server_url, telegram_token, bot_greeting, telegram_error_message, max_interactions, system_prompt
from src.MCP_client import setup_llm_with_tools, process_query, fetch_all_resources

logger = logging.getLogger(__name__)

# Telegram rejects text messages longer than 4096 characters (Bot API limit).
TELEGRAM_MESSAGE_LIMIT = 4096


def trim_conversation(conversation, max_interactions) -> None:
    # One interaction = one human message + one assistant message, so the buffer
    # cap is twice the number of interactions we want to keep.
    max_messages = max_interactions * 2
    if max_messages == 0:
        conversation.clear()
        return
    del conversation[:-max_messages]


def split_for_telegram(text, limit=TELEGRAM_MESSAGE_LIMIT) -> list[str]:
    # Fast path: short enough to send as a single message, no splitting needed.
    if len(text) <= limit:
        return [text]
    # Pack lines into chunks up to `limit` chars, breaking at newlines so the
    # split reads naturally. A single line longer than `limit` is hard-cut.
    chunks = []
    current = ""
    for line in text.split("\n"):
        while len(line) > limit:
            if current:
                chunks.append(current)
                current = ""
            chunks.append(line[:limit])
            line = line[limit:]
        extra = len(line) + (1 if current else 0)
        if len(current) + extra > limit:
            chunks.append(current)
            current = line
        else:
            current = (current + "\n" + line) if current else line
    if current:
        chunks.append(current)
    return chunks


# Start handler. Called when a user sends the /start command.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=update.effective_chat.id, text=bot_greeting)


# Question funtion. This funtion will answer when a user sends a text message to the bot.
async def question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        query = update.message.text
        # Pull the shared MCP session and bound LLM that main() stashed at startup
        session = context.bot_data["session"]
        llm_with_tools = context.bot_data["llm_with_tools"]
        augmented_prompt = context.bot_data["augmented_prompt"]
        # Per-user conversation, created on first message from that user
        conversations = context.bot_data["conversations"]
        conversation = conversations.setdefault(update.effective_user.id, [])
        answer = await process_query(session, llm_with_tools, query, augmented_prompt, conversation)
        # Cap the per-user buffer so conversations don't grow unbounded over time
        trim_conversation(conversation, max_interactions)
        logger.debug("Answer: %s", answer)
        # Split the answer if it is over Telegram's length limit
        for chunk in split_for_telegram(answer):
            await context.bot.send_message(chat_id=update.effective_chat.id, text=chunk)
    except Exception:
        logger.exception("Failed to handle message")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=telegram_error_message,
        )


async def main():
    # Open the MCP session once and keep it alive for the whole bot lifetime
    async with (
        streamable_http_client(mcp_server_url) as (read, write, _),
        ClientSession(read, write) as session,
    ):
        await session.initialize()
        llm_with_tools = await setup_llm_with_tools(session)
        # Pull resources once at startup and append them to the system prompt,
        # so every turn sees the same reference context without re-reading.
        resources_text = await fetch_all_resources(session)
        augmented_prompt = system_prompt + (f"\n\n{resources_text}" if resources_text else "")

        application = ApplicationBuilder().token(telegram_token).build()
        # Stash shared state so handlers can reach it via context.bot_data
        application.bot_data["session"] = session
        application.bot_data["llm_with_tools"] = llm_with_tools
        application.bot_data["augmented_prompt"] = augmented_prompt
        # Per-user conversations: {telegram_user_id: [message, ...]}
        application.bot_data["conversations"] = {}

        # Handler for new conversations (user sends /start)
        application.add_handler(CommandHandler("start", start))
        # Handler for text messages in an open chat
        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), question))

        # Manual lifecycle: run_polling() would block and hide the MCP session scope
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        try:
            # Wait forever; Ctrl+C raises KeyboardInterrupt and triggers cleanup
            await asyncio.Event().wait()
        finally:
            await application.updater.stop()
            await application.stop()
            await application.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
