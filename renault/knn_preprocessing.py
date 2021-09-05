from renault.get_data import get_pji_with_misssing_fluids_measure
import pandas as pd

def preprocess_data(input_df):
    """Global organisation of the data
    
    Return a dataframe with one line per PJI and engineered features +
    List of all bad PJI that have to be considered as anomaly"""
    # remove pji without 3 fluids and 3 measurements
    bad_pji = get_pji_with_misssing_fluids_measure(input_df)
    input_df = input_df[~input_df.pji.isin(bad_pji)]

    # Observations are PJI
    # columns are the differents features regrouped by fluids and measurements
    # important features
    # Average dataValue in tail(10)
    mean_tail_value = input_df.groupby(['pji', 'fluid', 'measurement']).tail(10)
    mean_tail_value = mean_tail_value.groupby(['pji', 'fluid', 'measurement'])[['dataValue']].mean()

    # Number of points in each group + average time delta
    timing = input_df.groupby(['pji', 'fluid', 'measurement']).agg({'delta':['count', 'mean', 'max']})

    # Slope meaningful values (min max or q10, q90)
    slope_df = input_df.copy()
    slope_df = slope_df.sort_values(['fluid', 'measurement', 'time'])
    slope = slope_df.groupby(['pji', 'fluid', 'measurement'])['dataValue'].diff()
    slope_df = input_df.copy()
    slope_df['slope'] = slope
    slope_df = slope_df.groupby(['pji', 'fluid', 'measurement']).agg({'slope':["mean", "max"]})
    

    global_merged = pd.concat([mean_tail_value, timing, slope_df], axis=1, join='inner')
    column_list = global_merged.columns
    final_df = global_merged.pivot_table(values=column_list, 
                    index = ['pji'],
                    columns=['fluid', 'measurement'], sort=False )

    return final_df, bad_pji