# https://www.psycopg.org/docs/usage.html
import psycopg2

# Connect to existing database
conn = psycopg2.connect(
    database="exampledb",
    user="docker",
    password="docker",
    host="0.0.0.0",
    port="5433" 
)

# Open cursor to perform database operation
cur = conn.cursor()

# Insert data
cur.execute("INSERT INTO semantic_tags (name) VALUES (%s);", ("moving",))

# Query the database 
cur.execute("SELECT * FROM semantic_tags;")
rows = cur.fetchall()
for row in rows:
    print(row)

# Close communications with database
cur.close()
conn.close()