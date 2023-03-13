"""
A module which aims to use OOP to reuse code in all three visualisation pages
"""
import streamlit as st
from utils import find_crash_counts, aggregate_columns


class PlotMaker:
    
    def __init__(self, grouping_cols, agg_func, plot_colour, date_name):
        