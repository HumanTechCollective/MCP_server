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

from src.config import mcp_server_url, telegram_token, bot_greeting, telegram_error_message
from src.MCP_client import setup_llm_with_tools, process_query

logger = logging.getLogger(__name__)


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
        # Per-user conversation, created on first message from that user
        conversations = context.bot_data["conversations"]
        conversation = conversations.setdefault(update.effective_user.id, [])
        answer = await process_query(session, llm_with_tools, query, conversation)
        logger.debug("Answer: %s", answer)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=answer)
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

        application = ApplicationBuilder().token(telegram_token).build()
        # Stash shared state so handlers can reach it via context.bot_data
        application.bot_data["session"] = session
        application.bot_data["llm_with_tools"] = llm_with_tools
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
