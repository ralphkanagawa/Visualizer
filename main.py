import streamlit as st
import folium
from streamlit_folium import st_folium
from fastkml import kml

st.set_page_config(page_title="Visor de Puntos KML", layout="wide")
st.title("Visor de puntos desde archivo KML")

uploaded_file = st.file_uploader("Sube un archivo KML", type=["kml"])

if uploaded_file:
    data = uploaded_file.read()
    k = kml.KML()
    try:
        k.from_string(data)
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
        st.stop()

    placemarks = []

    try:
        doc = next(k.features())  # primer nivel: Document
        for feature in doc.features():  # segundo nivel: Placemark
            if feature.geometry and feature.geometry.geom_type == 'Point':
                coords = (feature.geometry.y, feature.geometry.x)
                placemarks.append((feature.name, coords, feature.description))
    except Exception as e:
        st.error(f"No se pudieron extraer los puntos: {e}")
        st.stop()

    if not placemarks:
        st.warning("No se encontraron puntos en el archivo.")
        st.stop()

    latitudes = [p[1][0] for p in placemarks]
    longitudes = [p[1][1] for p in placemarks]
    center = [sum(latitudes)/len(latitudes), sum(longitudes)/len(longitudes)]

    m = folium.Map(location=center, zoom_start=15)

    for name, coords, desc in placemarks:
        popup_html = f"<b>{name}</b><br>{desc}"
        folium.Marker(location=coords, popup=popup_html).add_to(m)

    st.success(f"Se cargaron {len(placemarks)} puntos.")
    st_folium(m, width=1000, height=700)
else:
    st.info("Sube un archivo KML para comenzar.")
