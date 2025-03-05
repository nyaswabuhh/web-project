import psycopg2

# conn = psycopg2.connect(host = "134.209.24.19", user = "alex" , database ="alex", password ="12345" )

conn = psycopg2.connect(host = "localhost", port = "5432", user = "postgres" , database ="myduka", password ="simbapos@2019" )

cur = conn.cursor()

print("database connected successfully")