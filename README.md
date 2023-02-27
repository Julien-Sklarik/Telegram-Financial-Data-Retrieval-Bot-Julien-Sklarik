# Telegram Financial Data Retrieval Bot

This Python application launches a Telegram bot that retrieves financial data from any stock and returns it on command. The bot supports two web sources: Yahoo Finance and Deribit. By adding the API key of your portfolio, the bot can also tell you the total equity of your portfolio on command. You can even add a second portfolio and switch between them from Telegram.

The bot also includes a command that tells you which option contracts in your selected portfolio will expire in less than 24 hours. Even better, when you ask for the stock price of a stock, the bot will give you a reminder if any of your options on that stock are going to expire in less than 15 hours. Finally, the bot is fully operational and handles any typing errors.

To use the bot, simply start it by entering the /start command in Telegram. From there, you can enter any of the following commands:

Commands:
/start - Start the bot.
/equity - Get the total equity of your portfolio.
/deribit - Enter a ticker symbol and get the corresponding current asset price from Deribit.
/yahoo - Enter a ticker symbol and get the corresponding current asset price from Yahoo Finance.
/change_portfolio - Switch between portfolios.
/help - Display this message.

The bot will let you know if your command is unrecognized.

If you're interested in using the bot, simply clone this repository and follow the instructions in the README file to get started.

Happy trading!
