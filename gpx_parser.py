import math
import gpxpy

def lire_gpx(chemin_fichier):
    with open(chemin_fichier, "r", encoding="utf-8") as f:
        gpx = gpxpy.parse(f)
    
    points = []
    for track in gpx.tracks:
        for segment in track.segments:
            points.extend(segment.points)
    
    if len(points) < 2:
        raise ValueError("Le fichier GPX contient moins de 2 points.")
    
    print(f"✅ GPX chargé : {len(points)} points trouvés")
    return points

def lisser_altitudes(points, fenetre=12):
    altitudes = [p.elevation if p.elevation is not None else 0 for p in points]
    lissees = []
    for i in range(len(altitudes)):
        debut = max(0, i - fenetre)
        fin   = min(len(altitudes), i + fenetre + 1)
        lissees.append(sum(altitudes[debut:fin]) / (fin - debut))
    return lissees

def calculer_cap(p1, p2):
    y = math.sin(math.radians(p2.longitude - p1.longitude)) * math.cos(math.radians(p2.latitude))
    x = (math.cos(math.radians(p1.latitude)) * math.sin(math.radians(p2.latitude)) -
         math.sin(math.radians(p1.latitude)) * math.cos(math.radians(p2.latitude)) *
         math.cos(math.radians(p2.longitude - p1.longitude)))
    return (math.degrees(math.atan2(y, x)) + 360) % 360

def construire_segments(points, altitudes_lissees):
    segments = []
    dist_cumulee = 0
    
    for i in range(len(points) - 1):
        p1, p2 = points[i], points[i + 1]
        dist = p1.distance_2d(p2)
        
        if dist <= 2:
            continue
        
        dz = altitudes_lissees[i + 1] - altitudes_lissees[i]
        pente = (dz / dist) * 100
        pente = round((dz / dist) * 100, 2) # Écrêtage pentes aberrantes
        
        dist_cumulee += dist
        
        segments.append({
            "index"               : i,
            "lat"                 : p2.latitude,
            "lon"                 : p2.longitude,
            "distance_m"          : dist,
            "distance_cumulee_km" : round(dist_cumulee / 1000, 3),
            "altitude_m"          : round(altitudes_lissees[i + 1], 1),
            "pente_pct"           : round(pente, 2),
            "cap_deg"             : calculer_cap(p1, p2),
            "dz_m"                : dz,
        })
    
    return segments

def stats_parcours(segments):
    pentes = [s["pente_pct"] for s in segments]
    return {
        "nb_segments"    : len(segments),
        "distance_km"    : round(segments[-1]["distance_cumulee_km"], 2),
        "altitude_min"   : round(min(s["altitude_m"] for s in segments), 1),
        "altitude_max"   : round(max(s["altitude_m"] for s in segments), 1),
        "pente_min"      : round(min(pentes), 1),
        "pente_max"      : round(max(pentes), 1),
        "denivele_pos"   : round(sum(s["dz_m"] for s in segments if s["dz_m"] > 0)),
        "denivele_neg"   : round(sum(s["dz_m"] for s in segments if s["dz_m"] < 0)),
    }