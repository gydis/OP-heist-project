import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import re

from menu_options import *

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
    return region_data, industry_ind, df_2010_2021, df_2011_2021

# Streamlit app
st.set_page_config(page_title="Other Obtained Data", page_icon="🗃️", layout="wide")
st.title("Finnish Region Data Visualization")


####################################
########## Tax Data ################
####################################
tax_df = pd.read_csv('./data/tax_data/tax_data_viz.csv')

region_data, industry_ind, df_2010_2021, df_2011_2021 = load_data()

# Sidebar for user input
selected_region = st.sidebar.selectbox("Select Region for Tax Data", 
                                        tax_df['Name of region in Finnish'].unique(), 
                                        index=tax_df['Name of region in Finnish'].unique().tolist().index('Uusimaa'))

region_code = region_data[region_data['Region name (fi)'] == selected_region]['Region code'].iloc[0]

# Tax Data Processing
selected_region_data = tax_df[tax_df['Name of region in Finnish'] == selected_region]
grouped_data = selected_region_data.groupby(['Year', 'Name of region in Finnish']).sum().reset_index()

# Tax Data Visualization
st.subheader(f"Tax Data Visualization for {selected_region}")

# Plotly Express Line Chart
fig_tax_data = px.line(grouped_data, x='Year', y=['Tax_Revenue', 'Total_Amount_Paid', 'Tax_Advance', 'Tax_Return', 'Residual_Tax'],
                       labels={'value': 'Amount'}, title='Tax Data Over Years',
                       line_dash_sequence=['solid', 'dash', 'dot', 'dashdot', 'solid'])

# Display line chart
st.plotly_chart(fig_tax_data)


# Filter data based on region code
chosen_region_data = region_data[region_data['Region code'] == region_code]
chosen_industry_ind = industry_ind[industry_ind['Region code'] == region_code]

# Drop columns with region name and code
chosen_region_data.drop(columns=['Region code', 'Region name (en)', 'Region name (fi)'], inplace=True)    

st.header('Region-specific indices')
# Region-specific indices
# Get chosen indices indexed by year
indices = chosen_region_data.set_index(['Year']).drop_duplicates().dropna(how='all').sort_values(['Year'])
indices.drop(columns=['Dominant Industry'], inplace=True) # Drop non-numeric index
vals_for_graphs = indices.to_dict(orient='list')
# vals_for_graphs['Employment data pie chart'] = len(vals_for_graphs[indices.columns[0]]) * [0]
vals_for_graphs = {k : pd.Series(v).dropna().tolist() for k, v in vals_for_graphs.items()}
streamlit_table = pd.DataFrame({'Index' : indices.columns.to_list()})
config = {
    'Index' : st.column_config.TextColumn(disabled=True),
    'Selectbox' : st.column_config.CheckboxColumn(label="Choose index to graph", default=False, required=True),
    'Graph' : st.column_config.LineChartColumn(label='Graph of the index', y_min=0) 
}
streamlit_table['Selectbox'] = False
streamlit_table['Graph'] = vals_for_graphs.values()
streamlit_table = streamlit_table.copy()
streamlit_table = st.data_editor(streamlit_table, column_config=config)
chosen_ind = streamlit_table[streamlit_table['Selectbox'] == True]

def graph(index_to_graph):
    if index_to_graph != "Employment data pie chart":
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
    else:
        employment_pie_chart()
    

# Plot the region-specific indices if any chosen
if not chosen_ind.empty:
    graph(chosen_ind['Index'].iloc[-1])
    
####################################
########## Industry Data ###########
####################################
industry_data = pd.read_csv("./data/combined/percent_ind_per_region_eng.csv", index_col=0)

# Sidebar for user input
selected_region_industry = st.sidebar.selectbox("Select Region for Industry Data", 
                                                industry_data['Area'], 
                                                index=industry_data['Area'].tolist().index('Uusimaa'))

# Industry Data Processing
selected_region_data = industry_data[industry_data['Area'] == selected_region_industry].drop('Area', axis=1)
selected_region_data = selected_region_data.melt(var_name='Industry', value_name='Proportion')

# Industry Data Visualization
st.subheader("Industry Proportion Visualization")
selected_region_data = selected_region_data.replace({'Industry' : industry_dict})
fig_industry = px.pie(selected_region_data, names='Industry', values='Proportion',
                      title=f'Industry Proportion for {selected_region_industry}')
st.plotly_chart(fig_industry, use_container_width=True)



#give streamlit display a title
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
    municipality_and_region_info_fields,
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


