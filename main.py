from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sqlite3

app = FastAPI(title="API de Control Logístico")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_NAME = "logistica_real.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ordenes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            nota TEXT,
            cantidad TEXT,
            separador TEXT,
            hora_separacion TEXT,
            salida_user TEXT,
            hora_salida TEXT,
            estado TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

class Orden(BaseModel):
    fecha: str
    nota: str
    cantidad: str

class ActualizacionOrden(BaseModel):
    cantidad: Optional[str] = None
    separador: Optional[str] = None
    hora_separacion: Optional[str] = None
    salida_user: Optional[str] = None
    hora_salida: Optional[str] = None
    estado: Optional[str] = None

@app.get("/ordenes")
def obtener_ordenes():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ordenes ORDER BY id DESC")
    filas = cursor.fetchall()
    conn.close()
    return [dict(f) for f in filas]

@app.post("/ordenes/carga-masiva")
def carga_masiva(ordenes: List[Orden]):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    for o in ordenes:
        cursor.execute('''
            INSERT INTO ordenes (fecha, nota, cantidad, separador, hora_separacion, salida_user, hora_salida, estado)
            VALUES (?, ?, ?, '', '', '', '', 'Pendiente')
        ''', (o.fecha, o.nota, o.cantidad))
    conn.commit()
    conn.close()
    return {"status": "success", "message": f"{len(ordenes)} órdenes procesadas."}

@app.put("/ordenes/{orden_id}")
def actualizar_orden(orden_id: int, datos: ActualizacionOrden):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    for campo, valor in datos.dict(exclude_unset=True).items():
        cursor.execute(f"UPDATE ordenes SET {campo} = ? WHERE id = ?", (valor, orden_id))
    conn.commit()
    conn.close()
    return {"status": "updated"}

@app.delete("/ordenes/{orden_id}")
def eliminar_orden(orden_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ordenes WHERE id = ?", (orden_id,))
    conn.commit()
    conn.close()
    return {"status": "deleted"}
