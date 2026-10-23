"""
database.py - Memoria a largo plazo para BEST-IA
"""
import sqlite3
import os
from datetime import datetime

# Creamos la carpeta data si no existe

DB_PATH = "bestia.db"  # Guardar directo en la raíz

def init_db():
    """Crea la tabla de historial si no existe"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historial (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_message(role: str, content: str):
    """Guarda un mensaje en la base de datos"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO historial (role, content, timestamp) VALUES (?, ?, ?)",
        (role, content, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def get_all_messages() -> list:
    """Recupera todo el historial guardado"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT role, content, timestamp FROM historial ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    
    mensajes = []
    for row in rows:
        mensajes.append({
            "role": row[0],
            "content": row[1],
            "timestamp": datetime.fromisoformat(row[2]).timestamp()
        })
    return mensajes

def clear_history():
    """Borra todo el historial (para el botón de limpiar)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM historial")
    conn.commit()
    conn.close()