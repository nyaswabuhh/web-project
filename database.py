import psycopg2

conn = psycopg2.connect(host = "localhost" , port= "5432" , user = "postgres" , database ="myduka", password ="simbapos@2019" )

cur = conn.cursor()

print("database connected successfully")