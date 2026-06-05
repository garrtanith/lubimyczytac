import sqlite3

conn = sqlite3.connect("library.db")
cursor = conn.cursor()

cursor.execute("""
SELECT * FROM books_staging b
           
         
""")

rows = cursor.fetchall()

for r in rows:
    print(r)

    