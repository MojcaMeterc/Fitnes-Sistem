import sys
sys.path.insert(0, r'C:\Users\uporabnik\OneDrive - Univerza v Ljubljani\Desktop\PB1\Fitnes-Sistem')

import sqlite3
from model import Admin

conn = sqlite3.connect(r'C:\Users\uporabnik\OneDrive - Univerza v Ljubljani\Desktop\PB1\Fitnes-Sistem\fitnes.db')
conn.row_factory = sqlite3.Row

admin = Admin.pridobi_po_id(conn, 2)
print(type(admin))
print(type(admin.conn))
print(admin.ime)

trenerji = admin.vsi_trenerji()
print(trenerji)