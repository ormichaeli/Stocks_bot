import requests
import json
import pandas as pd
import pytz
import datetime
import mplfinance as mpf

def sma_200_50(stocks_ticker, date, api_key, est, utc):
    if len(stocks_ticker) > 0:
        yesterday_date = date - datetime.timedelta(days=1)
        before_85_days = date - datetime.timedelta(days=85)
        before_300_days = date - datetime.timedelta(days=300)

        url_to_polygon_300 = f'https://api.polygon.io/v2/aggs/ticker/{stocks_ticker}/range/1/day/{str(before_300_days)}/{str(yesterday_date)}?adjusted=true&sort=asc&apiKey={api_key}'
        resp_300 = requests.get(url_to_polygon_300)

        url_to_polygon_85 = f'https://api.polygon.io/v2/aggs/ticker/{stocks_ticker}/range/1/day/{str(before_85_days)}/{str(yesterday_date)}?adjusted=true&sort=asc&apiKey={api_key}'
        resp_85 = requests.get(url_to_polygon_85)
        if resp_300.ok and resp_85.ok:
            #####################
            # getting the sma200#
            #####################
            # wrong symbol was entered. #
            if json.loads(resp_300.text)['resultsCount'] == 0:
                return 'Please check the guide again or the sticker symbol.'

            results_300 = json.loads(resp_300.text)['results']

            df_300 = pd.DataFrame(results_300)
            df_300.drop(['v', 'vw', 'o', 'h', 'l', 'n'], axis=1, inplace=True)
            df_300.index = [datetime.datetime.utcfromtimestamp(ts / 1000.).replace(tzinfo=utc).astimezone(est) for ts in
                        df_300['t']]
            df_300.index.name = 'Date'
            df_200 = df_300.tail(200)
            sma_200 = df_200['c'].sum()/200

            ####################
            # getting the sma50#
            ####################


            if json.loads(resp_85.text)['resultsCount'] == 0:
                return 'Please check the guide again or the sticker symbol.'
            results_85 = json.loads(resp_85.text)['results']

            df_85 = pd.DataFrame(results_85)
            df_85.drop(['v', 'vw', 'o', 'h', 'l', 'n'], axis=1, inplace=True)
            df_85.index = [datetime.datetime.utcfromtimestamp(ts / 1000.).replace(tzinfo=utc).astimezone(est) for ts in df_85['t']]
            df_85.index.name = 'Date'
            df_50 = df_85.tail(50)
            sma_50 = df_50['c'].sum()/50

            return round(sma_200, 2), round(sma_50, 2)
        else:
            return 'sorry... we have limit of requests. Try again in a minute :)'
    else:
        # the user pressed the command but didn't enter params.
        return 'No sticker symbol was entered.'
