import sqlite3

conn = sqlite3.connect("library.db")
cursor = conn.cursor()

cursor.execute("""
SELECT * FROM books b
            JOIN book_shelves bs ON b.id = bs.book_id
            JOIN shelves s ON s.id = bs.shelf_id
           
""")

rows = cursor.fetchall()

for r in rows:
    print(r)

    