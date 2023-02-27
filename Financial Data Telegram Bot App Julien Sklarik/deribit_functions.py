import asyncio
import datetime as dt
import json
from datetime import datetime

import websockets
from telegram import Update

'''
The following functions are used to retrieve data from Deribit Options Exchange API.
'''
# Your test portfolio API keys:
portfolio_name = "test_portfolio"
client_id = "" # The client id of your first portfolio
client_secret = "" # The client secret of your first portfolio
www_or_test = "www"

def change_portfolio():
    """Switch between portfolios and return the name of the new portfolio"""
    global portfolio_name, client_id, client_secret, www_or_test
    if portfolio_name == "test_portfolio2":
        client_id = "" # The client id of your first portfolio
        client_secret = "" # The client secret of your first portfolio
        www_or_test = "www"
        portfolio_name = "test_portfolio"
        return "test_portfolio"
    elif portfolio_name == "test_portfolio":
        client_id = "" # The client id of your second portfolio
        client_secret = "" # The client secret of your second portfolio
        www_or_test = "test"
        portfolio_name = "test_portfolio2"
        return "test_portfolio2"


async def call_api(msg):
    """To get the latest asset prices from Deribit API."""
    async with websockets.connect('wss://test.deribit.com/ws/api/v2') as websocket:
        await websocket.send(msg)
        while websocket.open:
            response = await websocket.recv()
            return response

def async_loop(message):
    """To wait for the API response."""
    return asyncio.get_event_loop().run_until_complete(call_api(message))

async def get_quote(instrument):
    """Function preparing our request for Deribit API."""
    msg1 = \
        {
            "jsonrpc": "2.0",
            "id": 2805,
            "method": "public/ticker",
            "params": {
                "instrument_name": instrument +'-PERPETUAL',
                "kind": "future"
            }
        }
    quote = json.loads(async_loop(json.dumps(msg1)))
    return float(quote['result']['index_price'])

async def get_equity():
    """Function calculating the total equity of our portfolio"""
    async with websockets.connect(f'wss://{www_or_test}.deribit.com/ws/api/v2') as websocket:
        currencies = ["BTC", "ETH", "SOL", "USDC"]
        total_equity = 0
        te= 0
        # Authenticate the connection using public/auth method:
        auth_msg = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "public/auth",
            "params": {
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret
            }
        }
        await websocket.send(json.dumps(auth_msg))
        await websocket.recv()
        # Get the account equity for each currency and add them:
        for currency in currencies:
          account_msg = {
              "jsonrpc": "2.0",
              "id": 2,
              "method": "private/get_account_summary",
              "params": {
                  "currency": currency
              }
          }
          await websocket.send(json.dumps(account_msg))
          account_response = await websocket.recv()
          equity = json.loads(account_response)["result"]["equity"]
          # Convert equity to USD:
          if currency != "USDC":
            ticker_msg = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "public/ticker",
                "params": {
                    "instrument_name": f"{currency}-PERPETUAL"
                }
            }
            await websocket.send(json.dumps(ticker_msg))
            ticker_response = await websocket.recv()
            usd_price = json.loads(ticker_response)["result"]["last_price"]
          else:
            usd_price = 1
          te += equity
          usd_equity = equity * usd_price
          total_equity += usd_equity
    return round(total_equity,2)

