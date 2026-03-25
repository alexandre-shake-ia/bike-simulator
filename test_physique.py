from physics import calculer_vitesse, composante_vent_face
from gpx_parser import lire_gpx, lisser_altitudes, construire_segments, stats_parcours

# ============================================================
# COULEURS pour le terminal
# ============================================================
VERT  = "\033[92m"
ROUGE = "\033[91m"
BLEU  = "\033[94m"
RESET = "\033[0m"

def ok(msg):   print(f"{VERT}✅ {msg}{RESET}")
def err(msg):  print(f"{ROUGE}❌ {msg}{RESET}")
def info(msg): print(f"{BLEU}ℹ️  {msg}{RESET}")

resultats = {"ok": 0, "fail": 0}

def verifier(nom, valeur, mini, maxi):
    if mini <= valeur <= maxi:
        ok(f"{nom} : {valeur:.1f}  (attendu entre {mini} et {maxi})")
        resultats["ok"] += 1
    else:
        err(f"{nom} : {valeur:.1f}  ← HORS LIMITES (attendu entre {mini} et {maxi})")
        resultats["fail"] += 1

# ============================================================
# TEST 1 — Plat, sans vent
# ============================================================
print("\n" + "="*55)
print("TEST 1 — Plat, sans vent, 200W, 85kg, CdA=0.32")
print("="*55)
v = calculer_vitesse(watts=200, pente_pct=0, poids_kg=85, cda=0.32, vent_face_ms=0)
verifier("Vitesse (km/h)", v * 3.6, 28, 36)

# ============================================================
# TEST 2 — Montée 5%
# ============================================================
print("\n" + "="*55)
print("TEST 2 — Montée 5%, 200W, 85kg, CdA=0.32")
print("="*55)
v = calculer_vitesse(watts=200, pente_pct=5, poids_kg=85, cda=0.32, vent_face_ms=0)
verifier("Vitesse (km/h)", v * 3.6, 10, 16)

# ============================================================
# TEST 3 — Descente roue libre
# ============================================================
print("\n" + "="*55)
print("TEST 3 — Descente -8%, roue libre (0W)")
print("="*55)
v = calculer_vitesse(watts=0, pente_pct=-8, poids_kg=85, cda=0.32, vent_face_ms=0)
verifier("Vitesse (km/h)", v * 3.6, 35, 65)

# ============================================================
# TEST 4 — Vent de face vs vent de dos
# ============================================================
print("\n" + "="*55)
print("TEST 4 — Vent 10 km/h, plat, 200W")
print("="*55)
vent_ms = 10 / 3.6
v_face = calculer_vitesse(200, 0, 85, 0.32, +vent_ms)
v_dos  = calculer_vitesse(200, 0, 85, 0.32, -vent_ms)
info(f"Vent de face : {v_face*3.6:.1f} km/h")
info(f"Vent de dos  : {v_dos*3.6:.1f} km/h")
verifier("Écart face/dos (km/h)", v_dos*3.6 - v_face*3.6, 2, 15)

# ============================================================
# TEST 5 — Plus de puissance = plus vite
# ============================================================
print("\n" + "="*55)
print("TEST 5 — 150W vs 250W sur le plat")
print("="*55)
v_150 = calculer_vitesse(150, 0, 85, 0.32, 0)
v_250 = calculer_vitesse(250, 0, 85, 0.32, 0)
info(f"À 150W : {v_150*3.6:.1f} km/h")
info(f"À 250W : {v_250*3.6:.1f} km/h")
verifier("v(250W) > v(150W) de X km/h", v_250*3.6 - v_150*3.6, 3, 15)

# ============================================================
# TEST 6 — Ton fichier GPX réel
# ============================================================
print("\n" + "="*55)
print("TEST 6 — Lecture du fichier GPX réel")
print("="*55)

GPX_PATH = "data/IM_AGADIR.gpx"

try:
    points = lire_gpx(GPX_PATH)
    info(f"Nombre de points bruts : {len(points)}")

    alt_brutes  = [p.elevation for p in points[:10]]
    alt_lissees = lisser_altitudes(points, fenetre=5)[:10]

    print("\n  Comparaison altitudes (10 premiers points) :")
    print(f"  {'Brut':>8}  {'Lissé':>8}  {'Écart':>8}")
    for b, l in zip(alt_brutes, alt_lissees):
        if b is not None:
            print(f"  {b:>8.1f}  {l:>8.1f}  {abs(b-l):>8.2f}m")

    segs  = construire_segments(points, lisser_altitudes(points))
    stats = stats_parcours(segs)

    print("\n  Résumé du parcours :")
    for k, v in stats.items():
        print(f"  {k:<25} : {v}")

    ok("Fichier GPX lu avec succès")
    resultats["ok"] += 1

except FileNotFoundError:
    err(f"Fichier GPX non trouvé : {GPX_PATH}")
    err("→ Vérifie que ton fichier est bien dans le dossier data/")
    resultats["fail"] += 1

except Exception as e:
    err(f"Erreur inattendue : {e}")
    resultats["fail"] += 1

# ============================================================
# RÉSUMÉ FINAL
# ============================================================
print("\n" + "="*55)
total = resultats["ok"] + resultats["fail"]
print(f"RÉSULTAT : {resultats['ok']}/{total} tests réussis")
if resultats["fail"] == 0:
    ok("Tout est bon — le moteur physique est fiable !")
else:
    err(f"{resultats['fail']} test(s) à corriger")
print("="*55 + "\n")