import streamlit as st
import folium
from streamlit_folium import st_folium
from fastkml import kml

st.set_page_config(page_title="Visor KML", layout="wide")
st.title("Visor de archivos KML")

uploaded_file = st.file_uploader("Sube un archivo KML", type=["kml"])

if uploaded_file:
    k = kml.KML()
    k.from_string(uploaded_file.read())
    
    features = list(k.features())
    placemarks = []
    
    def extract_features(features):
        for f in features:
            if hasattr(f, 'geometry') and f.geometry:
                placemarks.append(f)
            if hasattr(f, 'features'):
                extract_features(list(f.features()))
    
    extract_features(features)

    m = folium.Map(location=[0, 0], zoom_start=2)
    
    for p in placemarks:
        geom = p.geometry
        if geom.geom_type == 'Point':
            folium.Marker(
                location=[geom.y, geom.x],
                popup=p.name or "Sin nombre"
            ).add_to(m)
        elif geom.geom_type == 'Polygon':
            folium.GeoJson(data=geom.__geo_interface__).add_to(m)
        elif geom.geom_type == 'LineString':
            folium.PolyLine(
                locations=[(pt[1], pt[0]) for pt in geom.coords],
                color="blue"
            ).add_to(m)
    
    st_folium(m, width=1000, height=700)
