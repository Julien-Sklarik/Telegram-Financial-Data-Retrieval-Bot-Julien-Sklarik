import asyncio
import string

import numpy as np
import yfinance as yf  # pip install yfinance --upgrade
from telegram import ForceReply, ReplyKeyboardRemove, Update
from telegram.ext import CallbackContext, ContextTypes, ConversationHandler

import deribit_functions as deribit_fun

'''
The following functions are called every time the Bot receives a Telegram message that contains the corresponding command.
'''

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hello {user.mention_html()}! Please type /help to see my commands.",
        reply_markup=ForceReply(selective=True),)
    await deribit_fun.expiry_notification(update)

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Commands: \n /start - Start the bot.\
                                                \n /equity - Get the total equity of your portfolio. \
                                                \n /deribit - Enter a ticker symbol and get the corresponding current asset price from Deribit. \
                                                \n /yahoo - Enter a ticker symbol and get the corresponding current asset price from Yahoo Finance. \
                                                \n /change_portfolio - Switch between portfolios.\
                                                \n /help - Display this message. \
                                                \n I will tel you if your command is unrecognized.")

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """This command filter reply to all commands that were not recognized by the previous handlers."""
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

async def equity(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Retrieve the total equity of your portfolio."""
    total_usd_equity = await deribit_fun.get_equity()
    await update.message.reply_text("The total equity of your portfolio is {eq}$.".format(eq=total_usd_equity))

async def change_portfolio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Changed the portfolio considered by the bot."""
    portfolio_name = deribit_fun.change_portfolio()
    await update.message.reply_text("The portfolio considered by this bot is now: {po}.".format(po = portfolio_name))

async def deribit(update: Update, context: CallbackContext, ticker: str = None) -> None:
    """Ask the ticker symbol."""
    await update.message.reply_html(
        rf"Please enter the ticker symbol of an asset available on Deribit (e.g: SOL), or type /cancel.",
        reply_markup=ForceReply(selective=True),
    )
    return 1 # This indicates to follow with the function n°1, "deribit_ticker".

async def yahoo(update: Update, context: CallbackContext, ticker: str = None) -> None:
    """Ask the ticker symbol."""
    await update.message.reply_html(
        rf"Please enter the ticker symbol of your choice (e.g: AAPL), or type /cancel.",
        reply_markup=ForceReply(selective=True),
    )
    return 2 # This indicates to follow with the function n°2, "yahoo_ticker".

async def deribit_ticker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Find the stock price for a given ticker on Deribit."""
    ticker = update.message.text.upper()
    recognise = False
    try:
        share_price = asyncio.run(deribit_fun.get_quote(ticker))
        message = f"{ticker} share price: {share_price}$."
        recognise = True
    except:
        message = f"The ticker symbol \"{ticker}\" wasn't recognise."
    await update.message.reply_text(message)
    if recognise:
        await deribit_fun.expiry_reminder(update, ticker)
    return ConversationHandler.END

async def yahoo_ticker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Find the stock price for a given ticker on Yahoo Finance."""
    ticker = update.message.text.upper()
    try:
        share_price = np.round(yf.Ticker(ticker).history(period="1d").Close.values.tolist()[-1], 2)
        message = f"{ticker} share price: {share_price}$."
    except:
        message = f"The ticker symbol \"{ticker}\" wasn't recognise."
    await update.message.reply_text(message)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    await update.message.reply_text(
        "Ok, let me know if you change your mind.", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END