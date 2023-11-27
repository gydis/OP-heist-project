#File for the region specific dashboard
import streamlit as st
import pandas as pd
import numpy as np
import re
import plotly.express as px
import plotly.graph_objects as go
import plotly.express as px

from menu_options import *

st.set_page_config(layout="wide")

@st.cache_data
def load_data():
    education_ind = pd.read_csv(r'./data/Indices/education_attainment_index.csv')
    code_to_name = education_ind[['Region code', 'Region name (en)']].drop_duplicates()
    gdp_region_ind = pd.read_csv(r'./data/Indices/gdp_region_index.csv')
    industry_ind = pd.read_csv(r'./data/Indices/industries_indexes.csv', index_col=0)
    industry_ind.reset_index(drop=True, inplace=True)
    population_den = pd.read_csv(r'./data/Indices/population_density_index.csv')
    region_ind = pd.read_csv(r'./data/Indices/regional_indexes.csv', index_col=0)
    tax_ind = pd.read_csv(r'./data/Indices/tax_revenue_index.csv') 
    working_age_ind = pd.read_csv(r'./data/Indices/working_age_population_index.csv')
    #Find columns with same names and print out
    
    # Replace name of columns with region code and year
    industry_ind.rename(columns={'Area':'Region code', 'Time':'Year'}, inplace=True)
    region_ind.rename(columns={'Area':'Region code', 'Time':'Year'}, inplace=True)
    
    # Drop duplicate columns with names
    names = education_ind[['Region code', 'Region name (en)', 'Region name (fi)']]
    education_ind.drop(columns=['Region name (en)', 'Region name (fi)'], inplace=True)
    gdp_region_ind.drop(columns=['Region name (en)', 'Region name (fi)'], inplace=True)
    population_den.drop(columns=['Region name (en)', 'Region name (fi)'], inplace=True)
    tax_ind.drop(columns=['Region name (en)', 'Region name (fi)'], inplace=True)
    working_age_ind.drop(columns=['Region name (en)', 'Region name (fi)'], inplace=True)
    
    # Merge region-specific dataframes
    region_data = pd.merge(education_ind, gdp_region_ind, on=['Region code', 'Year'], how='outer')
    region_data = pd.merge(region_data, population_den, on=['Region code', 'Year'], how='outer')
    region_data = pd.merge(region_data, region_ind, on=['Region code', 'Year'], how='outer')
    region_data = pd.merge(region_data, tax_ind, on=['Region code', 'Year'], how='outer')
    region_data = pd.merge(region_data, working_age_ind, on=['Region code', 'Year'], how='outer')
    
    region_data = pd.merge(region_data, names, on=['Region code'], how='outer')
    industry_ind = pd.merge(industry_ind, names, on=['Region code'], how='outer')
    
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

