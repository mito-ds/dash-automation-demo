import pandas as pd

def get_performance_data(username: str, password: str, year: int): 
    """
    Get Vangaurd fund performance data for a given year.

    The data returned by this function is sourced from: https://www.kaggle.com/datasets/callumrafter/vanguard-investor-fund-data?select=performance.csv
    """
    df = pd.read_csv('performance.csv')

    # Filter the pandas dataframe using the Date columns to only include the year specified
    df = df[df['Date'].str.contains(str(year))]

    return df
