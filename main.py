import streamlit as st
import folium
from streamlit_folium import st_folium
from fastkml import kml

st.set_page_config(page_title="Visor KML", layout="wide")
st.title("Visor de archivos KML")

uploaded_files = st.file_uploader(
    "Sube uno o varios archivos KML",
    type=["kml"],
    accept_multiple_files=True
)

if uploaded_files:
    m = folium.Map(location=[0, 0], zoom_start=2)
    total_placemarks = 0

    for uploaded_file in uploaded_files:
        st.write(f"Procesando: **{uploaded_file.name}**")

        k = kml.KML()
        try:
            k.from_string(uploaded_file.read())
        except Exception as e:
            st.error(f"Error al leer {uploaded_file.name}: {e}")
            continue

        placemarks = []

        def extract_features(features):
            for f in features:
                if hasattr(f, 'geometry') and f.geometry:
                    placemarks.append(f)
                if hasattr(f, 'features'):
                    try:
                        extract_features(list(f.features()))
                    except Exception:
                        continue

        try:
            layers = list(k.features())
            for layer in layers:
                if hasattr(layer, 'features'):
                    extract_features(list(layer.features()))
        except Exception:
            st.warning(f"No se pudieron extraer las features de {uploaded_file.name}")
            continue

        if not placemarks:
            st.info(f"No se encontraron elementos geográficos en {uploaded_file.name}")
            continue

        for p in placemarks:
            geom = p.geometry
            if geom.geom_type == 'Point':
                folium.Marker(
                    location=[geom.y, geom.x],
                    popup=p.name or uploaded_file.name
                ).add_to(m)
            elif geom.geom_type == 'Polygon':
                folium.GeoJson(
                    data=geom.__geo_interface__,
                    name=p.name or uploaded_file.name
                ).add_to(m)
            elif geom.geom_type == 'LineString':
                folium.PolyLine(
                    locations=[(pt[1], pt[0]) for pt in geom.coords],
                    color="blue"
                ).add_to(m)

        total_placemarks += len(placemarks)

    st.success(f"Se cargaron {len(uploaded_files)} archivos y {total_placemarks} elementos geográficos.")
    st_folium(m, width=1000, height=700)
else:
    st.info("Sube uno o más archivos KML para comenzar.")
