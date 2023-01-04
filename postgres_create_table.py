import psycopg2
from config import postgres_password

# establishing the connection
conn = psycopg2.connect(
   database="stocks_db", user='postgres', password=postgres_password, host='localhost', port='5433')
conn.autocommit = True

# Creating a cursor object using the cursor() method
cursor = conn.cursor()

sql_create_table1 = '''CREATE TABLE request_params(
   message_id integer,
   stocks_ticker VARCHAR(10),
   from_date VARCHAR(15),
   to_date VARCHAR(15),
   multiplier VARCHAR(10),
   timespan VARCHAR(15));'''

sql_create_table2 = '''CREATE TABLE hist_prices_results(
   date timestamp,
   open integer,
   close integer,
   high integer,
   low integer,
   message_id integer);'''

cursor.execute(sql_create_table1)
cursor.execute(sql_create_table2)

# Closing the connection
conn.close()
