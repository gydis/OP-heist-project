#File for the region specific dashboard
import streamlit as st
import pandas as pd
import numpy as np
import re
import plotly.express as px
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(layout="wide")

def load_data():
    education_ind = pd.read_csv(r'./data/Indices/education_attainment_index.csv')
    gdp_region_ind = pd.read_csv(r'./data/Indices/gdp_region_index.csv')
    industry_ind = pd.read_csv(r'./data/Indices/industries_indexes.csv', index_col=0)
    industry_ind.reset_index(drop=True, inplace=True)
    population_den = pd.read_csv(r'./data/Indices/population_density_index.csv')
    region_ind = pd.read_csv(r'./data/Indices/regional_indexes.csv')
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
    
    # Return region-specific indices and industry-specific separately
    return region_data, industry_ind

def dashboard(region_code):
    st.title('Region-specific dashboard')
    region_data, industry_ind = load_data()
    # Filter data based on region code
    chosen_region_data = region_data[region_data['Region code'] == region_code]
    chosen_industry_ind = industry_ind[industry_ind['Region code'] == region_code]
    # Print out region name
    region_name = chosen_region_data['Region name (en)'].unique()[0]
    st.header(f'Region name: {region_name}')
    # Print out region-specific indices
    #st.write(chosen_region_data)
    # Print out industry-specific indices
    #st.write(chosen_industry_ind)
    
    # Regional trade dependency ranking and value
    last_trade_dep = region_data.set_index(['Region code'])[['Year', 'Regional trade dependency']].dropna().sort_values('Year').groupby('Region code').tail(1)
    last_trade_dep['rank'] = last_trade_dep['Regional trade dependency'].rank(ascending=False, method='first')
    chosen_region_trade_rank = last_trade_dep.loc[region_code, 'rank']
    chosen_region_trade_value = last_trade_dep.loc[region_code, 'Regional trade dependency']
    
    st.write(f"Regional trade dependency rank: {int(chosen_region_trade_rank)}")
    st.write(f"Trade dependency value: {chosen_region_trade_value}")
    
    # Display chosen indices
    chosen_indices = ['GDP relative growth (%)', 'Population relative growth (%)']
    
    idx = pd.IndexSlice
    indices = chosen_region_data.set_index(['Year'])[chosen_indices].stack().swaplevel().sort_index().drop_duplicates().loc[idx[:, -1]]
    st.write(indices)
    
    #read csv files for demographic info
    df_2010_2012 = pd.read_csv('./data/region_city_data/city_info_2010_2012.csv')
    df_2013_2015 = pd.read_csv('./data/region_city_data/city_info_2013_2015.csv')
    df_2016_2018 = pd.read_csv('./data/region_city_data/city_info_2016_2018.csv')
    df_2019_2021 = pd.read_csv('./data/region_city_data/city_info_2019_2021.csv')
    df_2011_2021 = pd.read_csv('./data/region_city_data/region_info_2011_2021.csv')

    #remove redundant codes in the dataset of regions in Finland
    df_2011_2021["Information"] = df_2011_2021["Information"].apply(lambda row: re.sub(r"(\([A-Z]+\)$)|(^[A-Z] )", "", row).strip())
        
#create multiselection dropdown menus for user to choose region(s) and info(s) to display the graph(s)
    option_region = st.multiselect('Choose region', df_2011_2021["Region"].unique(), ['MK01 Uusimaa'], max_selections=3)
    option_info_region = st.multiselect('Choose information for the region', ['Inhabitants, total', 'Agriculture, forestry and fishing', 'Mining and quarrying', 
                                                        'Manufacturing', 'Electricity, gas, steam and air conditioning supply', 
                                                        'Water supply; sewerage, waste management and remediation activities', 
                                                        'Construction', 'Wholesale and retail trade; repair of motor vehicles and motorcycles', 
                                                        'Transportation and storage', 'Accommodation and food service activities', 
                                                        'Information and communication', 'Financial and insurance activities', 
                                                        'Real estate activities', 'Professional, scientific and technical activities', 
                                                        'Administrative and support service activities', 'Public administration and defence; compulsory social security', 
                                                        'Education', 'Human health and social work activities', 
                                                        'Arts, entertainment and recreation', 'Other service activities', 
                                                        'Activities of households as employers; undifferentiated goods- and services-producing activities of households for own use', 
                                                        'Activities of extraterritorial organisations and bodies', 'Employed', 'Workplaces, total'], 
                                                        ['Agriculture, forestry and fishing', 'Mining and quarrying'], max_selections=3)

#plot the line graph based on chosen region(s) and info(s)
    combined_region_graph_list = []

    for reg in option_region:
        for inf in option_info_region:
            result = df_2011_2021[df_2011_2021["Region"] == reg]
            result = result[result["Information"] == inf].reset_index(drop=True)
            x_axis = result.columns[2:]
            y_axis = result.loc[0][2:]
            combined_region_graph_list.append(go.Scatter(mode="lines+markers", x=x_axis, y=y_axis, name=f"{inf} of {reg}"))

    if combined_region_graph_list:
        fig1 = go.Figure(data = combined_region_graph_list)

        fig1.update_layout(
        xaxis_title="Year",
        yaxis_title="Number of people",
        legend_title="Legend Title",
        width=1000,
        height=500
        )

        st.plotly_chart(fig1)
    else:
        st.write("Please choose at least 1 region and 1 information")

