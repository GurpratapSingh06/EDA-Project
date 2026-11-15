import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

conn = psycopg2.connect(host='localhost', port=5432, user='postgres', password='root', dbname='postgres')
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cur = conn.cursor()
cur.execute("SELECT 1 FROM pg_database WHERE datname='chicago_crime_dw'")
if not cur.fetchone():
    cur.execute("CREATE DATABASE chicago_crime_dw")
    print("Created database chicago_crime_dw successfully!")
else:
    print("Database chicago_crime_dw already exists.")
cur.close()
conn.close()
