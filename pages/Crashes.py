import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils import aggregate_columns, find_crash_counts
import random
import json
import numpy as np
from plot_creator import PlotMaker


st.set_page_config(layout="wide")


# LOAD THE DATASET
df = pd.read_parquet('Processed_dataset/Crash_data_new.parquet')

# Read the CSS colours values
with open('Colours_list_real.txt', 'r') as file:
    values = file.readlines()
    CSS_colours = [value.strip() for value in values]
    
# For the continous colour scales (for heatmaps)
continuous_colours = px.colors.named_colorscales()
continuous_colours.sort()

# Find the index of the default scale - "Jet"
heatmap_colour_default = continuous_colours.index('jet')

with st.sidebar:
    colour_choice = st.selectbox(
        label='Use CSS colours or hex colours?',
        options=['CSS', 'Hex'],
        index=0
    )
    if colour_choice == 'Hex':
        plot_colour = st.color_picker(label='Colour to be used in the plots')
    else:
        plot_colour = st.selectbox(
            label='Select the plot colour',
            options=CSS_colours
        )
    heatmap_colour = st.selectbox(
        label='Select the colour scale for heatmaps',
        options=continuous_colours,
        index=heatmap_colour_default
    )
    figure_height = st.slider(
        label='Select the figure heights',
        min_value=400, max_value=800,
        value=500,
        step=50
    )
        
# Set up the colours
template = go.layout.Template()
template.layout.font.color = 'white'
template.layout.paper_bgcolor = '#1E1E1E'
px.defaults.template = template

st.markdown('## Apply the filters you want')
col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
# col1, col2 = st.columns(2)
with col1:
    country_filter = st.checkbox(label='Country', value=False)
with col2:
    continent_filter = st.checkbox(label='Continent', value=False)
with col3:
    year_filter = st.checkbox(label='Year', value=False)
with col4:
    month_filter = st.checkbox(label='Month', value=False)
with col5:
    day_filter = st.checkbox(label='Day of week', value=False)
with col6:
    day_num_filter = st.checkbox(label='Day', value=False)
with col7:
    decade_filter = st.checkbox(label='Decade', value=False)

# Create the options for the selectboxes
df['Continent'] = df['Continent'].fillna(value='Unknown')
country_list = sorted(df['Country'].unique())
continent_list = sorted(df['Continent'].unique())
selected_country, selected_continent = False, False

if country_filter:
    selected_country = st.selectbox(label='Select the country', options=country_list)
    df = df.query("Country in @selected_country")
if continent_filter:
    selected_continent = st.selectbox(label='Select the continent', options=continent_list)
    df = df.query('Continent in @selected_continent')


# Make the plotter object.
obj = PlotMaker(df=df, measure='Crashes', agg_func=None, continuous_colour=heatmap_colour, discrete_colour=plot_colour)

st.markdown('# Number of crashes')

obj.draw_line_plot(grouping_col=df['Date'].dt.year, title='Per year', date_name='Year', size=[None, figure_height])

# Make tabs for month, day of week, day number and time of day
st.markdown('## By date or time')
month_tab, day_tab, day_num_tab, time_tab = st.tabs([
    'Month', 'Day of week', 'Day number', 'Time of day'
])
with month_tab:
    obj.draw_histogram(grouping_col='Month', title='Per month', nbins=12, date_name=None, size=[None, figure_height])
with day_tab:
    obj.draw_histogram(grouping_col='Day_of_week', title='Per day', nbins=7, date_name=None, size=[None, figure_height])
with day_num_tab:
    obj.draw_histogram(grouping_col=df['Date'].dt.day, nbins=31, title='Per day number', date_name='Day', size=[None, figure_height])
with time_tab:
    obj.draw_time_histogram(nbins=24*2, title='Time of day', size=[None, figure_height])

# Create a worldmap only if all an individual country is not selected
if not selected_country:
    st.markdown('## Crashes throughout the world')
    us_exclude_flag = st.checkbox('Exclude the US from world map?')
    obj.draw_world_map(us_exclude_flag=us_exclude_flag, grouping_col='Country', title='Crashes throughout the world')

# Show the map of US only if all countries are selected or North America has been selected.
if selected_country == 'United States of America' or selected_continent == 'North America':
    st.markdown('## Crashes throughout the US states')
    obj.draw_US_map(title='Crashes throughout the US')

# Create heatmaps based on two conditions:
# If NONE of the date filters are applied, show the heatmaps.
# If even a single date filter is applied, DO NOT show the heatmaps.
date_filters = [year_filter, month_filter, day_filter, day_num_filter]
condition = all(date_filters) or not any(date_filters)
if condition:
    st.markdown('## Heatmaps')
    year_month, month_day, month_day_number = st.tabs([
        'Year and month', 'Month and day', 'Month and day number'
    ])
    with year_month:
        obj.draw_heatmap_year_month(title='Year and month', size=[None, figure_height])
    with month_day:
        obj.make_heatmap_month_day(title='Month and day', size=[None, figure_height])
    with month_day_number:
        obj.make_heatmap_month_day_number(title='Month and day number', size=[None, figure_height])
    # obj.draw_heatmap(grouping_cols=['Continent', 'Month'], date_name=None, size=[None, figure_height], title='Crashes by month and day number')

