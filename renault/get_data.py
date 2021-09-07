


def get_most_important_types(df, n_cars=10):
    """
    From the original data frame, returns the most frequent types of cars
    (sorted by decreasing number of vehicules)
    """
    vehicules = df.loc[:, ['pji', 'body_type','driving_side','gearbox_type','hybrid_level','engine_type']].drop_duplicates()

    # Count number of pji per vehicule type
    temp = vehicules.groupby(['body_type', 'gearbox_type', 'engine_type', 'driving_side', 'hybrid_level'])[['pji']].\
    count(). \
    reset_index().\
    sort_values('pji', ascending=False) 

    # Relative importance of each type + DF reshaping 
    temp['pji'] = temp.pji / vehicules.shape[0] * 100
    car_types = temp.rename(columns={'pji':'percentage_of_production'})
    top_cars = car_types.head(n_cars)
    return top_cars


def get_pji_with_misssing_fluids_measure(input_df, n_fluids=3, n_measure=3):
    """Returns only pji with less than 3 fluids and 3 measurements 
    for automatic recall"""
    # pji of vehicules with missing fluid
    vehicules_without_3_fluids = input_df.groupby('pji')[['fluid']]\
    .agg('nunique')
    vehicules_without_3_fluids = vehicules_without_3_fluids[vehicules_without_3_fluids['fluid'] < n_fluids].index
    bad_pji = list(vehicules_without_3_fluids)
    
    # Removes vehicules with missing fluids
    filtered_vehicules = input_df[~input_df.pji.isin(bad_pji)]

    # PJI of vehicules with missing mesurements
    temp = filtered_vehicules\
    .groupby(['pji', 'fluid'])[['measurement']]\
    .agg('nunique')\
    .reset_index()
    temp = temp[temp['measurement'] < n_measure]
    vehicules_without_3_measures = temp['pji'].unique()
    
    bad_pji.extend(list(vehicules_without_3_measures))
    return bad_pji