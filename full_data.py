from config import *
import requests
import json
import pandas as pd
import pytz
import datetime

today_date = datetime.datetime.now().date()
two_years_ago_date = today_date - datetime.timedelta(days=730)


def full_data(est, utc, stocks_ticker, api_key):
    url_to_polygon = f'https://api.polygon.io/v2/aggs/ticker/{stocks_ticker}/range/1/day/{two_years_ago_date}/{today_date}?adjusted=true&sort=asc&apiKey={api_key}'
    resp = requests.get(url_to_polygon)
    results = json.loads(resp.text)['results']
    df = pd.DataFrame(results)
    df.drop(['v', 'vw', 'n'], axis=1, inplace=True)

    df.index = [datetime.datetime.utcfromtimestamp(ts / 1000.).replace(tzinfo=utc).astimezone(est) for ts in
                df['t']]
    df.index.name = 'Date'
    df.columns = ['Open', 'Close', 'High', 'Low', 'Time']
    return df

