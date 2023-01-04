from config import *
import telebot
from telebot.types import KeyboardButton, ReplyKeyboardMarkup, CallbackQuery
from keyboard import start_keyboard
import requests
import json
import pandas as pd
import pytz
import datetime
import mplfinance as mpf
from utils import start_string, guide_string
from historical_prices import historical_prices
from sma import sma_200_50
from telebot import asyncio_filters
import asyncio
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_storage import StateMemoryStorage
from telebot.asyncio_handler_backends import State, StatesGroup


bot = AsyncTeleBot(bot_token, state_storage=StateMemoryStorage())
# bot.set_webhook()

est = pytz.timezone('America/New_York')
utc = pytz.utc

class params_of_request(StatesGroup):
    stocks_ticker = State()  # statesgroup should contain states
    from_ = State()
    to = State()
    multiplier = State()
    timespan = State()
    graph = State()
    ticker_sma = State()


@bot.message_handler(commands=['start'])
async def start_handler(message):
    chat_id = message.chat.id
    await bot.send_message(chat_id=chat_id, text=start_string, reply_markup=start_keyboard)


@bot.message_handler(commands=['Guide'])
async def guide_handler(message):
    chat_id = message.chat.id
    await bot.send_message(chat_id=chat_id, text=guide_string, reply_markup=start_keyboard)


@bot.message_handler(commands=['Historical_prices'])
async def historical_func_beginning(message):
    chat_id = message.chat.id
    await bot.set_state(message.from_user.id, params_of_request.stocks_ticker, chat_id)
    await bot.send_message(chat_id, 'Please, enter a stock ticker \nOnly uppercase letters are allowed')


@bot.message_handler(state=params_of_request.stocks_ticker)
async def get_stocks_ticker(message):
    chat_id = message.chat.id
    await bot.send_message(chat_id, f'From which date?\n (YYYY-MM-DD)')
    await bot.set_state(message.from_user.id, params_of_request.from_, chat_id)
    async with bot.retrieve_data(message.from_user.id, chat_id) as data:
        data['stocks_ticker'] = message.text


@bot.message_handler(state=params_of_request.from_)
async def get_from_date(message):
    chat_id = message.chat.id
    await bot.send_message(chat_id, f'Till which date?\n (YYYY-MM-DD)')
    await bot.set_state(message.from_user.id, params_of_request.to, chat_id)
    async with bot.retrieve_data(message.from_user.id, chat_id) as data:
        data['from_'] = message.text

@bot.message_handler(state=params_of_request.to)
async def get_to_date(message):
    chat_id = message.chat.id
    await bot.send_message(chat_id, f'Write the size of the timespan multiplier')
    await bot.set_state(message.from_user.id, params_of_request.multiplier, chat_id)
    async with bot.retrieve_data(message.from_user.id, chat_id) as data:
        data['to'] = message.text

@bot.message_handler(state=params_of_request.multiplier)
async def get_multiplier(message):
    chat_id = message.chat.id
    await bot.send_message(chat_id, f'Write a timespan \nOnly lowercase letters are allowed')
    await bot.set_state(message.from_user.id, params_of_request.timespan, chat_id)
    async with bot.retrieve_data(message.from_user.id, chat_id) as data:
        data['multiplier'] = message.text

@bot.message_handler(state=params_of_request.timespan)
async def get_timespan(message):
    chat_id = message.chat.id
    await bot.send_message(chat_id, f'how would you like to get the results?\nWrite your choice - candle/line \nOnly lowercase letters are allowed')
    await bot.set_state(message.from_user.id, params_of_request.graph, chat_id)
    async with bot.retrieve_data(message.from_user.id, chat_id) as data:
        data['timespan'] = message.text


@bot.message_handler(state=params_of_request.graph)
async def ready_params(message):
    chat_id = message.chat.id
    print(message.id)
    async with bot.retrieve_data(message.from_user.id, chat_id) as data:
        data['graph'] = message.text
        returned_from_historical_prices = historical_prices(est, utc, api_key, message, data['stocks_ticker'],
                                                            data['from_'], data['to'], data['multiplier'],
                                                            data['timespan'], data['graph'])

        if type(returned_from_historical_prices) == str:
            await bot.send_message(chat_id=chat_id, text=returned_from_historical_prices)
        else:
            await bot.send_chat_action(message.chat.id, 'upload_photo')
            img = open(f'periodic_historical_fig/fig{message.id}.jpg', 'rb')
            await bot.send_photo(chat_id, img)
            img.close()
            await bot.delete_state(message.from_user.id, message.chat.id)

@bot.message_handler(commands=['SMA'])
async def ready_params(message):
    chat_id = message.chat.id
    await bot.set_state(message.from_user.id, params_of_request.ticker_sma, chat_id)
    await bot.send_message(chat_id, 'Please, enter a stock ticker \nOnly uppercase letters are allowed')

@bot.message_handler(state=params_of_request.ticker_sma)
async def sma_func(message):
    chat_id = message.chat.id
    async with bot.retrieve_data(message.from_user.id, chat_id) as data:
        data['ticker_sma'] = message.text

        today_date = datetime.datetime.now().date()
        returned_from_sma = sma_200_50(data['ticker_sma'], today_date, api_key, est, utc)

        if type(returned_from_sma) == str:
            await bot.send_message(chat_id=chat_id, text=returned_from_sma)
        else:
            sma_200, sma_50 = returned_from_sma
            if sma_200 < sma_50:
                await bot.send_message(chat_id=chat_id, text=f"The simple average for the last 200 days is- {sma_200}.\
                    \nThe simple average for the last 50 days is- {sma_50}.\
                    \nTherefore, {data['ticker_sma']} is trending up!")
            elif sma_200 > sma_50:
                await bot.send_message(chat_id=chat_id, text=f"The simple average for the last 200 days is- {sma_200}.\
                           \nThe simple average for the last 50 days is- {sma_50}.\
                           \nTherefore, {data['ticker_sma']} is trending down!")
            else:
                # crossover
                sma200_2, sma50_2 = tuple(sma_200_50(data['ticker_sma'], today_date - datetime.timedelta(days=1), api_key, est, utc))
                if sma200_2 < sma50_2:
                    await bot.send_message(chat_id=chat_id, text=f"SMA Crossover!\
                    \nNow the trend is changing, and {data['ticker_sma']} is trending down!")
                else:
                    await bot.send_message(chat_id=chat_id, text=f"SMA Crossover!\
                                \nNow the trend is changing, and {data['ticker_sma']} is trending up!")

bot.add_custom_filter(asyncio_filters.StateFilter(bot))
asyncio.run(bot.polling())
