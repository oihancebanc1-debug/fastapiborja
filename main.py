"""API de Tareas con FastAPI."""
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="API de Tareas 📝",
    description="API sencilla para probar entre compañeros. Entra en /docs y toquetea 😉",
    version="1.0.0",
)

# Permitir llamadas desde cualquier origen (navegador, otros notebooks, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Modelos ----------
class TareaIn(BaseModel):
    titulo: str = Field(..., min_length=1, examples=["Aprender FastAPI"])
    descripcion: Optional[str] = Field(None, examples=["Hacer el CRUD completo"])
    completada: bool = False
    autor: Optional[str] = Field(None, examples=["Óscar"])

class Tarea(TareaIn):
    id: int
    creada: datetime

# ---------- "Base de datos" en memoria ----------
db: dict[int, Tarea] = {}
siguiente_id = 1

# ---------- Endpoints ----------
INTERFAZ = Path(__file__).parent / "static" / "index.html"

@app.get("/", include_in_schema=False)
def interfaz():
    """Interfaz web para usar la API desde el navegador."""
    return FileResponse(INTERFAZ)

@app.get("/estado", tags=["General"])
def estado():
    return {"mensaje": "¡La API funciona! Interfaz en / y documentación en /docs", "tareas": len(db)}

@app.get("/saludo/{nombre}", tags=["General"])
def saludar(nombre: str):
    return {"mensaje": f"¡Hola, {nombre}! 👋"}

@app.get("/tareas", response_model=list[Tarea], tags=["Tareas"])
def listar_tareas(completada: Optional[bool] = None):
    tareas = list(db.values())
    if completada is not None:
        tareas = [t for t in tareas if t.completada == completada]
    return tareas

@app.get("/tareas/{tarea_id}", response_model=Tarea, tags=["Tareas"])
def obtener_tarea(tarea_id: int):
    if tarea_id not in db:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return db[tarea_id]

@app.post("/tareas", response_model=Tarea, status_code=201, tags=["Tareas"])
def crear_tarea(tarea: TareaIn):
    global siguiente_id
    nueva = Tarea(id=siguiente_id, creada=datetime.now(), **tarea.model_dump())
    db[siguiente_id] = nueva
    siguiente_id += 1
    return nueva

@app.put("/tareas/{tarea_id}", response_model=Tarea, tags=["Tareas"])
def actualizar_tarea(tarea_id: int, tarea: TareaIn):
    if tarea_id not in db:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    actualizada = Tarea(id=tarea_id, creada=db[tarea_id].creada, **tarea.model_dump())
    db[tarea_id] = actualizada
    return actualizada

@app.delete("/tareas/{tarea_id}", tags=["Tareas"])
def borrar_tarea(tarea_id: int):
    if tarea_id not in db:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    del db[tarea_id]
    return {"mensaje": f"Tarea {tarea_id} borrada"}
