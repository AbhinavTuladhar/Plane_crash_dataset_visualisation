import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import random
import plotly.io as io
import plotly.graph_objects as go
import pycountry_convert
import streamlit as st


st.set_page_config(layout="wide")

with st.sidebar:
    color = st.color_picker('Pick A Color', '#00f900')

st.markdown("# Plane crash dataset visualisation")
st.write("""
    This is a simple app to visualise the plane crash dataset. \n
    All of this data was scraped from this website: http://www.planecrashinfo.com/database.htm \n
    This extremely dirty data was then cleaned, and some additional columns were added. \n
    This is what the raw data looks like:
""")

df_old = pd.read_parquet('Result_file_compressed.parquet')
st.write(df_old)

st.write('This is what the processed dataset looks like:')
df_new = pd.read_csv('Processed_dataset/Crash_data_new.csv')
st.write(df_new)

print(df_new.dtypes)
print(df_new['Time'])