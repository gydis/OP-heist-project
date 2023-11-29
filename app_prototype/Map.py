import os
import plotly.express as px
import pandas as pd
import geopandas as gpd
import streamlit as st
from streamlit_plotly_events import plotly_events

st.set_page_config(
    page_title="Map",
    page_icon="🗺️",
    layout="wide", 
)

# Load GeoJSON data
data = gpd.read_file(r'./map_poly/finland-with-regions_v2_.geojson')
trade_dep = pd.read_csv(r'./data/forecast_values/trade_dependencies.csv')
education_ind = pd.read_csv(r'./data/Indices/education_attainment_index.csv')
code_to_name = education_ind[['Region code', 'Region name (en)']].drop_duplicates()

trade_dep = trade_dep.drop(columns=['Unnamed: 0'])
trade_dep = trade_dep[trade_dep['Time'] == 2023]
cols = trade_dep.columns.tolist()
cols.remove('Time')

col_val = {}
for col in cols:
    col_val[col] = trade_dep[col].values[0]
    
code_to_name_dict = {}
for row in code_to_name.iterrows():
    code_to_name_dict[row[1]['Region name (en)']] = row[1]['Region code']

for row in data.iterrows():
    data.loc[row[0], 'trade_dep'] = col_val[code_to_name_dict[row[1]['nimi']]]

data_source = data
fig = px.choropleth_mapbox(data_source, geojson=data_source.geometry, locations=data_source.index,
                        color=data_source.trade_dep, color_continuous_scale='ylgn',
                        mapbox_style="carto-positron",
                        center={"lat": 64.5, "lon": 26},
                        zoom=4,
                        hover_name=data_source.get('nimi'),
                        hover_data=['code', 'trade_dep'])    
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
# st.plotly_chart(fig,use_container_width=True)
selected_points = plotly_events(fig)
first_point = selected_points[0].get('pointIndex', 18) if len(selected_points) > 0 else 18
code = data_source.iloc[first_point]['code']
chosen_region = code
st.session_state.chosen_region = chosen_region