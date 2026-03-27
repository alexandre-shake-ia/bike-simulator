from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv
import tempfile, os

from simulator import simuler

load_dotenv()

ALLOWED_ORIGIN = os.getenv("ALLOWED_ORIGIN", "http://localhost:3000")
MAX_FILE_SIZE  = 5 * 1024 * 1024  # 5 MB

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="ALLURE — Simulateur Cycliste", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health():
    return {"status": "ok", "app": "ALLURE"}


@app.post("/simulate")
@limiter.limit("10/minute")
async def simulate(
    request: Request,                          # obligatoire pour slowapi
    fichier: UploadFile         = File(...),
    puissance_w: int            = Form(...),
    poids_kg: float             = Form(...),
    cda: float                  = Form(...),
    v_vent_kmh: float           = Form(...),
    dir_vent_deg: int           = Form(...),
    peloton: bool               = Form(False),
    duree_peloton_h: float      = Form(0.0),
):
    # 1. Lecture du fichier
    contents = await fichier.read()

    # 2. Limite de taille — 5 MB max
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Fichier trop volumineux. Maximum 5 MB."
        )

    # 3. Validation basique du contenu GPX
    if not (contents.startswith(b'<?xml') or contents.startswith(b'<gpx')):
        raise HTTPException(
            status_code=400,
            detail="Fichier invalide. Seuls les fichiers GPX sont acceptés."
        )

    # 4. Sauvegarde temporaire et simulation
    suffix = os.path.splitext(fichier.filename)[1] or ".gpx"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(contents)
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