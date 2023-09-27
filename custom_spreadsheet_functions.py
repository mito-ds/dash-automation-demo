import pandas as pd

def GET_NUMEBR_OF_ASSETS(fund_name_series):
    """
    Get the number of assets in each fund. 
    """
    df = pd.read_csv('portfolio.csv')
    df = df.merge(fund_name_series, on='Fund Name')
    return df['Number of Assets']