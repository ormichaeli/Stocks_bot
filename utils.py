import requests
import json
import pandas as pd
import pytz
import datetime
import mplfinance as mpf


start_string = '''Welcome to Stock's bot! \nWhat would you like to do?.'''

guide_string = '''***For getting aggregate bars for a stock over a given date range in custom time window sizes --> choose Historical prices.\n
***For getting the SMA 200 and 50 for a specific stock --> choose SMA. \nHope you will enjoy the bot :)'''

