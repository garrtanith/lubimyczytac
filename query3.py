import sqlite3

conn = sqlite3.connect("library.db")
cursor = conn.cursor()

cursor.execute("""
SELECT b.id, b.title, b.my_rating, b.shelves FROM books_staging b
           
         
""")

rows = cursor.fetchall()

for r in rows:
    print(r)

    