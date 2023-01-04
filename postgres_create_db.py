import psycopg2
from config import postgres_password

# establishing the connection
conn = psycopg2.connect(
   database="postgres", user='postgres', password=postgres_password, host='localhost', port='5433')
conn.autocommit = True

# Creating a cursor object using the cursor() method
cursor = conn.cursor()

# preparing query to create a database
sql_create_db = '''CREATE database stocks_db;'''

# Creating a database
cursor.execute(sql_create_db)

# Closing the connection
conn.close()
