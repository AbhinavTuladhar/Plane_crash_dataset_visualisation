import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils import aggregate_columns, find_crash_counts
from plot_creator import PlotMaker
from collections import namedtuple


# LOAD THE DATASET
df = pd.read_parquet('Processed_dataset/Crash_data_new.parquet')

class Template:
    
    def __init__(self, measure, agg_func):
        st.set_page_config(layout="wide")
        self.df = df
        with open('Colours_list_real.txt', 'r') as file:
            values = file.readlines()
            self.CSS_colours = [value.strip() for value in values]
            
        # For the continous colour scales (for heatmaps)
        self.continuous_colours = px.colors.named_colorscales()
        self.continuous_colours.sort()

        # Find the index of the default scale - "Jet"
        self.heatmap_colour_default = self.continuous_colours.index('jet')
        
        self._make_sidebar()
        self.plotter = PlotMaker(df=self.df, measure=measure, agg_func=agg_func, continuous_colour=self.heatmap_colour, discrete_colour=self.plot_colour)
    
    def _make_sidebar(self):
        with st.sidebar:
            self.colour_choice = st.selectbox(
                label='Use CSS colours or hex colours?',
                options=['CSS', 'Hex'],
                index=0
            )
            if self.colour_choice == 'Hex':
                self.plot_colour = st.color_picker(label='Colour to be used in the plots')
            else:
                self.plot_colour = st.selectbox(
                    label='Select the plot colour',
                    options=self.CSS_colours
                )
            self.heatmap_colour = st.selectbox(
                label='Select the colour scale for heatmaps',
                options=self.continuous_colours,
                index=self.heatmap_colour_default
            )
            self.figure_height = st.slider(
                label='Select the figure heights',
                min_value=400, max_value=800,
                value=500,
                step=50
            )
            
    def _make_filters(self):
        st.markdown('Apply the filters you want.')
        col1, col2, col3, col4, col5, col6, col7= st.columns(7)
        with col1:
            self.country_filter = st.checkbox(label='Country/Region', value=False)
        with col2:
            self.continent_filter = st.checkbox(label='Continent', value=False)
        with col3:
            self.year_filter = st.checkbox(label='Year', value=False)
        with col4:
            self.month_filter = st.checkbox(label='Month', value=False)
        with col5:
            self.day_filter = st.checkbox(label='Day of week', value=False)
        with col6:
            self.day_num_filter = st.checkbox(label='Day', value=False)
        with col7:
            self.decade_filter = st.checkbox(label='Decade', value=False)

        self.passenger_filter = st.checkbox(label='Commercial flights', value=False)
            
        self.location_filters = [self.country_filter, self.continent_filter]

        # Create the options for the selectboxes
        # For locations
        self.df['Continent'] = self.df['Continent'].fillna(value='Unknown')
        country_list = sorted(self.df['Country'].unique())
        continent_list = sorted(self.df['Continent'].unique())
        self.selected_country, self.selected_continent = False, False
        
        # For dates
        year_list = sorted(self.df['Date'].dt.year.unique())
        month_list = self.df['Month'].sort_values().unique().tolist()
        day_list = self.df['Day_of_week'].sort_values().unique().tolist()
        day_num_list = sorted(self.df['Date'].dt.day.unique())
        decade_list = sorted(self.df['Decade'].unique())
        self.selected_year, self.selected_month, self.selected_day, self.selected_day_num, self.selected_decade = [False for _ in range(5)]

        # Make filters for locations
        if self.country_filter:
            self.selected_country = st.selectbox(label='Select the country (or region)', options=country_list)
            self.plotter.df = self.plotter.df.query("Country in @self.selected_country")
        if self.continent_filter:
            self.selected_continent = st.selectbox(label='Select the continent', options=continent_list)
            self.plotter.df = self.plotter.df.query('Continent in @self.selected_continent')
            
        # Make filters for date and times
        if self.year_filter:
            self.selected_year = st.selectbox(label='Select the year', options=year_list)
            self.plotter.df = self.plotter.df.query("Date.dt.year == @self.selected_year")
        if self.month_filter:
            self.selected_month = st.selectbox(label='Select the month', options=month_list)
            self.plotter.df = self.plotter.df.query("Month == @self.selected_month")
        if self.day_filter:
            self.selected_day = st.selectbox(label='Select the day', options=day_list)
            self.plotter.df = self.plotter.df.query("Day_of_week == @self.selected_day")
        if self.day_num_filter:
            self.selected_day_num = st.selectbox(label='Select the day number', options=day_num_list)
            self.plotter.df = self.plotter.df.query("Date.dt.day == @self.selected_day_num")
        if self.decade_filter:
            self.selected_decade = st.selectbox(label='Select the decade', options=decade_list)
            self.plotter.df = self.plotter.df.query("Decade == @self.selected_decade")
            
        # For non-military flights
        if self.passenger_filter:
            self.plotter.df = self.plotter.df.query('Type == "Passenger"')
            
    def _make_year_line_plot(self):
        st.markdown('## By year')
        self.plotter.draw_line_plot(grouping_col=self.plotter.df['Date'].dt.year, title='Per year', date_name='Year', height=self.figure_height)
            
    def _update_colours(self):
        self.plotter.continuous_colour = self.heatmap_colour
        self.plotter.discrete_colour = self.plot_colour
        
    def _make_main_title(self, title):
        st.markdown(f'# {title}')
        
    def _make_date_tabs(self):
        st.markdown('## By date or time')
        decade_tab, month_tab, day_tab, day_num_tab, time_tab = st.tabs([
            'Decade', 'Month', 'Day of week', 'Day number', 'Time of day'
        ])
        
        # If a particular date filter is applied, omit making the corresponding graph since it has only one column.
        error_message = '## Not applicable because of the applied filter(s).'
        tabs_info = [
            {
               'tab_name': decade_tab, 
                'filter': self.decade_filter, 
                'grouping_column': 'Decade',
                'title': 'Per decade', 
                'nbins': 15, 
            },
            {
                'tab_name': month_tab, 
                'filter': self.month_filter, 
                'grouping_column': 'Month',
                'title': 'Per month', 
                'nbins': 7,
            },
            {
                'tab_name': day_num_tab, 
                'filter': self.day_num_filter, 
                'grouping_column': self.df['Date'].dt.day,
                'title': 'Per day number', 
                'nbins': 31,
                'date_name': 'Day',
            },
            {
                'tab_name': day_tab, 
                'filter': self.day_filter, 
                'grouping_column': 'Day_of_week',
                'title': 'Per day', 
                'nbins': 12,
            },
        ]
        
        for tab_info in tabs_info:
            with tab_info['tab_name']:
                if tab_info['filter']:
                    st.write(error_message)
                    continue
                self.plotter.draw_histogram(
                    grouping_col=tab_info.get('grouping_column'),
                    title=tab_info.get('title'),
                    nbins=tab_info.get('nbins'),
                    date_name=tab_info.get('date_name'),
                    height=self.figure_height
                )

        # Give an explanation about the x-axis of the time histogram.
        time_tab_message = """
            A pandas column cannot be represented purely in just time - a date needs to be attached to this time data. \n
            As a result, the date in the x-axis is assumed to be the 1st of January, 1900. \n
            In other words, all the crashes are assumed to have occured on this date at different times of day.
        """
        with time_tab:
            with st.expander('A notice regarding the x-axis'):
                st.markdown(time_tab_message)
            self.plotter.draw_time_histogram(nbins=24*2, title='Time of day', height=self.figure_height)
                            
    def _make_geo_maps(self):
        # Create a worldmap only if all an individual country is not selected
        if self.selected_country:
            return
        st.markdown('## By countries')
        us_exclude_flag = st.checkbox('Exclude the US from world map?')
        # Make an expander to show the reason.
        with st.expander('Explanation:'):
            message = """
                There are a lot of data points of the US compared to other countries.
                Including the US will heavily skew the colour palette in the favour of the US.
                Excluding it will somewhat remove the skew.
            """
            st.write(message)
        self.plotter.draw_world_map(us_exclude_flag=us_exclude_flag, grouping_col='Country', title='Crashes throughout the world')
        
        # Show the map of US only if all countries are selected or North America has been selected.
        if (self.selected_country == 'United States of America' or
            self.selected_continent == 'North America' or
            not any(self.location_filters)):
            st.markdown('## By US states')
            self.plotter.draw_US_map(title='Crashes throughout the US')
            
    def _make_heatmaps(self, type_conversion: str = None):
        """
        Arguments:
            type_conversion: The target type of the measure column. Must be one of `int32`, `float64` or `None`
        """
        date_filters = [self.year_filter, self.month_filter, self.day_filter, self.day_num_filter]
        condition = all(date_filters) or not any(date_filters)
        if not condition:
            return
        st.markdown('## Heatmaps')
        self.show_values = st.checkbox('Show values?', value=False)
        year_month, month_day, month_day_number = st.tabs([
            'Year and month', 'Month and day', 'Month and day number'
        ])
        Kwargs = namedtuple('Kwargs', ['title'])
        tabs_info = [
            (year_month, self.plotter.draw_heatmap_year_month, Kwargs('Year and month')),
            (month_day, self.plotter.draw_heatmap_month_day, Kwargs('Month and day')),
            (month_day_number, self.plotter.draw_heatmap_month_day_number, Kwargs('Month and day number'))
        ]
        
        for tab_name, function, arguments in tabs_info:
            with tab_name:
                function(**arguments._asdict(), target_type=type_conversion, height=self.figure_height, show_value=self.show_values)
        
    def _make_treemaps(self):
        if self.country_filter:
            return
        st.markdown('## Treemaps')
        us_exclude = st.checkbox('Ignore the US?', value=False)
        self.plotter.draw_country_treemap(height=self.figure_height, us_exclude_flag=us_exclude)
        self.plotter.draw_continent_country_treemap(height=self.figure_height, us_exclude_flag=us_exclude)
        

    def make_page(
        self, 
        main_title: str, 
        target_type: str, 
        treemap_flag: bool = True
    ):
        self._make_main_title(main_title)
        self._make_filters()
        if not self.year_filter:
            self._make_year_line_plot()
        self._make_date_tabs()
        self._make_geo_maps()
        self._make_heatmaps(target_type)
        if treemap_flag:
            self._make_treemaps()
        