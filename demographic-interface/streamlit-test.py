import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re

#read csv files
df_2010_2012 = pd.read_csv('./data/region_city_data/city_info_2010_2012.csv')
df_2013_2015 = pd.read_csv('./data/region_city_data/city_info_2013_2015.csv')
df_2016_2018 = pd.read_csv('./data/region_city_data/city_info_2016_2018.csv')
df_2019_2021 = pd.read_csv('./data/region_city_data/city_info_2019_2021.csv')
df_2011_2021 = pd.read_csv('./data/region_city_data/region_info_2011_2021.csv')

#remove redundant codes in the dataset of regions in Finland
df_2011_2021["Information"] = df_2011_2021["Information"].apply(lambda row: re.sub(r"(\([A-Z]+\)$)|(^[A-Z] )", "", row).strip())

#give streamlit display a title 
st.title('Information on Regions in Finland 2011-2021')
    
#create multiselection dropdown menus for user to choose region(s) and info(s) to display the graph(s)
option_region = st.multiselect('Choose region', df_2011_2021["Region"].unique(), ['MK01 Uusimaa'])
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
                                                    'Activities of extraterritorial organisations and bodies', 'Industry unknown', 'Employed', 'Workplaces, total'], 
                                                    ['Agriculture, forestry and fishing', 'Mining and quarrying'])

#plot the line graph based on chosen region(s) and info(s)
fig, ax = plt.subplots()

for reg in option_region:
    for inf in option_info_region:
        result = df_2011_2021[df_2011_2021["Region"] == reg]
        result = result[result["Information"] == inf].reset_index(drop=True)
        x_axis = result.columns[2:]
        y_axis = result.loc[0][2:]
        ax.plot(x_axis, y_axis, label=reg + ': ' + inf)

ax.legend(loc='upper right')
fig.text(0.5, 0.02, 'years', ha='center')
st.pyplot(fig)


#merge datasets of municipalities in Finland into a continuous timeline
df_2010_2015 = pd.merge(df_2010_2012, df_2013_2015, on=["Region", "Information"])
df_2010_2018 = pd.merge(df_2010_2015, df_2016_2018, on=["Region", "Information"])
df_2010_2021 = pd.merge(df_2010_2018, df_2019_2021, on=["Region", "Information"])

#remove redundant codes in the dataset of municipalities in Finland
df_2010_2021["Information"] = df_2011_2021["Information"].apply(lambda row: re.sub(r"(\([A-Z]+\)$)|(^[A-Z] )", "", row).strip())

#give streamlit display a title
st.title('Information on Municipalities in Finland 2010-2021')
    
#create multiselection dropdown menus for user to choose municipality(s) and info(s) to display the graph(s)
option_municipality = st.multiselect('Choose municipality', df_2010_2021["Region"].unique(), ['Espoo'])
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
                                                    'Activities of extraterritorial organisations and bodies', 'Industry unknown', 'Employed', 'Workplaces, total'], 
                                                    ['Agriculture, forestry and fishing', 'Mining and quarrying'])

#plot the line graph based on chosen municipality(s) and info(s)
fig, ax = plt.subplots()

for muni in option_municipality:
    for inf in option_info_municipality:
        result = df_2010_2021[df_2010_2021["Region"] == muni]
        result = result[result["Information"] == inf].reset_index(drop=True)
        x_axis = result.columns[2:]
        y_axis = result.loc[0][2:]
        ax.plot(x_axis, y_axis, label=muni + ': ' + inf)

ax.legend(loc='upper right')
fig.text(0.5, 0.02, 'years', ha='center')
st.pyplot(fig)