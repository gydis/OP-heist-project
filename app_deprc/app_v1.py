import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import folium_static

# Title for the Streamlit app
st.title("GeoJSON Map Viewer with Hover Highlight")

# Upload a GeoJSON file
geojson_file = st.file_uploader("Upload a GeoJSON file", type=["geojson"])

if geojson_file is not None:
    # Read the GeoJSON file using GeoPandas
    gdf = gpd.read_file(geojson_file)

    # Create a Folium map
    m = folium.Map(location=[gdf['geometry'].centroid.y.mean(), gdf['geometry'].centroid.x.mean()], zoom_start=10)

    for _, row in gdf.iterrows():
        folium.GeoJson(row['geometry'], name=row['name']).add_to(m)

    # Add JavaScript code for interactivity
    folium.GeoJson(gdf, name="Features").add_to(m)
    script = f"var featureGroup = {m.get_name()}['Features']; featureGroup.on('mouseover', function(event) {{event.layer.setStyle({{'fillColor': 'yellow', 'color': 'yellow'}});}}); featureGroup.on('mouseout', function(event) {{event.layer.setStyle({{'fillColor': 'blue', 'color': 'blue'}});}});"
    folium.Element(script).add_to(m)

    # Display the map using streamlit_folium
    folium_static(m)
