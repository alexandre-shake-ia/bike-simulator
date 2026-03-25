import math
from scipy.optimize import brentq

# --- Constantes physiques ---
G = 9.81          # Gravité (m/s²)
RHO = 1.225       # Densité de l'air (kg/m³)
RENDEMENT = 0.97  # Rendement mécanique du vélo
CRR = 0.005       # Résistance au roulement

def puissance_requise(v, pente_pct, poids_kg, cda, vent_face_ms):
    angle = math.atan(pente_pct / 100)
    f_roulement = CRR * poids_kg * G * math.cos(angle)
    f_gravite   = poids_kg * G * math.sin(angle)
    v_air = v + vent_face_ms
    f_aero = 0.5 * RHO * cda * (v_air ** 2) * (1 if v_air >= 0 else -1)
    return (f_roulement + f_gravite + f_aero) * v / RENDEMENT

def calculer_vitesse(watts, pente_pct, poids_kg, cda, vent_face_ms):
    VITESSE_MIN = 0.5
    VITESSE_MAX = 22.2

    if watts == 0:
        def eq_roue_libre(v):
            return puissance_requise(v, pente_pct, poids_kg, cda, vent_face_ms)
        try:
            v = brentq(eq_roue_libre, VITESSE_MIN, VITESSE_MAX, xtol=0.01)
        except ValueError:
            v = 5.0
        return v

    def equation(v):
        return puissance_requise(v, pente_pct, poids_kg, cda, vent_face_ms) - watts

    try:
        f_min = equation(VITESSE_MIN)
        f_max = equation(VITESSE_MAX)
        if f_min * f_max > 0:
            return VITESSE_MIN
        v = brentq(equation, VITESSE_MIN, VITESSE_MAX, xtol=0.01)
    except Exception as e:
        print(f"[WARN] Erreur calcul vitesse: {e} | pente={pente_pct}% watts={watts}")
        v = VITESSE_MIN

    return min(max(v, VITESSE_MIN), VITESSE_MAX)

def composante_vent_face(direction_vent_deg, cap_cycliste_deg, vitesse_vent_ms):
    angle = (direction_vent_deg - cap_cycliste_deg + 360) % 360
    return vitesse_vent_ms * math.cos(math.radians(angle))