import streamlit as st


col1, col2 = st.columns(2)

col1.subheader('Row 1, column 1')
col1.write('Bottom text')

col1.subheader('Row 2, column 1')
col1.write('Bottom text')

col2.subheader('Row 1, column 2')
col2.write('Bottom text')

col2.subheader('Row 2, column 2')
col2.write('Bottom text')

st.markdown("# SOMETHING")

col1, col2 = st.columns(2)
col1.subheader('BTO')
col1.write('WHAT')

col2.subheader('Somet column')
col2.write('here')

first = st.columns()