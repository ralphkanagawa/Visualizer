import streamlit as st
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import xml.etree.ElementTree as ET
import re

st.set_page_config(layout="wide")

st.title("Visor de archivos KML")
st.markdown("Sube uno o varios ficheros KML para visualizar sus puntos en el mapa.")

uploaded_files = st.file_uploader("Selecciona archivo(s) KML", type=["kml"], accept_multiple_files=True)

def limpiar_descripcion(texto):
    if not texto:
        return ""
    texto = texto.replace("\n", " ").replace("\r", " ").strip()
    texto = re.sub(r"\s*([A-ZÁÉÍÓÚÑ0-9_]+):", r"\n\1:", texto)
    lineas = [line.strip() for line in texto.split("\n") if line.strip()]
    html = "<ul style='padding-left:10px; margin:0;'>"
    for linea in lineas:
        # negrita para clave: valor
        if ":" in linea:
            clave, valor = linea.split(":", 1)
            html += f"<li><b>{clave.strip()}:</b> {valor.strip()}</li>"
        else:
            html += f"<li>{linea}</li>"
    html += "</ul>"
    return html

if uploaded_files:
    m = folium.Map(location=[-2.2, -80.95], zoom_start=14, control_scale=True)
    cluster = MarkerCluster().add_to(m)

    for file in uploaded_files:
        try:
            tree = ET.parse(file)
            root = tree.getroot()

            ns = {"kml": "http://www.opengis.net/kml/2.2"}

            for pm in root.findall(".//kml:Placemark", ns):
                name = pm.find("kml:name", ns)
                desc = pm.find("kml:description", ns)
                coords = pm.find(".//kml:Point/kml:coordinates", ns)

                if coords is not None:
                    lon, lat, *_ = coords.text.strip().split(",")
                    lat, lon = float(lat), float(lon)

                    popup_html = f"""
                    <div style='width:380px; white-space:normal;'>
                        <b>{file.name}</b><br>
                        <b>{name.text if name is not None else ''}</b><br>
                        {limpiar_descripcion(desc.text if desc is not None else '')}
                    </div>
                    """

                    folium.CircleMarker(
                        location=[lat, lon],
                        radius=4,
                        color="blue",
                        fill=True,
                        fill_color="blue",
                        fill_opacity=0.7,
                        popup=folium.Popup(popup_html, max_width=400)
                    ).add_to(cluster)

        except Exception as e:
            st.error(f"Error procesando {file.name}: {e}")

    st_folium(m, width=1400, height=800)
else:
    st.info("Sube uno o varios ficheros KML para empezar.")
