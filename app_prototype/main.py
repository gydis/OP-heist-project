import os
import plotly.express as px
import pandas as pd
import geopandas as gpd
import streamlit as st
from streamlit_plotly_events import plotly_events

# Load GeoJSON data
data = gpd.read_file(r'C:\Users\pvs31\Desktop\Data Science Project\OP-heist-project\map_poly\maptest3.geojson')
st.set_page_config(layout="wide")

data_source = data
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

st.markdown("""
    <style>
    .stPlotlyChart {
        width: 100%;
        height: 100vh;
    }
    </style>
""", unsafe_allow_html=True)

fig.update_layout(clickmode='event+select')
#st.plotly_chart(fig,use_container_width=True)
selected_points = plotly_events(fig)
first_point = selected_points[0]
x_value = first_point["pointIndex"]
st.header(data['nimi'].iloc[int(x_value)])



