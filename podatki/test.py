import sqlite3
conn = sqlite3.connect("fitnes.db")
conn.row_factory = sqlite3.Row

cur = conn.execute("SELECT * FROM uporabniki WHERE uporabnik_id = ?", (1,))
row = cur.fetchone()
print(dict(row))