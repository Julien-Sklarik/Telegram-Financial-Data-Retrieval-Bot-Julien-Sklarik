import logging

import nest_asyncio
import telegram  # pip install python-telegram-bot --upgrade
import telegram.ext
from telegram.ext import (ApplicationBuilder, CommandHandler,
                          ConversationHandler, MessageHandler, filters)

import command_functions as comm

# The token of the bot used:
my_token = ""

# The portfolio API keys are in deribit_functions.py.

# The following part is for setting up logging module, to know when (and why) things don't work as expected.
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = ApplicationBuilder().token(my_token).read_timeout(30).write_timeout(30).build()

    nest_asyncio.apply()
    
    # The different commands - answer in Telegram
    start_handler = CommandHandler("start", comm.start)
    help_handler = CommandHandler("help", comm.help)
    share_price_deribit_handler =  ConversationHandler(
        entry_points=[CommandHandler("deribit", comm.deribit)],
        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, comm.deribit_ticker)],
        },
        fallbacks=[CommandHandler("cancel", comm.cancel)]
    )
    share_price_yahoo_handler =  ConversationHandler(
        entry_points=[CommandHandler("yahoo", comm.yahoo)],
        states={
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, comm.yahoo_ticker)],
        },
        fallbacks=[CommandHandler("cancel", comm.cancel)]
    )
    equity_handler = CommandHandler("equity", comm.equity)
    change_portfolio_handler = CommandHandler("change_portfolio", comm.change_portfolio)
    unknown_handler = MessageHandler(filters.COMMAND, comm.unknown)

    # To tell the bot to listen to commands like /start, we register CommandHandlers in the application.
    application.add_handler(start_handler)
    application.add_handler(help_handler)
    application.add_handler(share_price_deribit_handler)
    application.add_handler(share_price_yahoo_handler)
    application.add_handler(equity_handler)
    application.add_handler(change_portfolio_handler)
    application.add_handler(unknown_handler)
    
    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == "__main__":
    main()