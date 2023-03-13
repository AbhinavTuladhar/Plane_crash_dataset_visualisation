import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils import aggregate_columns, find_crash_counts

st.set_page_config(layout="wide")

# LOAD THE DATASET
df = pd.read_parquet('Processed_dataset/Crash_data_new.parquet')

# Read the CSS colours values
with open('Colours_list_real.txt', 'r') as file:
    values = file.readlines()
    CSS_colours = [value.strip() for value in values]

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
        color_discrete_sequence=[plot_colour]
    ).update_layout(bargap=0.05).update_yaxes(title_text='Crashes')
    st.plotly_chart(fig, use_container_width=True)
    
if __name__ == "__main__":
    crashes_per_year()
    crashes_per_month()
