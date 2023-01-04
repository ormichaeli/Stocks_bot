import requests
import json
import pandas as pd
import pytz
import datetime
import mplfinance as mpf
import psycopg2
from config import postgres_password
from utils import start_string, guide_string
from sqlalchemy import create_engine, types

#############################################
# establishing the connection to PostgresSQL#
#############################################

conn = psycopg2.connect(
    database="stocks_db", user='postgres', password=postgres_password, host='localhost', port='5433')
conn.autocommit = True

# Creating a cursor object using the cursor() method
cursor = conn.cursor()

#############################################
# sqlalchemy engine
##############################################
engine = create_engine(f'postgresql://postgres:{postgres_password}@localhost:5433/stocks_db')
##############################################


def historical_prices(est, utc, api_key, message, stocks_ticker, _from, to, multiplier, timespan, graph):
    message_id = message.id
    # checking if data already exists #
    sql_exists_query = f"SELECT message_id, stocks_ticker, from_date, to_date, multiplier, timespan\
                        FROM request_params\
                        WHERE stocks_ticker = '{stocks_ticker}' AND from_date = '{_from}' AND to_date = '{to}' AND multiplier = '{multiplier}'\
                        AND timespan = '{timespan}'"

    cursor.execute(sql_exists_query)
    prev_request_params = cursor.fetchall()
    # if records were found
    if (len(prev_request_params) > 0):
        prev_message_id = prev_request_params[0][0]
        sql_relevant_records = f'SELECT date, open, close, high, low\
                                FROM hist_prices_results\
                                WHERE message_id = {prev_message_id}'

        cursor.execute(sql_relevant_records)
        prev_request_results = cursor.fetchall()
        df = pd.DataFrame(prev_request_results, columns=['date', 'open', 'close', 'high', 'low'])
        df.index = df['date']

        df.index.name = 'date'

    # if there are no records - sent Http request to the api
    else:
            url_to_polygon = f'https://api.polygon.io/v2/aggs/ticker/{stocks_ticker}/range/{multiplier}/{timespan}/{_from}/{to}?adjusted=true&sort=asc&apiKey={api_key}'
            resp = requests.get(url_to_polygon)
            if resp.ok:
                result = json.loads(resp.text)
                # the response status is ok, but there are no results-> it means that the Stock Exchange was closed. #
                if result['resultsCount'] == 0:
                    if(stocks_ticker.islower()):
                        return 'Only uppercase required'
                    else:
                        return 'No data for days off or holidays'
                else:
                    results = json.loads(resp.text)['results']
                    df = pd.DataFrame(results)
                    df.index = [datetime.datetime.utcfromtimestamp(ts / 1000.).replace(tzinfo=utc).astimezone(est) for
                                ts in df['t']]
                    df.index.name = 'date'
                    df.drop(['v', 'vw', 'n', 't'], axis=1, inplace=True)
                    df.columns = ['open', 'close', 'high', 'low']
                    df.insert(loc=4, column='message_id', value=[message_id for i in range(len(df))])
                    insert_params_query = f" INSERT INTO request_params(message_id, stocks_ticker, from_date, to_date, multiplier, timespan)\
                                            VALUES('{message_id}', '{stocks_ticker}', '{_from}', '{to}', '{multiplier}', '{timespan}')"
                    cursor.execute(insert_params_query)

                    print(df)
                    df.to_sql(name='hist_prices_results', con=engine, if_exists='append', index=True,
                              dtype={'date': types.DATETIME, 'open': types.Integer, 'close': types.Integer,
                                     'high': types.Integer, 'low': types.Integer, 'message_id': types.Integer})

            else:
                return 'sorry... the number of requests is limited. Try again in a minute :)'

    fig_file_name = f'periodic_historical_fig/fig{message_id}.jpg'
    if graph == 'candle':
        mpf.plot(df, type='candle', show_nontrading=True, savefig=fig_file_name)
    if graph == 'line':
        mpf.plot(df, type='line', show_nontrading=True, savefig=fig_file_name)
