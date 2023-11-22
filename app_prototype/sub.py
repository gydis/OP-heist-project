#File for the region specific dashboard
import streamlit as st
import pandas as pd
import numpy as np
import re
import plotly.express as px
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(layout="wide")

@st.cache_data
def load_data():
    education_ind = pd.read_csv(r'./data/Indices/education_attainment_index.csv')
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
    return region_data, industry_ind, df_2010_2021, df_2011_2021

def dashboard(region_code):
    st.title('Region-specific dashboard')
    region_data, industry_ind, df_2010_2021, df_2011_2021 = load_data()
    
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
    region_name = chosen_region_data['Region name (en)'].unique()[0]
    # Drop columns with region name and code
    chosen_region_data.drop(columns=['Region name (en)', 'Region name (fi)', 'Region code'], inplace=True)
    
    # Print out region name
    st.header(f'Region name: {region_name}')

    # Print out region-specific indices
    # st.write(chosen_region_data.set_index(['Year']).sort_values('Year'))
    # Print out industry-specific indices
    # st.write(chosen_industry_ind)
    
    # Regional trade dependency ranking and value
    last_trade_dep = region_data.set_index(['Region code'])[['Year', 'Regional trade dependency']].dropna().sort_values('Year').groupby('Region code').tail(1)
    last_trade_dep['rank'] = last_trade_dep['Regional trade dependency'].rank(ascending=False, method='first')
    chosen_region_trade_rank = last_trade_dep.loc[region_code, 'rank']
    chosen_region_trade_value = last_trade_dep.loc[region_code, 'Regional trade dependency']
    
    st.write(f"Regional trade dependency rank: #{int(chosen_region_trade_rank)}")
    st.write(f"Trade dependency value: {chosen_region_trade_value:.2f}")

    st.subheader('Region-specific indices')
    # Region-specific indices
    chosen_indices = ['GDP relative growth (%)', 'Population relative growth (%)']
    description = [('GDP relative growth (%)', 'GDP relative growth (%) is the percentage change in GDP compared to the previous year.'),
                   ('Population relative growth (%)', 'Population relative growth (%) is the percentage change in population compared to the previous year.')]
    description = pd.DataFrame.from_records(description, columns=['Index', 'Description'])
    # Get chosen indices indexed by year
    indices = chosen_region_data.set_index(['Year']).drop_duplicates().dropna(how='all').sort_values(['Year'])
    indices.drop(columns=['Dominant Industry'], inplace=True) # Drop non-numeric index
    vals_for_graphs = indices.to_dict(orient='list')
    vals_for_graphs = {k : pd.Series(v).dropna().tolist() for k, v in vals_for_graphs.items()}
    streamlit_table = pd.DataFrame({'Index' : indices.columns.to_list()}).merge(description, on='Index', how='left')
    config = {
        'Index' : st.column_config.TextColumn(disabled=True),
        'Description' : st.column_config.TextColumn(disabled=True),   
        'Selectbox' : st.column_config.CheckboxColumn(label="Choose index to graph", default=False, required=True),
        'Graph' : st.column_config.LineChartColumn(label='Graph of the index', y_min=0) 
    }
    streamlit_table['Selectbox'] = False
    streamlit_table['Graph'] = vals_for_graphs.values()
    streamlit_table = streamlit_table.copy()
    streamlit_table = st.data_editor(streamlit_table, column_config=config)
    chosen_ind = streamlit_table[streamlit_table['Selectbox'] == True]
    
    def graph(index_to_graph):
        fig = go.Figure()
        ser = indices[index_to_graph].dropna()
        fig.add_trace(go.Scatter(x=ser.index, y=ser, name=index_to_graph))
        fig.update_layout(
            xaxis_title="Year",
            yaxis_title=index_to_graph,
            legend_title="Legend",
            width=1000,
            height=500,
             xaxis = dict(
                tickmode = 'linear',
                tick0 = ser.index.min(),
                dtick = 1
            )
        )
        st.plotly_chart(fig)
    
    if not chosen_ind.empty:
        graph(chosen_ind['Index'].iloc[-1])
    
    option_info_region = st.multiselect(
        "Choose information for the region",
        [
            "Inhabitants, total",
            "Agriculture, forestry and fishing",
            "Mining and quarrying",
            "Manufacturing",
            "Electricity, gas, steam and air conditioning supply",
            "Water supply; sewerage, waste management and remediation activities",
            "Construction",
            "Wholesale and retail trade; repair of motor vehicles and motorcycles",
            "Transportation and storage",
            "Accommodation and food service activities",
            "Information and communication",
            "Financial and insurance activities",
            "Real estate activities",
            "Professional, scientific and technical activities",
            "Administrative and support service activities",
            "Public administration and defence; compulsory social security",
            "Education",
            "Human health and social work activities",
            "Arts, entertainment and recreation",
            "Other service activities",
            "Activities of households as employers; undifferentiated goods- and services-producing activities of households for own use",
            "Activities of extraterritorial organisations and bodies",
            "Employed",
            "Workplaces, total",
        ],
        ["Agriculture, forestry and fishing", "Mining and quarrying"],
        max_selections=3,
    )

    # =========================================================
    # Plot the line graph based on chosen region(s) and info(s)
    # =========================================================
    combined_region_graph_list = []

    for inf in option_info_region:
        result = df_2011_2021[df_2011_2021["Region"] == option_region]
        result = result[result["Information"] == inf].reset_index(drop=True)
        x_axis = result.columns[2:]
        y_axis = result.loc[0][2:]
        combined_region_graph_list.append(
            go.Scatter(
                mode="lines+markers", x=x_axis, y=y_axis, name=f"{inf} of {option_region}"
            )
        )

    if combined_region_graph_list:
        fig1 = go.Figure(data=combined_region_graph_list)
        fig1.update_layout(
            xaxis_title="Year",
            yaxis_title="Number of people",
            legend_title="Legend Title",
            width=1000,
            height=500,
        )
        st.plotly_chart(fig1)

    else:
        st.write("Please choose at least 1 region and 1 information")

    # =========================================================================
    # Plot pie chart of industries distribution for each chosen regions in 2020
    # =========================================================================
    option_industries = [
        "Agriculture, forestry and fishing",
        "Mining and quarrying",
        "Manufacturing",
        "Electricity, gas, steam and air conditioning supply",
        "Water supply; sewerage, waste management and remediation activities",
        "Construction",
        "Wholesale and retail trade; repair of motor vehicles and motorcycles",
        "Transportation and storage",
        "Accommodation and food service activities",
        "Information and communication",
        "Financial and insurance activities",
        "Real estate activities",
        "Professional, scientific and technical activities",
        "Administrative and support service activities",
        "Public administration and defence; compulsory social security",
        "Education",
        "Human health and social work activities",
        "Arts, entertainment and recreation",
        "Other service activities",
        "Activities of households as employers; undifferentiated goods- and services-producing activities of households for own use",
        "Activities of extraterritorial organisations and bodies",
        "Industry unknown",
    ]
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

    # give streamlit display a title
    st.title("Information on Municipalities in Finland 2010-2021")

    # create multiselection dropdown menus for user to choose municipality(s) and info(s) to display the graph(s)
    option_municipality = st.multiselect(
        "Choose municipality",
        df_2010_2021["Region"].unique(),
        ["Espoo"],
        max_selections=3,
    )
    option_info_municipality = st.multiselect(
        "Choose information for the municipality",
        [
            "Inhabitants, total",
            "Agriculture, forestry and fishing",
            "Mining and quarrying",
            "Manufacturing",
            "Electricity, gas, steam and air conditioning supply",
            "Water supply; sewerage, waste management and remediation activities",
            "Construction",
            "Wholesale and retail trade; repair of motor vehicles and motorcycles",
            "Transportation and storage",
            "Accommodation and food service activities",
            "Information and communication",
            "Financial and insurance activities",
            "Real estate activities",
            "Professional, scientific and technical activities",
            "Administrative and support service activities",
            "Public administration and defence; compulsory social security",
            "Education",
            "Human health and social work activities",
            "Arts, entertainment and recreation",
            "Other service activities",
            "Activities of households as employers; undifferentiated goods- and services-producing activities of households for own use",
            "Activities of extraterritorial organisations and bodies",
            "Employed",
            "Workplaces, total",
        ],
        ["Agriculture, forestry and fishing", "Mining and quarrying"],
        max_selections=3,
    )

    # ===============================================================
    # Plot the line graph based on chosen municipality(s) and info(s)
    # ===============================================================
    combined_municipality_graph_list = []

    for muni in option_municipality:
        for inf in option_info_municipality:
            result = df_2010_2021[df_2010_2021["Region"] == muni]
            result = result[result["Information"] == inf].reset_index(drop=True)
            x_axis = result.columns[2:]
            y_axis = result.loc[0][2:]
            combined_municipality_graph_list.append(
                go.Scatter(
                    mode="lines+markers", x=x_axis, y=y_axis, name=f"{inf} of {muni}"
                )
            )

    if combined_municipality_graph_list:
        fig2 = go.Figure(data=combined_municipality_graph_list)
        fig2.update_layout(
            xaxis_title="year",
            yaxis_title="Number of people",
            legend_title="Legend Title",
            width=957,
            height=500,
        )
        st.plotly_chart(fig2)

    else:
        st.write("Please choose at least 1 region and 1 information")

    # ================================================================================
    # Plot pie chart of industries distribution for each chosen municipalities in 2020
    # ================================================================================
    for muni in option_municipality:
        employed = df_2010_2021[
            (df_2010_2021["Region"] == muni)
            & (df_2010_2021["Information"].isin(option_industries))
        ]
        fig_2 = px.pie(
            employed,
            values="2020",
            names="Information",
            title=f"Industries distribution of {muni}",
            hover_name="Information",
        )
        fig_2.update_layout(
            legend=dict(y=0.9, x=1.1),
            width=1100,
            height=690,
            # margin=dict(l=50, r=50, b=50, t=50)
        )
        st.plotly_chart(fig_2, theme="streamlit")

    # ==================================================================
    # Plot line graph of a chosen index of a chosen industry 2015 - 2020
    # ==================================================================
    st.title("Index of Industry in Region")

    industry_dict = {
        "A": "Agriculture, forestry and fishing",
        "B": "Mining and quarrying",
        "C": "Manufacturing",
        "D": "Electricity, gas, steam and air conditioning supply",
        "E": "Water supply; sewerage, waste management and remediation activities",
        "F": "Construction",
        "G": "Wholesale and retail trade; repair of motor vehicles and motorcycles",
        "H": "Transportation and storage",
        "I": "Accommodation and food service activities",
        "J": "Information and communication",
        "K": "Financial and insurance activities",
        "L": "Real estate activities",
        "M": "Professional, scientific and technical activities",
        "N": "Administrative and support service activities",
        "O": "Public administration and defence; compulsory social security",
        "P": "Education",
        "Q": "Human health and social work activities",
        "R": "Arts, entertainment and recreation",
        "S": "Other service activities",
        "T": "Activities of households as employers; undifferentiated goods- and services-producing activities of households for own use",
        "U": "Activities of extraterritorial organisations and bodies",
    }
    industry_ind_new = industry_ind[(industry_ind['Industry'] != 'Industry Unknown')]
    industry_ind_new = industry_ind_new[industry_ind_new['Region code'] == option_region.split()[0]].drop_duplicates()
    industry_ind_new['Industry'] = industry_ind_new['Industry'].apply(lambda row: industry_dict[row])

    col1, col2 = st.columns([0.4, 0.6], gap="large")
    index = "Export"
    with col1:
        industry = st.selectbox("Choose industry", industry_dict.values())

        index = st.selectbox("Choose index", [
            "Export",
            "Import",
            "Industry trade dependency",
            "Import-Export imbalance",
            "Export Growth",
            "Import Growth",
        ])
        st.caption("Display from year 2015 to 2020")

    with col2:
        industry_ind_plot = industry_ind_new[industry_ind_new['Industry'] == industry]
        industry_ind_plot = industry_ind_plot[["Year", index]]
        fig = px.line(industry_ind_plot, x="Year", y=index, title=f"{index} of {industry} of {option_region}")
        st.plotly_chart(fig, theme="streamlit")

        
#dashboard("MK01")