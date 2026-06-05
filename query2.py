import sqlite3

conn = sqlite3.connect("library.db")
cursor = conn.cursor()

cursor.execute("""
SELECT b.title,s.name, b.date_read FROM books b
            JOIN book_shelves bs ON b.id = bs.book_id
            JOIN shelves s ON s.id = bs.shelf_id
            WHERE s.name = "Chcę przeczytać" and b.date_read > '0'
""")

rows = cursor.fetchall()

for r in rows:
    print(r)

    