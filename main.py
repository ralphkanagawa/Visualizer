import streamlit as st
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import xml.etree.ElementTree as ET
import re

st.set_page_config(layout="wide")

st.title("Visor de archivos KML")
st.markdown("Sube uno o varios ficheros KML para visualizar sus puntos en el mapa.")

uploaded_files = st.file_uploader(
    "Selecciona archivo(s) KML", type=["kml"], accept_multiple_files=True
)

def extraer_tabla_html(descripcion):
    if not descripcion:
        return ""
    descripcion = re.sub(r"<!\[CDATA\[|\]\]>", "", descripcion)
    filas = re.findall(r"<tr>.*?</tr>", descripcion)
    html = "<ul style='padding-left:12px; margin:0; font-size:13px; line-height:1.3;'>"
    for fila in filas:
        celdas = re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", fila)
        if len(celdas) == 2:
            clave = re.sub(r"<[^>]+>", "", celdas[0]).strip()
            valor = re.sub(r"<[^>]+>", "", celdas[1]).strip()
            html += f"<li><b>{clave}:</b> {valor}</li>"
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
                    <div style='width:380px; white-space:normal; font-family:Arial, sans-serif;'>
                        <b>{file.name}</b><br>
                        <b>{name.text if name is not None else ''}</b><br>
                        {extraer_tabla_html(desc.text if desc is not None else '')}
                    </div>
                    """

                    folium.CircleMarker(
                        location=[lat, lon],
                        radius=4,
                        color="blue",
                        fill=True,
                        fill_color="blue",
                        fill_opacity=0.8,
                        popup=folium.Popup(popup_html, max_width=420)
                    ).add_to(cluster)

        except Exception as e:
            st.error(f"Error procesando {file.name}: {e}")

    st_folium(m, width=None, height=800)
else:
    st.info("Sube uno o varios ficheros KML para empezar.")

