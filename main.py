from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import tempfile, os

from simulator import simuler

load_dotenv()  # Lit le fichier .env

ALLOWED_ORIGIN = os.getenv("ALLOWED_ORIGIN", "http://localhost:3000")

app = FastAPI(title="ALLURE — Simulateur Cycliste", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],  # ← sécurisé, plus de wildcard *
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health():
    return {"status": "ok", "app": "ALLURE"}

@app.post("/simulate")
async def simulate(
    fichier: UploadFile         = File(...),
    puissance_w: int            = Form(...),
    poids_kg: float             = Form(...),
    cda: float                  = Form(...),
    v_vent_kmh: float           = Form(...),
    dir_vent_deg: int           = Form(...),
    peloton: bool               = Form(False),
    duree_peloton_h: float      = Form(0.0),
):
    suffix = os.path.splitext(fichier.filename)[1] or ".gpx"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await fichier.read())
        chemin_temp = tmp.name

    try:
        parametres = {
            "puissance_w":     puissance_w,
            "poids_kg":        poids_kg,
            "cda":             cda,
            "v_vent_kmh":      v_vent_kmh,
            "dir_vent_deg":    dir_vent_deg,
            "temperature_c":   20,
            "peloton":         peloton,
            "duree_peloton_h": duree_peloton_h,
        }
        resultat = simuler(chemin_temp, parametres)
    finally:
        os.unlink(chemin_temp)

    return resultat