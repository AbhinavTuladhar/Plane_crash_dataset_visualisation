"""
A bunch of utlity functions for aggregation, pivot tables, etc.
"""

import pandas as pd

# Load the dataframe.
df = pd.read_parquet('Processed_dataset/Crash_data_new.parquet')
print(df)