import streamlit as st
import pandas as pd
import plotly.express as px


# Streamlit app
st.title("Finnish Region Data Visualization")


####################################
########## Tax Data ################
####################################
tax_df = pd.read_csv('./data/tax_data/tax_data_viz.csv')

# Sidebar for user input
selected_region = st.sidebar.selectbox("Select Region for Tax Data", 
                                        tax_df['Name of region in Finnish'].unique(), 
                                        index=tax_df['Name of region in Finnish'].unique().tolist().index('Uusimaa'))

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
fig_industry = px.pie(selected_region_data, names='Industry', values='Proportion',
                      title=f'Industry Proportion for {selected_region_industry}')
st.plotly_chart(fig_industry)
