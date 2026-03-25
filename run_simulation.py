from simulator import simuler

parametres = {
    "puissance_w"  : 243,
    "poids_kg"     : 90,
    "cda"          : 0.26,
    "v_vent_kmh"   : 5,
    "dir_vent_deg" : 0,
    "temperature_c": 20
}

resultat = simuler("data/IM_AGADIR.gpx", parametres)

print("="*45)
print("RÉSULTAT DE LA SIMULATION")
print("="*45)
print(f"Temps simulé    : {resultat['temps_formate']}")
print(f"Distance        : {resultat['distance_km']} km")
print(f"Vitesse moyenne : {resultat['vitesse_moyenne_kmh']} km/h")
print(f"Dénivelé +      : {resultat['denivele_pos_m']} m")
print("="*45)
print("TON TEMPS RÉEL  : 2h 25min 10s")
print("="*45)