#plot pie chart of industries distribution for each chosen regions in 2020
    option_industries = ['Agriculture, forestry and fishing', 'Mining and quarrying', 
                                                        'Manufacturing', 'Electricity, gas, steam and air conditioning supply', 
                                                        'Water supply; sewerage, waste management and remediation activities', 
                                                        'Construction', 'Wholesale and retail trade; repair of motor vehicles and motorcycles', 
                                                        'Transportation and storage', 'Accommodation and food service activities', 
                                                        'Information and communication', 'Financial and insurance activities', 
                                                        'Real estate activities', 'Professional, scientific and technical activities', 
                                                        'Administrative and support service activities', 'Public administration and defence; compulsory social security', 
                                                        'Education', 'Human health and social work activities', 
                                                        'Arts, entertainment and recreation', 'Other service activities', 
                                                        'Activities of households as employers; undifferentiated goods- and services-producing activities of households for own use', 
                                                        'Activities of extraterritorial organisations and bodies', 'Industry unknown']
    for reg in option_region:
        employed = df_2011_2021[(df_2011_2021["Region"] == reg) & (df_2011_2021["Information"].isin(option_industries))]
        fig_1 = px.pie(employed, values='2020', names='Information', title=f"Industries distribution of {reg}", hover_name='Information')
        fig_1.update_layout(
            legend=dict(y=0.9, x=1.1),
            width=1100,
            height=690,
            # margin=dict(l=50, r=50, b=50, t=50)
        )
        st.plotly_chart(fig_1, theme="streamlit")

#merge datasets of municipalities in Finland into a continuous timeline
    df_2010_2015 = pd.merge(df_2010_2012, df_2013_2015, on=["Region", "Information"])
    df_2010_2018 = pd.merge(df_2010_2015, df_2016_2018, on=["Region", "Information"])
    df_2010_2021 = pd.merge(df_2010_2018, df_2019_2021, on=["Region", "Information"])

#remove redundant codes in the dataset of municipalities in Finland
    df_2010_2021["Information"] = df_2011_2021["Information"].apply(lambda row: re.sub(r"(\([A-Z]+\)$)|(^[A-Z] )", "", row).strip())

#give streamlit display a title
    st.title('Information on Municipalities in Finland 2010-2021')
        
#create multiselection dropdown menus for user to choose municipality(s) and info(s) to display the graph(s)
    option_municipality = st.multiselect('Choose municipality', df_2010_2021["Region"].unique(), ['Espoo'], max_selections=3)
    option_info_municipality = st.multiselect('Choose information for the municipality', ['Inhabitants, total', 'Agriculture, forestry and fishing', 'Mining and quarrying', 
                                                        'Manufacturing', 'Electricity, gas, steam and air conditioning supply', 
                                                        'Water supply; sewerage, waste management and remediation activities', 
                                                        'Construction', 'Wholesale and retail trade; repair of motor vehicles and motorcycles', 
                                                        'Transportation and storage', 'Accommodation and food service activities', 
                                                        'Information and communication', 'Financial and insurance activities', 
                                                        'Real estate activities', 'Professional, scientific and technical activities', 
                                                        'Administrative and support service activities', 'Public administration and defence; compulsory social security', 
                                                        'Education', 'Human health and social work activities', 
                                                        'Arts, entertainment and recreation', 'Other service activities', 
                                                        'Activities of households as employers; undifferentiated goods- and services-producing activities of households for own use', 
                                                        'Activities of extraterritorial organisations and bodies', 'Employed', 'Workplaces, total'], 
                                                        ['Agriculture, forestry and fishing', 'Mining and quarrying'], max_selections=3)

#plot the line graph based on chosen municipality(s) and info(s)
    combined_municipality_graph_list = []

    for muni in option_municipality:
        for inf in option_info_municipality:
            result = df_2010_2021[df_2010_2021["Region"] == muni]
            result = result[result["Information"] == inf].reset_index(drop=True)
            x_axis = result.columns[2:]
            y_axis = result.loc[0][2:]
            combined_municipality_graph_list.append(go.Scatter(mode="lines+markers", x=x_axis, y=y_axis, name=f"{inf} of {muni}"))

    if combined_municipality_graph_list:

        fig2 = go.Figure(data = combined_municipality_graph_list)

        fig2.update_layout(
            xaxis_title="year",
            yaxis_title="Number of people",
            legend_title="Legend Title",
            width=957,
            height=500
        )
        st.plotly_chart(fig2)
    else:
        st.write("Please choose at least 1 region and 1 information")

# plot pie chart of industries distribution for each chosen municipalities in 2020
# option_industries = ['Agriculture, forestry and fishing', 'Mining and quarrying', 
#                                                     'Manufacturing', 'Electricity, gas, steam and air conditioning supply', 
#                                                     'Water supply; sewerage, waste management and remediation activities', 
#                                                     'Construction', 'Wholesale and retail trade; repair of motor vehicles and motorcycles', 
#                                                     'Transportation and storage', 'Accommodation and food service activities', 
#                                                     'Information and communication', 'Financial and insurance activities', 
#                                                     'Real estate activities', 'Professional, scientific and technical activities', 
#                                                     'Administrative and support service activities', 'Public administration and defence; compulsory social security', 
#                                                     'Education', 'Human health and social work activities', 
#                                                     'Arts, entertainment and recreation', 'Other service activities', 
#                                                     'Activities of households as employers; undifferentiated goods- and services-producing activities of households for own use', 
#                                                     'Activities of extraterritorial organisations and bodies', 'Industry unknown']
    for muni in option_municipality:
        employed = df_2010_2021[(df_2010_2021["Region"] == muni) & (df_2010_2021["Information"].isin(option_industries))]
        fig_2 = px.pie(employed, values='2020', names='Information', title=f"Industries distribution of {muni}", hover_name='Information')
        fig_2.update_layout(
            legend=dict(y=0.9, x=1.1),
            width=1100,
            height=690,
            # margin=dict(l=50, r=50, b=50, t=50)
        )
        st.plotly_chart(fig_2, theme="streamlit")


dashboard('MK01')


