# -*- coding: utf-8 -*-
"""covidEDA.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/14DaNRo2-B1eY0_AbXmnJ4zLetvmnfw1j
"""

ls

# Install required library
!pip3 install calmap
!pip3 install bar_chart_race
!pip3 install pywaffle
!pip3 install folium
!pip install geopandas
!pip install --upgrade plotly

# Commented out IPython magic to ensure Python compatibility.
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
import calmap
from datetime import datetime
import json
import requests
plt.style.use('fivethirtyeight')
# %matplotlib inline

#bar chart race
import bar_chart_race as bcr

# Waffle Chart
from pywaffle import Waffle

# plotly
import plotly.express as px
import plotly.graph_objs as go
import plotly.figure_factory as ff
from plotly.subplots import make_subplots

#geopandas
import geopandas as gpd

#folium
import folium

# color pallette
cnf, dth, rec, act = '#393e46', '#ff2e63', '#21bf73', '#fe9801'

import warnings
warnings.filterwarnings("ignore")

import os

covid_19_india = pd.read_csv('covid_19_india.csv')

covid_19_india = covid_19_india.drop(['Sno','Time','ConfirmedIndianNational', 'ConfirmedForeignNational'], axis=1)
covid_19_india = covid_19_india.rename(columns={'State/UnionTerritory':'States','Cured':'Recovered'})

covid_19_india['Active'] = covid_19_india['Confirmed'] - covid_19_india['Recovered'] - covid_19_india['Deaths']
covid_19_india = covid_19_india.sort_values(['Date', 'States']).reset_index(drop=True)

covid_19_india['Date'] = pd.to_datetime(covid_19_india['Date'])

print(covid_19_india)

india_wise_cases = covid_19_india[covid_19_india['Date'] == covid_19_india['Date'].max()].copy().fillna(0)
india_wise_cases.index = india_wise_cases["States"]
india_wise_cases = india_wise_cases.drop(['States', 'Date'], axis=1)

df = pd.DataFrame(pd.to_numeric(india_wise_cases.sum()),dtype=np.float64).transpose()
df.style.background_gradient(cmap='PuBu',axis=1)

df_last_date = covid_19_india[covid_19_india['Date'] == covid_19_india['Date'].max()]
temp = df_last_date.groupby('Date')['Confirmed', 'Deaths', 'Recovered', 'Active'].sum().reset_index()
temp = temp.reset_index(drop=True)


tm = temp.melt(id_vars="Date", value_vars=['Active', 'Deaths', 'Recovered'])
fig = px.treemap(tm, path=["variable"], values="value", height=225, width=700,color_discrete_sequence=[act, rec, dth])
fig.data[0].textinfo = 'label+value'
fig.show()

india_wise_cases.sort_values('Confirmed', ascending= False).style\
    .background_gradient(cmap='BrBG_r', subset=['Confirmed'])\
    .background_gradient(cmap='YlGn_r', subset=["Deaths"])\
    .background_gradient(cmap='YlOrBr',subset=['Recovered'])\
    .background_gradient(cmap='summer_r', subset=['Active'])

full_latest = covid_19_india[covid_19_india['Date'] == max(covid_19_india['Date'])]

print(full_latest)

fig = px.treemap(full_latest.sort_values(by='Confirmed', ascending=False).reset_index(drop=True), path=["States"], values="Confirmed", height=700, title='Total Confirmed Cases')
fig.data[0].textinfo = 'label+text+value'
fig.show()

unique_states = covid_19_india['States'].unique()
plt.style.use("seaborn-talk")

# Get last date to see which states have the most cases currently
last_date = covid_19_india['Date'].max()
df_last_date = covid_19_india[covid_19_india['Date'] == last_date]
series_last_date = df_last_date.groupby('States')['Confirmed'].sum().sort_values(ascending=False)

labels = []
values = []
state_count = 5
other_total = 0
for state in series_last_date.index:
    if state_count > 0:
        labels.append(state)
        values.append(series_last_date[state])
        state_count -= 1
    else:
        other_total += series_last_date[state]
labels.append("Other")
values.append(other_total)

wedge_dict = {
    'edgecolor': 'black',
    'linewidth': 2        
}

explode = (0, 0.1, 0, 0, 0, 0)
fig = plt.figure(figsize=(15,9))
plt.title(f"Total Cases on {last_date}")
plt.pie(values, labels=labels, explode=explode, autopct='%1.1f%%', wedgeprops=wedge_dict)
plt.show()

fp = 'Indian_States.shp'
map_df = gpd.read_file(fp, encoding="utf-8")

print(map_df.head(24))

# change state name to match in both files -- Manually checking
map_df['st_nm'].iloc[0]  = 'Andaman and Nicobar Islands'
map_df['st_nm'].iloc[12] = 'Jammu and Kashmir'
map_df['st_nm'].iloc[6] = 'Dadara and Nagar Havelli'
map_df['st_nm'].iloc[23] = 'Delhi'

print(map_df.head())

merged = map_df.set_index('st_nm').join(covid_19_india.set_index('States'))

#fill NaN values with Zero

merged[['Confirmed', 'Recovered', 'Deaths']] = merged[['Confirmed', 'Recovered', 'Deaths']].fillna(0).astype('int')

fig, ax = plt.subplots(1, figsize=(23, 19))
ax.axis('on')
ax.set_title('Total COVID-19 cases in India', fontdict={'fontsize': '35', 'fontweight' : '5'})

# plot the figure
merged.plot(column='Confirmed', cmap='Oranges', linewidth=0.8, ax=ax, edgecolor='0.8', legend=True)



# Save the output as a PNG image
#fig.savefig("TotalCase_India.png", dpi=100)

# create figure and axes for Matplotlib and set the title
fig, ax = plt.subplots(1, figsize=(23, 19))
ax.axis('on')
ax.set_title('Total Deaths due to COVID-19 in India', fontdict={'fontsize': '35', 'fontweight' : '5'})

# plot the figure
merged.plot(column='Deaths', cmap='Blues', linewidth=0.8, ax=ax, edgecolor='0.8', legend=True)


# Save the output as a PNG image
#fig.savefig("TotalDeath_India.png", dpi=100)

