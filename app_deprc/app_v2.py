import streamlit as st
import geopandas as gpd
import plotly.express as px

# Title for the Streamlit app
st.title("GeoJSON Map Viewer with Hover Highlight (Plotly)")

# Upload a GeoJSON file
#geojson_file = st.file_uploader("Upload a GeoJSON file", type=["geojson"])

if True:
    # Read the GeoJSON file using GeoPandas
    gdf = gpd.read_file(r"C:\Users\pvs31\Desktop\Data Science Project\OP-heist-project\map_poly\maptest3.geojson")
    print("hey")
    # Create a Plotly choropleth map
    fig = px.choropleth(
        gdf,
        geojson=gdf.geometry.__geo_interface__,
        locations=gdf.index,
        color=gdf['nimi'],  # Change 'name' to the column you want to use for coloring
        hover_name=gdf['nimi'],  # Change 'name' to the column for hover information
    )

    # Display the Plotly map using Streamlit
    st.plotly_chart(fig)
