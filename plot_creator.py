"""
A module which aims to use OOP to reuse code in all three visualisation pages
"""
import streamlit as st
from utils import find_crash_counts, aggregate_columns
import pandas as pd
import plotly.express as px
import json
import plotly.graph_objects as go
import numpy as np


class PlotMaker:
    
    def __init__(
        self, 
        df: pd.DataFrame,
        measure: str,
        agg_func: str, 
        continuous_colour: str, 
        discrete_colour: str
    ):
        """
        Arguments:
            df: The dataframe to be used.
            grouping_cols: The list of columns to group by.
            measure: The numeric data to be aggregated.
            agg_func: The aggregated function to be applied.
            continuous_colour: The colour to be used in heatmaps.
            discrete_colour: The colour to be used in non-heatmap plots.
            date_name: An alias of the date column.
        """
        self.df = df
        self.measure = measure
        self.agg_func = agg_func
        self.continuous_colour = continuous_colour
        self.discrete_colour = discrete_colour
        self.type_map = {
            'int32': np.int32,
            'float64': np.float64
        }
        
    def aggregate_dataframe(self, grouping_cols: list[str], date_name: str=None, us_flag=None):
        """
        Aggregates the dataframe by the provided grouping columns and measure.
        
        Arguments:
            grouping_cols: The columns to group by.
            date_name: Renames the `Date` column to `date_name`
            us_flag: Whether to include the US in maps.
        """
        if us_flag is None:
            df_to_use = self.df
        else:
            df_to_use = self.df.query('Country == "United States of America"')
        if self.agg_func is None:
            df_agg = find_crash_counts(
                df=df_to_use,
                grouping_cols=grouping_cols,
                date_name=date_name
            )
        else:
            df_agg = aggregate_columns(
                df=df_to_use,
                column_names=grouping_cols,
                agg_func=self.agg_func,
                value_column=self.measure,
                date_name=date_name
            )
        return df_agg
    
    def draw_histogram(self, grouping_col: str, title: str, nbins: int, date_name: str = None, height: int = None):
        df_agg = self.aggregate_dataframe(grouping_cols=grouping_col, date_name=date_name)
        x = grouping_col if date_name is None else date_name
        hist_funcs_map = {
            'sum': 'sum',
            'mean': 'avg'
        }
        hist_func = hist_funcs_map.get(self.agg_func)
        fig = px.histogram(    
            data_frame=df_agg,
            x=x,
            y=self.measure,
            text_auto=True,
            nbins=nbins,
            title=title,
            histfunc=hist_func,
            color_discrete_sequence=[self.discrete_colour],
            height=height
        ).update_traces(marker=dict(line=dict(color='black', width=1))).update_layout(bargap=0.2)
        st.plotly_chart(fig, use_container_width=True)
        
    def draw_line_plot(self, grouping_col: str, title: str, date_name: str = None, height: int = None):
        df_agg = self.aggregate_dataframe(grouping_cols=grouping_col, date_name=date_name)
        
        fig = px.line(
            data_frame=df_agg,
            x=date_name,
            y=self.measure,
            markers=True,
            title=title,
            color_discrete_sequence=[self.discrete_colour],
            height=height,
        )
        st.plotly_chart(fig, use_container_width=True)
        
    def draw_world_map(self, us_exclude_flag, grouping_col: str, title: str):
        """
        Draw a heatmap-based world map based on the supplied measure.
        
        Arguments:
            us_exclude_flag: Omit the US from maps.
            grouping_col: The column to group by.
            title: The title of the figure.
        """
        df_agg = self.aggregate_dataframe(grouping_cols=grouping_col, date_name=None)
        if us_exclude_flag:
            df_agg = df_agg.query('Country != "United States of America"')
        fig = px.choropleth(
            df_agg,
            locations='Country',
            locationmode='country names',
            color=self.measure,
            hover_name='Country',
            color_continuous_scale=self.continuous_colour,
            title=title
        ).update_layout(geo=dict(showocean=True, oceancolor='LightBlue'),
            title=dict(x=0.5),
            margin=dict(l=0, r=0, t=0, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)
        
    def draw_US_map(self, title: str=None):
        """
        Draws a heatmap for the US states for the supplied measure.
        """
        with open('US_states_abbrv.json', 'r') as file:
            state_abbr = json.load(file)
        df_US_agg = self.aggregate_dataframe(grouping_cols='US_State', us_flag=True)
        df_US_agg['StateAbbr'] = df_US_agg['US_State'].map(state_abbr)
        
        fig = px.choropleth(
            df_US_agg,
            locations='StateAbbr',
            locationmode='USA-states',
            color=self.measure,
            hover_name='US_State',
            color_continuous_scale=self.continuous_colour,
            scope='usa',
            title=title
        ).update_layout(geo=dict(showocean=True, oceancolor='LightBlue'),
            title=dict(x=0.5),
            margin=dict(l=0, r=0, t=0, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)
        
    def _return_heatmap(self, matrix, title=None, height: int = None, show_value: bool = False) -> go.Figure:
        fig = px.imshow(
            matrix, 
            aspect='equal',
            text_auto=show_value, 
            color_continuous_scale=self.continuous_colour,
            height=height,
            title=title
        )
        return fig
        
    def draw_heatmap_year_month(
        self, 
        divisions: int=4,
        title: str=None, 
        height: int = None,
        target_type: str = None,
        show_value: bool = False
    ):
        """
        Make a heatmap of year vs month.
        
        Arguments:
            division: The number of parts to divide the total number of decades with.
            title: The title
            size: A list consisting of [width, height]
            target_type: The type that the measure column should be converted to. Must be one of `int32`, `float64` or `None`
        """
        decades = self.df['Decade'].unique().tolist()
        decade_values = decades[::-divisions]

        for decade in decade_values:
            decade_to_draw = [decade + 10*i for i in range(0, divisions)]
            df_agg = self.aggregate_dataframe(grouping_cols=[self.df.query('Decade in @decade_to_draw')['Date'].dt.year, 'Month'], date_name='Year')
            measure_dtype = self.type_map.get(target_type)
            df_agg[self.measure] = df_agg[self.measure].astype(measure_dtype)
            matrix = df_agg.pivot_table(
                index='Month',
                columns='Year',
                values=self.measure
            )
            figure = self._return_heatmap(matrix=matrix, title=title, height=height, show_value=show_value)
            st.plotly_chart(figure, use_container_width=True)
            
    def make_heatmap_month_day(self, title=None, height: int = None, target_type: str = None, show_value: bool = False):
        df_agg = self.aggregate_dataframe(grouping_cols=['Month', 'Day_of_week'])
        measure_dtype = self.type_map.get(target_type)
        df_agg[self.measure] = df_agg[self.measure].astype(measure_dtype)
        matrix = df_agg.pivot_table(
            index='Day_of_week',
            columns='Month',
            values=self.measure
        )
        figure = self._return_heatmap(matrix=matrix, title=title, height=height, show_value=show_value)
        st.plotly_chart(figure, use_container_width=True)
        
    def make_heatmap_month_day_number(self, title=None, height: int = None, target_type: str = None, show_value: bool = False):
        df_agg = self.aggregate_dataframe(grouping_cols=['Month', self.df['Date'].dt.day], date_name='Day')
        measure_dtype = self.type_map.get(target_type)
        df_agg[self.measure] = df_agg[self.measure].astype(measure_dtype)
        matrix = df_agg.pivot_table(
            columns='Day',
            index='Month',
            values=self.measure
        )
        figure = self._return_heatmap(matrix=matrix, title=title, height=height, show_value=show_value)
        st.plotly_chart(figure, use_container_width=True)
        
    def draw_time_histogram(self, nbins: int, title: str=None, height: int = None):
        df_time = self.aggregate_dataframe(grouping_cols='Time')
        df_time['Time'] = pd.to_datetime(df_time['Time'], format="%H:%M:%S").sort_values()
        hist_funcs_map = {
            'sum': 'sum',
            'mean': 'avg'
        }
        hist_func = hist_funcs_map.get(self.agg_func)
        fig = px.histogram(    
            data_frame=df_time,
            x='Time',
            y=self.measure,
            text_auto=True,
            nbins=nbins,
            title=title,
            color_discrete_sequence=[self.discrete_colour],
            histfunc=hist_func,
            height=height
        ).update_traces(marker=dict(line=dict(color='black', width=1))).update_layout(bargap=0.2)
        st.plotly_chart(fig, use_container_width=True)
        
    def draw_country_treemap(self, us_exclude_flag: bool = False, height: int = None):
        df_agg = self.aggregate_dataframe(grouping_cols='Country')
        if us_exclude_flag:
            df_agg = df_agg.query('Country != "United States of America"')
        self.country_treemap_threshold = st.number_input(label=f'Enter the threshold value for `{self.measure}`', key=1, step=1)
        df_agg = df_agg.query(f'{self.measure} >= @self.country_treemap_threshold')
        fig = px.treemap(
            df_agg, 
            path=[px.Constant("world"), 'Country'], 
            values=self.measure,
            color=self.measure,
            title='By country',
            color_continuous_scale=self.continuous_colour,
            height=height
        )
        st.plotly_chart(fig, use_container_width=True)
        
    def draw_continent_country_treemap(self, us_exclude_flag: bool = False, height: int = None):
        df_agg = self.aggregate_dataframe(grouping_cols=['Continent', 'Country'])
        if us_exclude_flag:
            df_agg = df_agg.query('Country != "United States of America"')
        df_agg[self.measure] = df_agg[self.measure].astype('int32')
        df_agg = df_agg.query(f'{self.measure} >= @self.country_treemap_threshold')
        fig = px.treemap(
            df_agg, 
            path=[px.Constant("world"), 'Continent', 'Country'], 
            values=self.measure,
            color=self.measure,
            title='By continent and country',
            color_continuous_scale=self.continuous_colour,
            height=height
        )
        st.plotly_chart(fig, use_container_width=True)
