import os
import plotly.express as px
import pandas as pd
import geopandas as gpd
import streamlit as st

# Load GeoJSON data
data = gpd.read_file(r'C:\Users\pvs31\Desktop\Data Science Project\OP-heist-project\map_poly\maptest3.geojson')
st.set_page_config(layout="wide")

data_source = data

click_script = """
<script>
        var map = document.getElementById('map');
        map.on('plotly_click', function(eventData) {
            if (eventData.points.length > 0) {
                var featureId = eventData.points[0].location.split('-')[1];
                if (featureId) {
                    var data = JSON.stringify({ featureId: featureId });
                    fetch('/handle_click', {
                        method: 'POST',
                        body: data,
                        headers: {
                            'Content-Type': 'application/json'
                        }
                    });
                }
            }
        });
    </script>
"""

st.write(click_script, unsafe_allow_html=True)
fig = px.choropleth_mapbox(data_source, geojson=data_source.geometry, locations=data_source.index,
                        color=data_source.kuntanro, color_continuous_scale='geyser',
                        mapbox_style="carto-positron",
                        center={"lat": 64.5, "lon": 26},
                        zoom=4,
                        hover_name=data_source.get('nimi', ''),
                        hover_data=["pinta_ala", "posti_alue"])    
fig.update_layout(
    margin={"r":0,"t":0,"l":0,"b":0},
    showlegend=False,
    mapbox=dict(
        bearing=0,
        pitch=0,
        zoom=1,
        center={"lat": 64.5, "lon": 26},
        layers=[]
    )
)

fig.update_mapboxes(
    bounds_east=56.17,
    bounds_west=-1,
    bounds_north=71,
    bounds_south=59
)

st.plotly_chart(fig,use_container_width=True)
