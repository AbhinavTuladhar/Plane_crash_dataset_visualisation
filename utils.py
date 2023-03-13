"""
A bunch of utlity functions for aggregation, pivot tables, etc.
"""
import pandas as pd

# Load the dataframe.
df = pd.read_parquet('Processed_dataset/Crash_data_new.parquet')
print(df)

def find_crash_counts(
        df: pd.DataFrame, 
        grouping_cols: list[str], 
        date_name: str=None,
        sort_ascending: bool=None
    ) -> pd.DataFrame:
    """
    Finds the number of plane crashes grouped by `grouping cols.`
    
    Arguments:
        df: The dataframe to be operated upon.
        grouping_cols: The columns to aggregate on.
        date_name: If the data is to be aggregated from a date value, supply the name of the new column.
        sort_ascending: Whether to sort the values. `None` doesn't sort the values at all, `True` sorts in ascending 
            order and `False` sorts in descending order.
    Returns:
        A pandas DataFrame containing the aggregated data.
    """
    try:
        df_grouped = df.groupby(grouping_cols) \
            .size() \
            .reset_index(name='Crashes')
    except KeyError:
        raise Exception('The column name is incorrect.')
    
    if date_name is not None:
        df_grouped = df_grouped.rename(columns={'Date': date_name})
    if sort_ascending is not None:
        df_grouped = df_grouped.sort_values(by='Crashes', ascending=sort_ascending)
    return df_grouped


def aggregate_columns(
        df: pd.DataFrame, 
        column_name: str, 
        agg_func: str, 
        value_column: str,
        date_name: str=None
    ) -> pd.DataFrame:
    """
    Aggregates `column_name` by the aggregation function `agg_func`.
    
    Arguments:
        df: The dataframe to be ooperated upon.
        column_name: The column that is to be aggregated by.
        value_column: The column containing the values to be aggregated.
        agg_func: The aggregation function to be applied to `column_name`.
        date_name: If a date column is supplied, rename that column to `date_name`.
        
    Returns:
        A pandas DataFrame containing the aggregated data.
    """
    try:
        df_grouped = df.groupby(column_name) \
            [value_column] \
            .agg(agg_func) \
            .reset_index()
    except AttributeError:
        raise Exception('The aggregation function is not correct!')
    except KeyError:
        raise Exception('The column name is invalid.')
                              
    if date_name is not None:
        df_grouped = df_grouped.rename(columns={column_name: date_name})
        
    return df_grouped