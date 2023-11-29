#File for the region specific dashboard
import streamlit as st
import pandas as pd
import numpy as np
import re
import plotly.express as px
import plotly.graph_objects as go
import plotly.express as px
import random

from menu_options import *


@st.cache_data
def load_data():
    education_ind = pd.read_csv(r'./data/Indices/education_attainment_index.csv')
    code_to_name = education_ind[['Region code', 'Region name (en)']].drop_duplicates()
    # gdp_region_ind = pd.read_csv(r'./data/Indices/gdp_region_index.csv')
    # industry_ind = pd.read_csv(r'./data/Indices/industries_indexes.csv', index_col=0)
    # industry_ind.reset_index(drop=True, inplace=True)
    # population_den = pd.read_csv(r'./data/Indices/population_density_index.csv')
    # region_ind = pd.read_csv(r'./data/Indices/regional_indexes.csv', index_col=0)
    # tax_ind = pd.read_csv(r'./data/Indices/tax_revenue_index.csv') 
    # working_age_ind = pd.read_csv(r'./data/Indices/working_age_population_index.csv')
    # #Find columns with same names and print out
    
    # # Replace name of columns with region code and year
    # industry_ind.rename(columns={'Area':'Region code', 'Time':'Year'}, inplace=True)
    # region_ind.rename(columns={'Area':'Region code', 'Time':'Year'}, inplace=True)
    
    # # Drop duplicate columns with names
    # names = education_ind[['Region code', 'Region name (en)', 'Region name (fi)']]
    # education_ind.drop(columns=['Region name (en)', 'Region name (fi)'], inplace=True)
    # gdp_region_ind.drop(columns=['Region name (en)', 'Region name (fi)'], inplace=True)
    # population_den.drop(columns=['Region name (en)', 'Region name (fi)'], inplace=True)
    # tax_ind.drop(columns=['Region name (en)', 'Region name (fi)'], inplace=True)
    # working_age_ind.drop(columns=['Region name (en)', 'Region name (fi)'], inplace=True)
    
    # # Merge region-specific dataframes
    # region_data = pd.merge(education_ind, gdp_region_ind, on=['Region code', 'Year'], how='outer')
    # region_data = pd.merge(region_data, population_den, on=['Region code', 'Year'], how='outer')
    # region_data = pd.merge(region_data, region_ind, on=['Region code', 'Year'], how='outer')
    # region_data = pd.merge(region_data, tax_ind, on=['Region code', 'Year'], how='outer')
    # region_data = pd.merge(region_data, working_age_ind, on=['Region code', 'Year'], how='outer')
    
    # region_data = pd.merge(region_data, names, on=['Region code'], how='outer')
    # industry_ind = pd.merge(industry_ind, names, on=['Region code'], how='outer')
    
    # Read regional indices with forecasts
    indices = {
        "Bachelor Degree" : r'./data/forecast_values/bachelor.csv',
        "Doctoral Degree" : r'./data/forecast_values/doctoral.csv',
        "Master Degree" : r'./data/forecast_values/master.csv',
        "GDP Per Capita" : r'./data/forecast_values/gdp_per_capita.csv',
        "GDP" : r'./data/forecast_values/gdp.csv',
        "Population Density" : r'./data/forecast_values/population_density.csv',
        "Tax Revenue" : r'./data/forecast_values/tax_revenue.csv',
        "Working Age Population" : r'./data/forecast_values/working_age_population.csv'
    }
    
    indices_2 = {
        "Export Value" : r'./data/forecast_values/exports.csv',
        "Export Growth" : r'./data/forecast_values/exports_growth.csv',
        "Trade Imbalance" : r'./data/forecast_values/imbalances.csv',
        "Import Value" : r'./data/forecast_values/imports.csv',
        "Import Growth" : r'./data/forecast_values/imports_growth.csv',
        "Trade Dependency" : r'./data/forecast_values/trade_dependencies.csv'
    }
    
    for key, value in indices.items():
        frame = pd.read_csv(value)
        frame.index = frame['Year']
        frame.drop(columns=['Year'], inplace=True)
        frame = frame.stack()
        frame.index = frame.index.rename('Region code', level=1)
        frame.name = key
        indices[key] = frame
    indices = pd.concat(indices, axis=1)
    
    for key, value in indices_2.items():
        frame = pd.read_csv(value, index_col=0)
        frame.rename(columns={'Time' : 'Year'}, inplace=True)
        frame.index = frame['Year']
        frame.drop(columns=['Year'], inplace=True)
        frame = frame.stack()
        frame.index = frame.index.rename('Region code', level=1)
        frame.name = key
        indices_2[key] = frame
    
    indices_2 = pd.concat(indices_2, axis=1)
    
    region_data = pd.merge(indices, indices_2, on=['Region code', 'Year'], how='outer').reset_index()
    
    # Read industry-specific indices with forecasts
    industry_indices = {
        "Export Value" : r'./data/forecast_values/exports_industry.csv',
        "Export Growth" : r'./data/forecast_values/exports_growth_industry.csv',
        "Trade Imbalance" : r'./data/forecast_values/imbalances_industry.csv',
        "Import Value" : r'./data/forecast_values/imports_industry.csv',
        "Import Growth" : r'./data/forecast_values/imports_growth_industry.csv',
        "Trade Dependency" : r'./data/forecast_values/trade_dependencies_industry.csv'
    }
    
    for key, value in industry_indices.items():
        frame = pd.read_csv(value, index_col=0)
        frame.rename(columns={'Time' : 'Year'}, inplace=True)
        frame = pd.wide_to_long(frame, stubnames=[f'MK{i:02}' for i in range(1, 22)], i='Year', j='Industry', sep='_', suffix='\w+')
        frame.dropna(axis=1, inplace=True, how='all')
        frame = frame.stack()
        frame.index = frame.index.rename('Region code', level=2)
        frame.name = key
        industry_indices[key] = frame
    
    industry_ind = pd.concat(industry_indices, axis=1).reset_index()
        
        # read csv files for demographic info
    df_2010_2012 = pd.read_csv("./data/region_city_data/city_info_2010_2012.csv")
    df_2013_2015 = pd.read_csv("./data/region_city_data/city_info_2013_2015.csv")
    df_2016_2018 = pd.read_csv("./data/region_city_data/city_info_2016_2018.csv")
    df_2019_2021 = pd.read_csv("./data/region_city_data/city_info_2019_2021.csv")
    df_2011_2021 = pd.read_csv("./data/region_city_data/region_info_2011_2021.csv")

    # remove redundant codes in the dataset of regions in Finland
    df_2011_2021["Information"] = df_2011_2021["Information"].apply(
        lambda row: re.sub(r"(\([A-Z]+\)$)|(^[A-Z] )", "", row).strip()
    )
    
    # merge datasets of municipalities in Finland into a continuous timeline
    df_2010_2015 = pd.merge(df_2010_2012, df_2013_2015, on=["Region", "Information"])
    df_2010_2018 = pd.merge(df_2010_2015, df_2016_2018, on=["Region", "Information"])
    df_2010_2021 = pd.merge(df_2010_2018, df_2019_2021, on=["Region", "Information"])

    # remove redundant codes in the dataset of municipalities in Finland
    df_2010_2021["Information"] = df_2011_2021["Information"].apply(
        lambda row: re.sub(r"(\([A-Z]+\)$)|(^[A-Z] )", "", row).strip()
    )



    # Return region-specific indices and industry-specific separately
    return region_data, industry_ind, df_2010_2021, df_2011_2021, code_to_name

