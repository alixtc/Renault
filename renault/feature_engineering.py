import pandas as pd


def feature_engineering(input_df):
    """
    Input is a dataframe with same number of fluids and measurements per PJI
    
    Returns: Observations are PJI in index, columns are the differents features 
    regrouped by fluids and meaasurements
    """
    
    # Grabs the last values for each fluid/measurements, calculate average
    tail_analysis = input_df.groupby(['pji', 'fluid', 'measurement']).tail(3)
    tail_analysis = tail_analysis.groupby(['pji', 'fluid', 'measurement'])[['dataValue']].mean()


    # Get low and high quantiles for each fluid/measurements, calculate average
    # In case distributions are somewhat skewed
    end_distrib_analysis = input_df\
    .groupby(['pji', 'fluid', 'measurement'])['dataValue']\
    .describe(percentiles=[0.1, 0.2, 0.8, 0.9]
    )
    end_distrib_analysis = end_distrib_analysis.drop(['count', 'std'], axis=1)

    # Number of points in for each fluid/measurements + average time delta
    timing = input_df.groupby(['pji', 'fluid', 'measurement']).agg({'delta':['count', 'mean', 'max']})

    # Mean and max Slope for dataValue
    tdelta_analysis = input_df.copy()
    tdelta_analysis = tdelta_analysis.sort_values(['fluid', 'measurement', 'time'])
    slope = tdelta_analysis.groupby(['pji', 'fluid', 'measurement'])['dataValue'].diff()
    tdelta_analysis['slope'] = slope
    tdelta_analysis = tdelta_analysis.groupby(['pji', 'fluid', 'measurement']).agg({'slope':["mean", "max"]})
    
    # Combine on their multiple index all previous dataframes 
    # indexes are PJI, fluid, and measurement
    global_merged = pd.concat(
        [tail_analysis, timing, tdelta_analysis, end_distrib_analysis],
        axis=1, join='inner')
    # Pivot to wider format: 1 observation = 1 PJI (in index)
    column_list = global_merged.columns
    final_df = global_merged.pivot_table(values=column_list, 
                    index = ['pji'],
                    columns=['fluid', 'measurement'], sort=False )
    
    # add order of filling sequence 
    # grouped by pji, order of fluids
    fluid_begining = input_df.groupby(['pji', 'fluid'])['time'].min().reset_index()
    fluid_begining = fluid_begining.sort_values('time')
    fluid_begining['order'] = fluid_begining.groupby('pji').cumcount()+1
    # one col per fluid, order as int, PJI as index
    fluid_order = fluid_begining.drop('time', axis=1).pivot(index='pji', values='order', columns='fluid')
    
    # Add columns with fluid order, merging based on pji in index
    final_df = pd.concat([final_df, fluid_order], axis=1)

    return final_df