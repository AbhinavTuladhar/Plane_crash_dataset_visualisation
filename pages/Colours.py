import streamlit as st

# Read the list of colors from a text file
with open("Colours_list_real.txt", "r") as f:
    colors = [line.strip() for line in f]

# Define the size of the grid
grid_size = 14
cols = 5
rows = len(colors) // cols + 1

# Define the size of each color box
box_size = 30

# Define the style for the color box
box_style = f"width:{box_size}px; height:{box_size}px; margin:0px;"

# Define the style for the color name
name_style = f"text-align:center; font-size:12px; margin-top:5px; margin-bottom:0px;"

# Create a table for the grid
table = "<table>"
for i in range(rows):
    # Add a row for the color boxes and names
    table += "<tr>"
    try:
        for j in range(cols):
            color = colors[i*grid_size + j]
            table += f"<td style='{name_style}'>{color}</td>"
            table += f"<td style='{box_style} background-color:{color};'></td>"
        table += "</tr>"
    except IndexError:
        break
table += "</table>"

# Display the table
st.write(table, unsafe_allow_html=True)