import psycopg2

conn = psycopg2.connect(host = "134.209.24.19", user = "nyaswabu" , database ="nyaswabu", password ="12345" )

cur = conn.cursor()

print("database connected successfully")