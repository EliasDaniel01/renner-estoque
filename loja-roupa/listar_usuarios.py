import sqlite3
import os

def listar_usuarios():
    db_path = os.path.join(os.path.dirname(__file__), 'usuarios.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    rows = cursor.execute("SELECT * FROM usuarios").fetchall()
    print(rows)
    conn.close()

listar_usuarios()