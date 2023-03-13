"""
A module which aims to use OOP to reuse code in all three visualisation pages
"""
import streamlit as st
from utils import find_crash_counts, aggregate_columns
import pandas as pd


class PlotMaker:
    
    def __init__(
        self, 
        df: pd.DataFrame,
        grouping_cols: list[str], 
        measure: str,
        agg_func: str, 
        plot_colour: str, 
        date_name: str = None
    ):
        """
        Arguments:
            df: The dataframe to be used.
            grouping_cols: The list of columns to group by.
            measure: The numeric data to be aggregated.
            agg_func: The aggregated function to be applied.
            plot_colour: The colour to be used in the plots.
            date_name: An alias of the date column.
        """
        self.df = df
        self.grouping_cols = grouping_cols
        self.measure = measure
        self.agg_func = agg_func
        self.plot_colour = plot_colour
        self.date_name = date_name
        
    def aggregate_dataframe(self):
        if self.agg_func is None:
            self.df_agg = find_crash_counts(
                df=self.df,
                grouping_cols=self.grouping_cols,
                date_name=self.date_name
            )
        else:
            self.df_agg = aggregate_columns(
                df=self.df,
                column_names=self.grouping_cols,
                agg_func=self.agg_func,
                value_column=self.measure
            )
    

df = pd.read_parquet('Processed_dataset/Crash_data_new.parquet')
print(df)