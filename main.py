from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import pandas as pd

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ====== ARCHIVOS ======
ARCHIVOS = [
    {
        "file": "bitacora tarde.xlsx",
        "sheet": "concentrado nocturno.",
        "horas": ["4:00", "5:00", "6:00", "7:00", "8:00", "9:00"],
        "dias": {
            "lunes": (4, 8),
            "martes": (9, 13),
            "miercoles": (14, 18),
            "jueves": (19, 23),
            "viernes": (24, 28),
        }
    },]
    
   

# ====== UTIL ======
def normalizar(valor):
    if pd.isna(valor):
        return ""
    return str(valor).strip().upper()


def hora_a_minutos(hora: str) -> int:
    h, m = hora.split(":")
    return int(h) * 60 + int(m)



# ====== LOGICA PRINCIPAL ======
def buscar_profesor(matricula: str, dia: str):
    matricula = normalizar(matricula)
    dia = dia.lower()
    resultados = []

    for info in ARCHIVOS:
        if dia not in info["dias"]:
            continue

        col_inicio, col_fin = info["dias"][dia]
        horas = info["horas"]

        try:
            df = pd.read_excel(info["file"], sheet_name=info["sheet"], header=None)
        except Exception as e:
            print(f"Error leyendo {info['file']} - {e}")
            continue

        for fila in range(4, 68):
            aula = normalizar(df.iloc[fila, 0])
            grupo = normalizar(df.iloc[fila, 1])
            licenciatura = normalizar(df.iloc[fila, 2])

            for i, col in enumerate(range(col_inicio, col_fin + 1)):
                celda = normalizar(df.iloc[fila, col])

                if celda == matricula and i < len(horas):
                    resultados.append({
                        "hora": horas[i],
                        "aula": aula,
                        "grupo": grupo,
                        "licenciatura": licenciatura
                    })

    # ordenar por hora (string funciona bien aquí)
    resultados.sort(key=lambda x: hora_a_minutos(x["hora"]))


    return resultados


# ====== RUTAS ======
@app.get("/", response_class=HTMLResponse)
def inicio(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "resultados": None}
    )


@app.post("/buscar", response_class=HTMLResponse)
def buscar(request: Request, matricula: str = Form(...), dia: str = Form(...)):
    clases = buscar_profesor(matricula, dia)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "matricula": matricula.upper(),
            "dia": dia.capitalize(),
            "resultados": clases
        }
    )
