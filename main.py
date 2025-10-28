import streamlit as st
import folium
from streamlit_folium import st_folium
import xml.etree.ElementTree as ET
import re

st.set_page_config(page_title="Visor de Puntos KML", layout="wide")
st.title("Visor de puntos desde archivos KML")

def limpiar_descripcion(html_text):
    html_text = html_text.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
    filas = re.findall(r"<th[^>]*>(.*?)</th>\s*<td[^>]*>(.*?)</td>", html_text)
    if not filas:
        return html_text.strip()
    return "\n".join([f"{k.strip()}: {v.strip()}" for k, v in filas])

uploaded_files = st.file_uploader(
    "Sube uno o varios archivos KML",
    type=["kml"],
    accept_multiple_files=True
)

if uploaded_files:
    placemarks = []

    for uploaded_file in uploaded_files:
        try:
            tree = ET.parse(uploaded_file)
            root = tree.getroot()
        except Exception as e:
            st.error(f"Error al leer {uploaded_file.name}: {e}")
            continue

        namespace = {"kml": "http://www.opengis.net/kml/2.2"}

        for placemark in root.findall(".//kml:Placemark", namespace):
            name_elem = placemark.find("kml:name", namespace)
            name = name_elem.text if name_elem is not None else "Sin nombre"

            desc_elem = placemark.find("kml:description", namespace)
            desc = limpiar_descripcion(desc_elem.text) if desc_elem is not None else ""

            coord_elem = placemark.find(".//kml:Point/kml:coordinates", namespace)
            if coord_elem is not None and coord_elem.text:
                try:
                    lon, lat, *_ = map(float, coord_elem.text.strip().split(","))
                    placemarks.append((uploaded_file.name, name, (lat, lon), desc))
                except Exception:
                    continue

    if not placemarks:
        st.warning("No se encontraron puntos en los archivos.")
        st.stop()

    latitudes = [p[2][0] for p in placemarks]
    longitudes = [p[2][1] for p in placemarks]
    center = [sum(latitudes)/len(latitudes), sum(longitudes)/len(longitudes)]

    m = folium.Map(location=center, zoom_start=14, control_scale=True)

    for file_name, name, coords, desc in placemarks:
        popup_html = f"""
        <div style='width:350px; white-space:pre-wrap;'>
            <b>{file_name}</b><br>
            <b>{name}</b><br>
            <pre>{desc}</pre>
        </div>
        """
        popup = folium.Popup(popup_html, max_width=500)
        folium.CircleMarker(
            location=coords,
            radius=5,
            color="blue",
            fill=True,
            fill_opacity=0.8,
            popup=popup,
        ).add_to(m)

    st.success(f"Se cargaron {len(uploaded_files)} archivos con {len(placemarks)} puntos.")
    st_folium(m, width=None, height=850, use_container_width=True)
else:
    st.info("Sube uno o más archivos KML para comenzar.")