def dashboard(region_code, key):
    region_data, industry_ind, df_2010_2021, df_2011_2021, code_to_name = load_data()
    # =====================================================================================================
    # Create multiselection dropdown menus for user to choose region(s) and info(s) to display the graph(s)
    # =====================================================================================================
    option_region = st.selectbox(
        "Choose region",
        df_2011_2021["Region"].unique(),
        key=key+1,
        index=code_to_name['Region code'].tolist().index(region_code)
    )
    region_code = option_region[:4]
    region_name = option_region[5:]
    
    chosen_region_data = region_data[region_data['Region code'] == region_code]
    chosen_industry_ind = industry_ind[industry_ind['Region code'] == region_code]

    chosen_region_data.drop(columns=['Region code'], inplace=True)    

    # Print out region name
    st.header(f'Region: {region_name}')
    
    # Regional trade dependency ranking and value
    last_trade_dep_curr = region_data.set_index(['Region code'])[['Year', 'Trade Dependency']].dropna().sort_values('Year').groupby('Region code').nth(-4)
    last_trade_dep_curr['rank'] = last_trade_dep_curr['Trade Dependency'].rank(ascending=False, method='first')

    last_trade_dep_4y = region_data.set_index(['Region code'])[['Year', 'Trade Dependency']].dropna().sort_values('Year').groupby('Region code').nth(-8)
    last_trade_dep_4y['rank'] = last_trade_dep_4y['Trade Dependency'].rank(ascending=False, method='first')
    
    rank_change = last_trade_dep_curr['rank'] - last_trade_dep_4y['rank']
    val_change = last_trade_dep_curr['Trade Dependency'] - last_trade_dep_4y['Trade Dependency']
    
    col1, col2 = st.columns([0.1, 0.1])
    tooltip = "This metric measures how dependent a region is on international trade. A high trade dependency ratio suggests that a region's economy is heavily reliant on international trade, making it more vulnerable to trade disruptions or economic downturns."
    col1.metric(label='Trade dependency rank', value=int(last_trade_dep_curr['rank'][region_code]), 
                delta=f'{int(rank_change[region_code])}', delta_color='off', help="Position of the region in the ranking of trade dependency. (1 = most dependent)")
    col2.metric(label='Trade dependency value', value=f'{last_trade_dep_curr["Trade Dependency"][region_code]:.2f}', 
                delta=f'{val_change[region_code]:.2f}', delta_color='off', help=tooltip)
    
    st.header('Important indicators')
    col1, col2 = st.columns([0.45, 0.55])
    
    # Important indicators box
    data = chosen_region_data.set_index(['Year']).drop_duplicates().dropna(how='all').sort_values(['Year'])
    with col1:
        indicators = ['GDP', 'Import Value', 'Export Value', 'Tax Revenue', 'Working Age Population']
        units = [' (€B)', ' (€B)', ' (€B)', ' (€B)', ' (1000s people)']
        order = [10**9, 10**9, 10**9, 10**9, 10**3]
        formatting = ['{:.2f}', '{:.2f}', '{:.2f}', '{:.2f}', '{:.2f}']
        values = [data[i].dropna().iloc[-1] for i in indicators]
        deltas = [(data[i].dropna().iloc[-4] - data[i].dropna().iloc[-8]) / data[i].dropna().iloc[-8] for i in indicators]
        deltas = [f'{d*100:.2f}%' for d in deltas]
        values = [v/o for v, o in zip(values, order)]
        values = [f.format(v) for f, v in zip(formatting, values)]
        values = [f'{v}{u}' for v, u in zip(values, units)]
        metrics = [st.metric(label=indicators[i], value=values[i], delta=deltas[i]) for i in range(len(indicators))]

    def employment_pie_chart():
        # =========================================================================
        # Plot pie chart of industries distribution for each chosen regions in 2020
        # =========================================================================
        employed = df_2011_2021[
            (df_2011_2021["Region"] == option_region)
            & (df_2011_2021["Information"].isin(option_industries))
        ]
        fig_1 = px.pie(
            employed,
            values="2020",
            names="Information",
            title=f"Industries distribution of {option_region}",
            hover_name="Information",
        )
        fig_1.update_layout(
            legend=dict(y=-2, x=0),
            width=1100,
            height=690,
            # margin=dict(l=50, r=50, b=50, t=50)
        )
        st.plotly_chart(fig_1, theme="streamlit", use_container_width=True)


    with col2:        
        employment_pie_chart() 
        
    index_to_graph = st.selectbox("Choose index to graph", [None,  'GDP', 'Import Value', 'Export Value', 'Tax Revenue', 'Working Age Population'], key=key+2)
    
    def graph(index_to_graph):
        if index_to_graph is not None:
            fig = go.Figure()
            ser = data[index_to_graph].dropna()
            fig.add_trace(go.Scatter(x=ser.index[:-3], y=ser.iloc[:-3], name=index_to_graph))
            fig.add_trace(go.Scatter(x=ser.index[-4:], y=ser.iloc[-4:], line = dict(shape = 'linear', dash = 'dot'), showlegend=False))
            fig.update_layout(
                xaxis_title="Year",
                yaxis_title=index_to_graph,
                legend_title="Legend",
                width=500,
                height=500,
                 xaxis = dict(
                    tickmode = 'linear',
                    tick0 = ser.index.min(),
                    dtick = 1
                )
            )
            st.plotly_chart(fig, use_container_width=True)
    
    graph(index_to_graph)

        
    col1, col2 = st.columns([0.5, 0.5])
    
    curr_industry_inds = chosen_industry_ind.set_index(['Year']).drop_duplicates().dropna(how='all').sort_values(['Year']).groupby(['Industry']).nth(-4)
    curr_industry_inds['rank'] = curr_industry_inds['Export Value'].rank(ascending=False, method='first')
    sorted_industries = curr_industry_inds.set_index(['rank'])[['Industry']].sort_index()
    with col1:
        st.subheader("Top 3 industries")
        top3 = sorted_industries.iloc[:3]['Industry'].to_list()
        top3 = ["1. " + industry_dict[i] for i in top3]
        st.markdown('\n'.join(top3))
        
    with col2:
        st.subheader("Bottom 3 industries")
        bottom3 = sorted_industries.iloc[-3:]['Industry'].to_list()
        bottom3 = ["1. " + industry_dict[i] for i in bottom3]
        st.markdown('\n'.join(bottom3))
        

        
    


    # ==================================================================
    # Plot line graph of a chosen index of a chosen industry 2015 - 2020
    # ==================================================================
    st.title("Index of Industry in Region")

    inv_industry_dict = {v: k for k, v in industry_dict.items()}

    industry_ind_new = industry_ind
    industry_ind_new = industry_ind_new.set_index(['Year']).loc[industry_ind_new['Year'].unique()[:-3]].reset_index()
    industry_ind_new = industry_ind_new[industry_ind_new['Region code'] == option_region.split()[0]].drop_duplicates()
    industry_ind_new['Industry'] = industry_ind_new['Industry'].apply(lambda row: industry_dict[row])

    pred_export_growth = pd.read_csv(r'./data/forecast_values/exports_growth_industry.csv')
    pred_import_growth = pd.read_csv(r'./data/forecast_values/imports_growth_industry.csv')
    pred_export = pd.read_csv(r'./data/forecast_values/exports_industry.csv')
    pred_import = pd.read_csv(r'./data/forecast_values/imports_industry.csv')
    pred_imbalance = pd.read_csv(r'./data/forecast_values/imbalances_industry.csv')
    pred_trade_dependency = pd.read_csv(r'./data/forecast_values/trade_dependencies_industry.csv')
    
    index_to_data_dict = {
        "Export Value": pred_export[pred_export.columns[1:]],
        "Import Value": pred_import[pred_import.columns[1:]],
        "Trade Dependency": pred_trade_dependency[pred_trade_dependency.columns[1:]],
        "Trade Imbalance": pred_imbalance[pred_imbalance.columns[1:]],
        "Export Growth": pred_export_growth[pred_export_growth.columns[1:]],
        "Import Growth": pred_import_growth[pred_import_growth.columns[1:]],
    }
    
    col1, col2 = st.columns([0.4, 0.6], gap="large")
    index = "Export"

    indices_unit_dict = {
        "Employment": "(Number of people)",
        "Export Value": "(Euros)",
        "Import Value": "(Euros)",
        "Trade Dependency": "(Percentage)",
        "Trade Imbalance": "(Percentage)",
        "Export Growth": "(Percentage)",
        "Import Growth": "(Percentage)",
    }

    with col1:
        industry_list = st.multiselect("Choose industry", industry_dict.values(), ['Agriculture, forestry and fishing'], max_selections=3, key=key+3)

        index = st.selectbox("Choose index", [
            "Employment",
            "Export Value",
            "Import Value",
            "Trade Dependency",
            "Trade Imbalance",
            "Export Growth",
            "Import Growth",
        ], key=key+4)
        st.caption("Dashed line indicates predicted values")

    with col2:
        combined_fig = go.Figure()
        combined_fig.update_layout(
            showlegend=True,
            height=500,
            xaxis_title="Year", 
            legend=dict(yanchor="top", y=-0.3, xanchor="left", x=0)
        )
        for industry in industry_list:
            if index != "Employment":
                pred_data = index_to_data_dict[index]
                region_industry_code = option_region[:4] + '_' + inv_industry_dict[industry]
                pred_data_new = pred_data[["Time", region_industry_code]]
                pred_fig = go.Scatter(x=pred_data_new["Time"], y=pred_data_new[region_industry_code], line = dict(shape = 'linear', dash = 'dot'), showlegend=False)

                industry_ind_plot = industry_ind_new[industry_ind_new['Industry'] == industry]
                industry_ind_plot = industry_ind_plot[["Year", index]]
                fig = go.Scatter(x=industry_ind_plot["Year"], y=industry_ind_plot[index], name=industry)
                
                combined_fig.add_traces(pred_fig)
                combined_fig.add_traces(fig)
                combined_fig.update_layout(
                    title=f"{index} of chosen industries in {option_region}",
                    yaxis_title=f"{index} " + indices_unit_dict[index],
                )
            else:
                employment_plot = df_2011_2021[df_2011_2021["Region"] == option_region]
                employment_plot = employment_plot[employment_plot["Information"] == industry].reset_index(drop=True)
                employment_plot = employment_plot[['2015', '2016', '2017', '2018', '2019', '2020']]
                x_axis = employment_plot.columns
                y_axis = employment_plot.loc[0]
                fig = go.Scatter(x=x_axis, y=y_axis, name=industry)
                combined_fig.add_traces(fig)
                combined_fig.update_layout(
                    title=f"{index} of chosen industries in {option_region}",
                    yaxis_title=f"{index} " + indices_unit_dict[index],
                )

        if industry_list:
            st.plotly_chart(combined_fig, use_container_width=True)
        else:
            st.write("Please choose at least 1 region and 1 information")

st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="wide", 
)
region_code = st.session_state.chosen_region if 'chosen_region' in st.session_state else 'MK01'
st.title('Region-specific dashboard')
col1, col2 = st.columns(2, gap="large")        
with col1:
    dashboard(region_code, 1)

with col2:
    dashboard(region_code, 10)