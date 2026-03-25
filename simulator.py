from gpx_parser import lire_gpx, lisser_altitudes, construire_segments, stats_parcours
from physics import calculer_vitesse, composante_vent_face

def simuler(chemin_gpx, parametres):
    """
    Simule le temps d'un parcours vélo.
    
    parametres = {
        "puissance_w"   : puissance moyenne en watts,
        "poids_kg"      : poids total cycliste + vélo,
        "cda"           : coefficient aérodynamique,
        "v_vent_kmh"    : vitesse du vent en km/h,
        "dir_vent_deg"  : direction du vent en degrés (0=Nord, 90=Est),
        "temperature_c" : température en °C (optionnel)
    }
    """
    # --- 1. Chargement et préparation du parcours ---
    points   = lire_gpx(chemin_gpx)
    altitudes = lisser_altitudes(points, fenetre=5)
    segments  = construire_segments(points, altitudes)

    # --- 2. Simulation segment par segment ---
    temps_total  = 0
    resultats    = []

    for seg in segments:
        pente = seg["pente_pct"]

        # Stratégie de puissance selon la pente
        if pente > 3:
            watts = parametres["puissance_w"] * 1.15  # Effort en montée
        elif pente < -5:
            watts = 0                                  # Roue libre en descente
        else:
            watts = parametres["puissance_w"]          # Plat

        # Calcul de la composante vent de face
        vent_face = composante_vent_face(
            parametres["dir_vent_deg"],
            seg["cap_deg"],
            parametres["v_vent_kmh"] / 3.6
        )

        # Calcul de la vitesse sur ce segment
        v_ms = calculer_vitesse(
            watts       = watts,
            pente_pct   = pente,
            poids_kg    = parametres["poids_kg"],
            cda         = parametres["cda"],
            vent_face_ms= vent_face
        )

        # Temps pour franchir ce segment
        temps_seg     = seg["distance_m"] / v_ms
        temps_total  += temps_seg

        resultats.append({
            **seg,
            "watts"      : watts,
            "vitesse_kmh": round(v_ms * 3.6, 1),
            "temps_seg_s": round(temps_seg, 2),
        })

    # --- 3. Calcul des statistiques finales ---
    dist_totale_m = sum(s["distance_m"] for s in resultats)
    stats         = stats_parcours(segments)

    return {
        "temps_total_s"      : round(temps_total),
        "temps_formate"      : formater_temps(temps_total),
        "distance_km"        : round(dist_totale_m / 1000, 2),
        "vitesse_moyenne_kmh": round((dist_totale_m / temps_total) * 3.6, 1),
        "denivele_pos_m"     : stats["denivele_pos"],
        "segments"           : resultats,
    }

def formater_temps(secondes):
    h = int(secondes // 3600)
    m = int((secondes % 3600) // 60)
    s = int(secondes % 60)
    return f"{h}h {m:02d}min {s:02d}s"