async def expiry_reminder(update: Update, ticker):
    """Communication with Deribit API: authentication and getter. 
    Then, the bot sends the relevant info to the telegram group."""
    async with websockets.connect(f'wss://{www_or_test}.deribit.com/ws/api/v2') as websocket:
        instrument_expiring_today = []
        instrument_expiring_tomorrow = []
        now = datetime.now(dt.timezone.utc)
        tomorrow = now + dt.timedelta(days=1)
        current_time = now.strftime("%d%b%y").upper()
        tomorrow_time = tomorrow.strftime("%d%b%y").upper()
        # Authenticate the connection using public/auth method:
        auth_msg = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "public/auth",
            "params": {
                "grant_type": "client_credentials",
                "client_id": client_id, # Here you can put your own portfolio info.
                "client_secret": client_secret
            }
        }
        await websocket.send(json.dumps(auth_msg))
        await websocket.recv() # auth_response = await websocket.recv()
        # Get the options' info and save the relevant results by organizing them in two lists:
        request_msg = {
        "jsonrpc" : "2.0",
        "id" : 9367,
        "method" : "private/get_user_trades_by_currency",
        "params" : {
            "currency" : ticker,
            "count" : 20
        }
        }
        await websocket.send(json.dumps(request_msg))
        request_response = await websocket.recv()
        for trade in json.loads(request_response)["result"]["trades"]:
            name = trade["instrument_name"]
            expiry = name.split("-")[1]
            if expiry == current_time: # Here I store the instrument names between the two lists corresponding to the two possible messages of the Bot. 
                instrument_expiring_today.append(name)
            elif expiry == tomorrow_time:
                instrument_expiring_tomorrow.append(name)
        await websocket.close()
    now = datetime.now(dt.timezone.utc)
    target_time = now.replace(hour=8, minute=0, second=0, microsecond=0)
    time_diff = target_time - now
    if instrument_expiring_today: # Here, I send the messages.
        if now.hour < 8:
          hours_remaining = int(time_diff.total_seconds() / 3600)+1
          await update.message.reply_text("Reminder for Today: You have {nb_contract} option contract(s) expiring in less than {remaining_time} hours:".format(nb_contract=len(instrument_expiring_today), remaining_time=hours_remaining))
          for option in instrument_expiring_today:
              await update.message.reply_text(option)
    if instrument_expiring_tomorrow:
        time_diff += dt.timedelta(days=1)
        hours_remaining = int(time_diff.total_seconds() / 3600)+1
        await update.message.reply_text("(Reminder) You have {nb_contract} option contract(s) expiring in less than {remaining_time} hours:".format(nb_contract=len(instrument_expiring_tomorrow), remaining_time=hours_remaining))
        for option in instrument_expiring_tomorrow:
            await update.message.reply_text(text=option)

async def expiry_notification(update: Update):
    """Communication with Deribit API: authentication and getter. 
    Then, the bot sends the relevant info to the telegram group."""
    async with websockets.connect(f'wss://{www_or_test}.deribit.com/ws/api/v2') as websocket:
        instrument_expiring_today = []
        instrument_expiring_tomorrow = []
        now = datetime.now(dt.timezone.utc)
        tomorrow = now + dt.timedelta(days=1)
        current_time = now.strftime("%d%b%y").upper()
        tomorrow_time = tomorrow.strftime("%d%b%y").upper()
        # Authenticate the connection using public/auth method:
        auth_msg = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "public/auth",
            "params": {
                "grant_type": "client_credentials",
                "client_id": client_id, # Here you can put your own portfolio info.
                "client_secret": client_secret
            }
        }
        await websocket.send(json.dumps(auth_msg))
        await websocket.recv() # auth_response = await websocket.recv()
        # Get the options' info and save the relevant results by organizing them in two lists:
        for currency in ["BTC", "ETH", "SOL", "USDC"]:
          request_msg = {
            "jsonrpc" : "2.0",
            "id" : 9367,
            "method" : "private/get_user_trades_by_currency",
            "params" : {
              "currency" : currency,
              "count" : 20
            }
          }
          await websocket.send(json.dumps(request_msg))
          request_response = await websocket.recv()
          for trade in json.loads(request_response)["result"]["trades"]:
            name = trade["instrument_name"]
            expiry = name.split("-")[1]
            if expiry == current_time: # Here I store the instrument names between the two lists corresponding to the two possible messages of the Bot.
              instrument_expiring_today.append(name)
            elif expiry == tomorrow_time:
              instrument_expiring_tomorrow.append(name)
        await websocket.close()
    now = datetime.now(dt.timezone.utc)
    if instrument_expiring_today: # Here, I send the messages.
        if now.hour < 8:
          await update.message.reply_text("The following option contract(s) are expiring today at 8:")
          for option in instrument_expiring_today:
              await update.message.reply_text(option)
    if instrument_expiring_tomorrow:
        if now.hour > 16:
            await update.message.reply_text("The following option contract(s) are expiring tomorrow morning at 8:")
            for option in instrument_expiring_tomorrow:
                await update.message.reply_text(text=option)