import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from simulator import simuler

# --- Configuration de la page ---
st.set_page_config(
    page_title="Simulateur Cycliste",
    page_icon="🚴",
    layout="wide"
)

st.title("🚴 Simulateur de Performance Cycliste")
st.markdown("Importe ton fichier GPX et ajuste tes paramètres pour estimer ton temps.")

# --- Initialisation de la mémoire ---
if "resultat" not in st.session_state:
    st.session_state.resultat = None

# --- Barre latérale : paramètres utilisateur ---
st.sidebar.header("⚙️ Tes paramètres")

st.sidebar.subheader("👤 Cycliste & Vélo")
poids_kg = st.sidebar.number_input(
    "Poids total (cycliste + vélo) en kg",
    min_value=40, max_value=150, value=90
)
cda = st.sidebar.slider(
    "Aérodynamisme (CdA)",
    min_value=0.20, max_value=0.50, value=0.26, step=0.01,
    help="0.20 = très aéro (TT) | 0.32 = route standard | 0.40 = position haute"
)

st.sidebar.subheader("⚡ Puissance")
puissance_w = st.sidebar.number_input(
    "Puissance (W)",
    min_value=50, max_value=600, value=239
)
st.sidebar.subheader("👥 Peloton")
peloton = st.sidebar.toggle("Rouler en peloton")
duree_peloton_h = 0.0
if peloton:
    duree_peloton_h = st.sidebar.slider(
        "Durée en peloton (heures)",
        min_value=0.0, max_value=5.0, value=1.0, step=0.25,
        help="Le peloton réduit la résistance aéro de 30%"
    )
    st.sidebar.info(f"⚡ Économie aéro pendant {duree_peloton_h}h")

st.sidebar.subheader("🌤️ Météo")
v_vent_kmh = st.sidebar.slider(
    "Vitesse du vent (km/h)",
    min_value=0, max_value=80, value=5
)
dir_vent_deg = st.sidebar.slider(
    "Direction du vent (0°=Nord, 90°=Est, 180°=Sud)",
    min_value=0, max_value=359, value=0
)

# --- Zone principale : import GPX ---
st.subheader("📂 Importe ton parcours GPX")
fichier = st.file_uploader("Glisse ton fichier .gpx ici", type=["gpx"])

if fichier is not None:
    import tempfile, os
    suffix = os.path.splitext(fichier.name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(fichier.getbuffer())
        chemin_temp = tmp.name

    if st.button("🚀 Lancer la simulation", type="primary"):
        with st.spinner("Calcul en cours..."):
            parametres = {
    "puissance_w"    : puissance_w,
    "poids_kg"       : poids_kg,
    "cda"            : cda,
    "v_vent_kmh"     : v_vent_kmh,
    "dir_vent_deg"   : dir_vent_deg,
    "temperature_c"  : 20,
    "peloton"        : peloton,
    "duree_peloton_h": duree_peloton_h
}
            # On sauvegarde le résultat en mémoire
            st.session_state.resultat = simuler(chemin_temp, parametres)

# --- Affichage des résultats (reste visible même après interaction) ---
if st.session_state.resultat is not None:
    resultat = st.session_state.resultat
    df = pd.DataFrame(resultat["segments"])

    # --- Résultats principaux ---
    st.subheader("🏁 Résultats")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("⏱️ Temps estimé",   resultat["temps_formate"])
    col2.metric("📏 Distance",        f"{resultat['distance_km']} km")
    col3.metric("⚡ Vitesse moyenne", f"{resultat['vitesse_moyenne_kmh']} km/h")
    col4.metric("⛰️ Dénivelé +",      f"{resultat['denivele_pos_m']} m")

    # --- Carte interactive ---
    st.subheader("🗺️ Carte du parcours")

    lat_centre = df["lat"].mean()
    lon_centre = df["lon"].mean()
    carte = folium.Map(location=[lat_centre, lon_centre], zoom_start=12)

    vitesse_max = df["vitesse_kmh"].max()
    vitesse_min = df["vitesse_kmh"].min()

    def couleur_vitesse(v):
        if vitesse_max == vitesse_min:
            return "#3388ff"
        ratio = (v - vitesse_min) / (vitesse_max - vitesse_min)
        if ratio > 0.66:
            return "#00cc44"
        elif ratio > 0.33:
            return "#ff8800"
        else:
            return "#ff2200"

    coords  = list(zip(df["lat"], df["lon"]))
    vitesses = df["vitesse_kmh"].tolist()

    for i in range(len(coords) - 1):
        folium.PolyLine(
            locations=[coords[i], coords[i+1]],
            color=couleur_vitesse(vitesses[i]),
            weight=4,
            opacity=0.8
        ).add_to(carte)

    folium.Marker(
        location=coords[0],
        popup="🟢 Départ",
        icon=folium.Icon(color="green", icon="play")
    ).add_to(carte)

    folium.Marker(
        location=coords[-1],
        popup="🏁 Arrivée",
        icon=folium.Icon(color="red", icon="flag")
    ).add_to(carte)

    st_folium(carte, use_container_width=True, height=500)

    st.markdown("""
    **Légende vitesse :**
    🟢 Rapide &nbsp;&nbsp; 🟠 Moyen &nbsp;&nbsp; 🔴 Lent
    """)

    # --- Graphiques ---
    st.subheader("📈 Profil du parcours")
    st.area_chart(
        df.set_index("distance_cumulee_km")["altitude_m"],
        use_container_width=True
    )

    st.subheader("⚡ Puissance & Vitesse par segment")
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.line_chart(
            df.set_index("distance_cumulee_km")["vitesse_kmh"],
            use_container_width=True
        )
    with col_g2:
        st.line_chart(
            df.set_index("distance_cumulee_km")["watts"],
            use_container_width=True
        )

    # --- Tableau détaillé ---
    st.subheader("📊 Détail des segments")
    st.dataframe(
        df[["distance_cumulee_km", "altitude_m", "pente_pct", "vitesse_kmh", "watts"]]
        .rename(columns={
            "distance_cumulee_km": "Distance (km)",
            "altitude_m"         : "Altitude (m)",
            "pente_pct"          : "Pente (%)",
            "vitesse_kmh"        : "Vitesse (km/h)",
            "watts"              : "Puissance (W)"
        }),
        use_container_width=True,
        hide_index=True
    )

else:
    st.info("👈 Commence par importer ton fichier GPX.")