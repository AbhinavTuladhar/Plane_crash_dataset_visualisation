import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils import aggregate_columns, find_crash_counts
import random

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
        index=1
    )
    if colour_choice == 'Hex':
        background_colour = st.color_picker(label='Background colour of the plots')
        plot_colour = st.color_picker(label='Colour to be used in the plots')
    else:
        background_colour = st.selectbox(
            label='Select the background colour',
            options=CSS_colours
        )
        plot_colour = st.selectbox(
            label='Select the plot colour',
            options=CSS_colours
        )
    heatmap_colour = st.selectbox(
        label='Select the colour scale for heatmaps',
        options=continuous_colours,
        index=heatmap_colour_default
    )
        
# Set up the colours
template = go.layout.Template()
template.layout.font.color = 'white'
template.layout.paper_bgcolor = '#1E1E1E'
template.layout.plot_bgcolor = background_colour
px.defaults.template = template

st.markdown('# Number of crashes')

def crashes_per_year():
    st.markdown('## Crashes over the years')
    df_year = find_crash_counts(df=df, grouping_cols=df['Date'].dt.year, date_name='Year')

    fig = px.line(
        data_frame=df_year,
        x='Year',
        y='Crashes',
        markers=True,
        title=f'Accidents per year',
        color_discrete_sequence=[plot_colour],
        template=template
    )
    st.plotly_chart(fig, use_container_width=True)


def crashes_per_day_number():
    st.markdown('## Crashes in each day number')
    df_day_number = find_crash_counts(df=df, grouping_cols=df['Date'].dt.day, date_name='Day')

    fig = px.histogram(    
        data_frame=df_day_number,
        x='Day',
        y='Crashes',
        text_auto=True,
        nbins=31,
        title=f'Number of plane crashes per day number',
        color_discrete_sequence=[plot_colour]
    ).update_layout(bargap=0.05).update_yaxes(title_text='Crashes')
    st.plotly_chart(fig, use_container_width=True)
 
def crashes_per_month():
    st.markdown('## Crashes in each month')
    df_month = find_crash_counts(df=df, grouping_cols='Month')

    fig = px.histogram(    
        data_frame=df_month,
        x='Month',
        y='Crashes',
        text_auto=True,
        nbins=12,
        title=f'Number of plane crashes per month',
        color_discrete_sequence=[plot_colour],
        height=500
    ).update_layout(bargap=0.2).update_yaxes(title_text='Crashes')
    st.plotly_chart(fig, use_container_width=True)
    
def crashes_per_day_of_week():
    st.markdown('## Crashes in each day')
    df_day = find_crash_counts(df=df, grouping_cols='Day_of_week')

    fig = px.histogram(    
        data_frame=df_day,
        x='Day_of_week',
        y='Crashes',
        text_auto=True,
        nbins=7,
        title=f'Number of plane crashes per day of week',
        color_discrete_sequence=[plot_colour],
        height=500
    ).update_layout(bargap=0.2).update_yaxes(title_text='Crashes')
    st.plotly_chart(fig, use_container_width=True)
    
def crashes_per_decade():
    st.markdown('## Crashes per decade')
    df_decade = find_crash_counts(df=df, grouping_cols='Decade')
    
    # We first need to find a good number of bins for this.
    max_decade, min_decade = df['Decade'].max(), df['Decade'].min()
    bin_count = max_decade - min_decade
    bin_count = bin_count // 10 + 1

    fig = px.histogram(    
        data_frame=df_decade,
        y='Decade',
        x='Crashes',
        text_auto=True,
        nbins=int(bin_count),
        title=f'Number of plane crashes per decade',
        orientation='h',
        color_discrete_sequence=[plot_colour],
        height=500
    ).update_layout(bargap=0.2).update_yaxes(title_text='Crashes')
    st.plotly_chart(fig, use_container_width=True)
    
def crashes_per_year_and_month(base_decade, separation):
    """
    Shows a heatmap of crashes per year and month of two decades.
    """
    decade_values = [base_decade + 10*i for i in range(0, separation)]

    # We now have to filter the dataframe so that the decade values are of base_decade and base_decade + 10.
    df_filtered = df.query('Decade in @decade_values')
    df_year_month = find_crash_counts(
        df=df_filtered,
        grouping_cols=[df_filtered['Date'].dt.year, 'Month'],
        date_name='Year'
    )
    
    # Next we make a pivot table.
    df_pivot = df_year_month.pivot_table(index='Month', columns='Year', values='Crashes')
    
    fig = px.imshow(
        df_pivot, 
        aspect='equal', 
        color_continuous_scale=heatmap_colour,
        title=f'Crashes from {decade_values[0]} till {decade_values[-1]+9}',
        width=100, height=500
    )
    st.plotly_chart(fig, use_container_width=True)

def crashes_per_month_weekday():
    st.markdown('## Per month and day of the week')
    df_month_weekday = find_crash_counts(df=df, grouping_cols=['Month', 'Day_of_week'])
    df_pivot = df_month_weekday.pivot_table(index='Day_of_week', columns='Month', values='Crashes')
    fig = px.imshow(
        df_pivot, 
        aspect='equal', 
        color_continuous_scale=heatmap_colour,
        title=f'Crashes by month and day of week',
        text_auto=True,
        width=400, height=500
    )
    st.plotly_chart(fig, use_container_width=True)
    
    
def crashes_per_month_day():
    st.markdown('## Per month and day number')
    df_month_day = find_crash_counts(df=df, grouping_cols=['Month', df['Date'].dt.day], date_name='Day')
    df_pivot = df_month_day.pivot_table(columns='Day', index='Month', values='Crashes')
    fig = px.imshow(
        df_pivot, 
        aspect='equal', 
        color_continuous_scale=heatmap_colour,
        title=f'Crashes by month and day number',
        text_auto=True,
        width=400, height=500
    )
    st.plotly_chart(fig, use_container_width=True)
    
    
if __name__ == "__main__":
    crashes_per_year()
    crashes_per_day_number()
    
    col1, col2 = st.columns(2)
    
    with col1:
        crashes_per_month()
    with col2:
        crashes_per_day_of_week()
    
    crashes_per_decade()
    
    # For the year-month heatmap, we split the diagram into unequal parts.
    separation = 4
    st.markdown('## Crashes per year and month')
    decade_values = df['Decade'].unique().tolist()[::-separation]
    for decade in decade_values:
        crashes_per_year_and_month(decade, separation)
    
    crashes_per_month_weekday()
    crashes_per_month_day()