import streamlit as st
import folium
from streamlit_folium import st_folium
import xml.etree.ElementTree as ET
import re

st.set_page_config(page_title="Visor de Puntos KML", layout="wide")
st.title("Visor de puntos desde archivo KML")

def limpiar_descripcion(html_text):
    html_text = html_text.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
    filas = re.findall(r"<th[^>]*>(.*?)</th>\s*<td[^>]*>(.*?)</td>", html_text)
    if not filas:
        return html_text.strip()
    return "\n".join([f"{k.strip()}: {v.strip()}" for k, v in filas])

uploaded_file = st.file_uploader("Sube un archivo KML", type=["kml"])

if uploaded_file:
    try:
        tree = ET.parse(uploaded_file)
        root = tree.getroot()
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
        st.stop()

    namespace = {"kml": "http://www.opengis.net/kml/2.2"}
    placemarks = []

    for placemark in root.findall(".//kml:Placemark", namespace):
        name_elem = placemark.find("kml:name", namespace)
        name = name_elem.text if name_elem is not None else "Sin nombre"

        desc_elem = placemark.find("kml:description", namespace)
        desc = limpiar_descripcion(desc_elem.text) if desc_elem is not None else ""

        coord_elem = placemark.find(".//kml:Point/kml:coordinates", namespace)
        if coord_elem is not None and coord_elem.text:
            try:
                lon, lat, *_ = map(float, coord_elem.text.strip().split(","))
                placemarks.append((name, (lat, lon), desc))
            except Exception:
                continue

    if not placemarks:
        st.warning("No se encontraron puntos en el archivo.")
        st.stop()

    # Centro del mapa
    latitudes = [p[1][0] for p in placemarks]
    longitudes = [p[1][1] for p in placemarks]
    center = [sum(latitudes)/len(latitudes), sum(longitudes)/len(longitudes)]

    m = folium.Map(location=center, zoom_start=15)

    for name, coords, desc in placemarks:
        popup_html = f"<b>{name}</b><br><pre>{desc}</pre>"
        folium.CircleMarker(
            location=coords,
            radius=5,
            color="blue",
            fill=True,
            fill_opacity=0.8,
            popup=popup_html,
        ).add_to(m)

    st.success(f"Se cargaron {len(placemarks)} puntos.")
    st_folium(m, width=1000, height=700)
else:
    st.info("Sube un archivo KML para comenzar.")