def dashboard(region_code):
    st.title('Region-specific dashboard')
    region_data, industry_ind, df_2010_2021, df_2011_2021, code_to_name = load_data()
    # =====================================================================================================
    # Create multiselection dropdown menus for user to choose region(s) and info(s) to display the graph(s)
    # =====================================================================================================
    option_region = st.selectbox(
        "Choose region",
        df_2011_2021["Region"].unique(),
    )
    
    region_code = option_region[:4]

    # Filter data based on region code
    chosen_region_data = region_data[region_data['Region code'] == region_code]
    chosen_industry_ind = industry_ind[industry_ind['Region code'] == region_code]
    
    # Save region name
    region_name = code_to_name[code_to_name['Region code'] == region_code]['Region name (en)'].iloc[0]
    # Drop columns with region name and code
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
    col1.metric(label='Trade dependency rank', value=int(last_trade_dep_curr['rank'][region_code]), 
                delta=f'{int(rank_change[region_code])}', delta_color='off')
    col2.metric(label='Trade dependency value', value=f'{last_trade_dep_curr["Trade Dependency"][region_code]:.2f}', 
                delta=f'{val_change[region_code]:.2f}', delta_color='off')
    
    st.header('Important indicators')
    col1, col2 = st.columns([0.35, 0.65])
    
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
            legend=dict(y=0.9, x=1.1),
            width=1100,
            height=690,
            # margin=dict(l=50, r=50, b=50, t=50)
        )
        st.plotly_chart(fig_1, theme="streamlit")


    with col2:        
        employment_pie_chart()  
    

    # st.header('Region-specific indices')
    # # Region-specific indices
    # chosen_indices = ['GDP relative growth (%)', 'Population relative growth (%)']
    # description = [('GDP relative growth (%)', 'GDP relative growth (%) is the percentage change in GDP compared to the previous year.'),
    #                ('Population relative growth (%)', 'Population relative growth (%) is the percentage change in population compared to the previous year.')]
    # description = pd.DataFrame.from_records(description, columns=['Index', 'Description'])
    # # Get chosen indices indexed by year
    # indices = chosen_region_data.set_index(['Year']).drop_duplicates().dropna(how='all').sort_values(['Year'])
    # indices.drop(columns=['Dominant Industry'], inplace=True) # Drop non-numeric index
    # vals_for_graphs = indices.to_dict(orient='list')
    # vals_for_graphs['Employment data pie chart'] = len(vals_for_graphs[indices.columns[0]]) * [0]
    # vals_for_graphs = {k : pd.Series(v).dropna().tolist() for k, v in vals_for_graphs.items()}
    # streamlit_table = pd.DataFrame({'Index' : indices.columns.to_list() + ["Employment data pie chart"]}).merge(description, on='Index', how='left')
    # config = {
    #     'Index' : st.column_config.TextColumn(disabled=True),
    #     'Description' : st.column_config.TextColumn(disabled=True),   
    #     'Selectbox' : st.column_config.CheckboxColumn(label="Choose index to graph", default=False, required=True),
    #     'Graph' : st.column_config.LineChartColumn(label='Graph of the index', y_min=0) 
    # }
    # streamlit_table['Selectbox'] = False
    # streamlit_table['Graph'] = vals_for_graphs.values()
    # streamlit_table = streamlit_table.copy()
    # streamlit_table = st.data_editor(streamlit_table, column_config=config)
    # chosen_ind = streamlit_table[streamlit_table['Selectbox'] == True]
    
    # def graph(index_to_graph):
    #     if index_to_graph != "Employment data pie chart":
    #         fig = go.Figure()
    #         ser = indices[index_to_graph].dropna()
    #         fig.add_trace(go.Scatter(x=ser.index, y=ser, name=index_to_graph))
    #         fig.update_layout(
    #             xaxis_title="Year",
    #             yaxis_title=index_to_graph,
    #             legend_title="Legend",
    #             width=1000,
    #             height=500,
    #              xaxis = dict(
    #                 tickmode = 'linear',
    #                 tick0 = ser.index.min(),
    #                 dtick = 1
    #             )
    #         )
    #         st.plotly_chart(fig)
    #     else:
    #         employment_pie_chart()
        

    # # Plot the region-specific indices if any chosen
    # if not chosen_ind.empty:
    #     graph(chosen_ind['Index'].iloc[-1])
    

    # give streamlit display a title
    # st.title("Information on Municipalities in Finland 2010-2021")

    # # create multiselection dropdown menus for user to choose municipality(s) and info(s) to display the graph(s)
    # option_municipality = st.multiselect(
    #     "Choose municipality",
    #     df_2010_2021["Region"].unique(),
    #     ["Espoo"],
    #     max_selections=3,
    # )
    # option_info_municipality = st.multiselect(
    #     "Choose information for the municipality",
    #     municipality_and_region_info_fields,
    #     ["Agriculture, forestry and fishing", "Mining and quarrying"],
    #     max_selections=3,
    # )

    # # ===============================================================
    # # Plot the line graph based on chosen municipality(s) and info(s)
    # # ===============================================================
    # combined_municipality_graph_list = []

    # for muni in option_municipality:
    #     for inf in option_info_municipality:
    #         result = df_2010_2021[df_2010_2021["Region"] == muni]
    #         result = result[result["Information"] == inf].reset_index(drop=True)
    #         x_axis = result.columns[2:]
    #         y_axis = result.loc[0][2:]
    #         combined_municipality_graph_list.append(
    #             go.Scatter(
    #                 mode="lines+markers", x=x_axis, y=y_axis, name=f"{inf} of {muni}"
    #             )
    #         )

    # if combined_municipality_graph_list:
    #     fig2 = go.Figure(data=combined_municipality_graph_list)
    #     fig2.update_layout(
    #         xaxis_title="year",
    #         yaxis_title="Number of people",
    #         legend_title="Legend Title",
    #         width=957,
    #         height=500,
    #     )
    #     st.plotly_chart(fig2)

    # else:
    #     st.write("Please choose at least 1 region and 1 information")

    # # ================================================================================
    # # Plot pie chart of industries distribution for each chosen municipalities in 2020
    # # ================================================================================
    # for muni in option_municipality:
    #     employed = df_2010_2021[
    #         (df_2010_2021["Region"] == muni)
    #         & (df_2010_2021["Information"].isin(option_industries))
    #     ]
    #     fig_2 = px.pie(
    #         employed,
    #         values="2020",
    #         names="Information",
    #         title=f"Industries distribution of {muni}",
    #         hover_name="Information",
    #     )
    #     fig_2.update_layout(
    #         legend=dict(y=0.9, x=1.1),
    #         width=1100,
    #         height=690,
    #         # margin=dict(l=50, r=50, b=50, t=50)
    #     )
    #     st.plotly_chart(fig_2, theme="streamlit")

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
        industry_list = st.multiselect("Choose industry", industry_dict.values(), ['Agriculture, forestry and fishing'], max_selections=3)

        index = st.selectbox("Choose index", [
            "Employment",
            "Export Value",
            "Import Value",
            "Trade Dependency",
            "Trade Imbalance",
            "Export Growth",
            "Import Growth",
        ])
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
            st.plotly_chart(combined_fig)
        else:
            st.write("Please choose at least 1 region and 1 information")

        
dashboard("MK01")