import telebot
from telebot.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup


###################
# Keyboard - menu#
###################

guide_button = KeyboardButton('/Guide')
historical_prices_button = KeyboardButton('/Historical_prices')
sma_button = KeyboardButton('/SMA')
start_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(guide_button)\
    .add(historical_prices_button).add(sma_button)
