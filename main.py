from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from typing import Union
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from datetime import date
import pyodbc
import os

app=FastAPI()


app.mount("/static", StaticFiles(directory="static", html=True), name="static")



@app.get("/home.html")
def serve_home_direct():
    return FileResponse("static/home.html")


@app.get("/listar.html")
def serve_listar():
    return FileResponse("static/listar.html")

@app.get("/registrar.html")
def serve_registrar():
    return FileResponse("static/registrar.html")

@app.get("/actualizar.html")
def serve_actualizar():
    return FileResponse("static/actualizar.html")

@app.get("/eliminar.html")
def serve_eliminar():
    return FileResponse("static/eliminar.html")
def get_connection():
    return pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=MARMOTA\\SQLEXPRESS;'
        'DATABASE=GESTION;'
        'Trusted_Connection=yes;')

@app.get("/QX.html")
def serve_agendar_qx():
    return FileResponse("static/QX.html")


class Cirugias(BaseModel):
    id: int
    nombre: str
    indicaciones: str = None

class Paciente(BaseModel):
    id: int = None
    rut: str
    nombre: str
    celular: str = None
    correo: str = None
    fecha_registro: date

class PacienteInserta(BaseModel):
    rut: str
    nombre: str
    celular: str = None
    correo: str = None

class Agendamiento(BaseModel):
    pac_id_paciente: int
    ciru_id_cirugia: int
    agenda_fecha: date
    agenda_hora: str 

@app.get("/cirugias", response_model=List[Cirugias])
def obtener_cirugias():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("EXEC ListarCirugias")
    cirugias = []
    for row in cursor.fetchall():
        cirugias.append(Cirugias(id=row[0], nombre=row[1], indicaciones=row[2]))
    conn.close()
    return cirugias



@app.get("/pacientes", response_model=List[Paciente])
def listar_pacientes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("EXEC ListarRegistros")
    pacientes = []
    for row in cursor.fetchall():
        pacientes.append(Paciente(
            id=row[0],
            rut=row[1],
            nombre=row[2],
            celular=row[3],
            correo=row[4],
            fecha_registro=row[5]
        ))
    conn.close()
    return pacientes

@app.post("/pacientes")
def insertar_paciente(paciente: PacienteInserta):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("EXEC InsertarRegistro ?, ?, ?, ?", 
                   paciente.rut, paciente.nombre, paciente.celular, paciente.correo)
    conn.commit()
    conn.close()
    return {"mensaje": "Paciente insertado correctamente"}

@app.put("/pacientes/{id}")
def actualizar_paciente(id: int, paciente: PacienteInserta):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("EXEC ActualizarRegistro ?, ?, ?, ?, ?", 
                   id, paciente.rut, paciente.nombre, paciente.celular, paciente.correo)
    conn.commit()
    conn.close()
    return {"mensaje": "Paciente actualizado correctamente"}

@app.delete("/pacientes/{id}")
def eliminar_paciente(id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("EXEC EliminarRegistro ?", id)
    conn.commit()
    conn.close()
    return {"mensaje": "Paciente eliminado correctamente"}


@app.get("/pacientes/buscar/{rut}", response_model=Union[Paciente, dict])
def buscar_paciente_por_rut(rut: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("EXEC BuscarPorRUT ?", rut)
    row = cursor.fetchone()
    conn.close()

    if row:
        return Paciente(
            id=row[0],
            rut=row[1],
            nombre=row[2],
            celular=row[3],
            correo=row[4],
            fecha_registro=row[5]
        )
    else:
        return {"mensaje": "Paciente no encontrado"}


@app.post("/agenda")
def crear_agendamiento(agendamiento: Agendamiento):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        EXEC InsertarAgendaCirugia ?, ?, ?, ?
    """, 
    agendamiento.pac_id_paciente, 
    agendamiento.ciru_id_cirugia, 
    agendamiento.agenda_fecha, 
    agendamiento.agenda_hora)
    
    conn.commit()
    conn.close()
    return {"mensaje": "Agendamiento guardado correctamente"}
