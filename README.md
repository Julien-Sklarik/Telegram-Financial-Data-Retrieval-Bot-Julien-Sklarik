# Telegram Financial Data Retrieval Bot

This bot is designed for traders who want to stay up-to-date on their portfolio and financial data. With just a few simple commands, you can retrieve the latest stock prices and track the expiration dates of your option contracts. For instance, the bot will tell if any option contracts in your selected portfolio will expire in less than 24 hours. Additionally, when you ask for a stock price, the bot will give you a reminder if any of your options on that stock are going to expire in less than 15 hours. Plus, you have the flexibility to choose your data source between Yahoo Finance or Deribit.

In addition, the bot provides a command to retrieve the total equity of your portfolio on demand. You can also switch between two portfolios at any time, which is useful for those who manage multiple accounts.

The bot is designed to handle any typing errors you may make, ensuring a smooth experience. Furthermore, if you ask for the stock price of a stock and have options that will expire in less than 15 hours, the bot will provide you with a reminder.

## Commands

- `/start` - Start the bot
- `/equity` - Get the total equity of your portfolio
- `/deribit` - Enter a ticker symbol and get the corresponding current asset price from Deribit
- `/yahoo` - Enter a ticker symbol and get the corresponding current asset price from Yahoo Finance
- `/change_portfolio` - Switch between portfolios
- `/help` - Display this message
