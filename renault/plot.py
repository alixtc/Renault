import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def plot_all_fluid(ropit, pji_number):
    """Given pandas Ropit dataframe, and a vehicule number, 
    plot curves for all available fluids"""
    df = ropit[ropit.pji == pji_number]
    df.reset_index(drop= True, inplace=True)
    df.reset_index(inplace=True)

    g = sns.FacetGrid(data=df, col='fluid', hue='measurement')
    g.map_dataframe(sns.scatterplot, x='index', y='dataValue')
    g.set_xlabels('Timepoints')
    g.set_ylabels('Measurement value')
    g.add_legend()
    g.fig.set_figheight(4)
    g.fig.set_figwidth(13)
    g.fig.suptitle(f'Measurements for PJI N° {pji_number}')
    return g
    
def plot_selective_fluid(df, pji_numer, fluid, measure):
    """visualize the data for a given PJI, fluid, and measurement"""
    temp = df[df['fluid'] == fluid]
    temp = temp[(temp['pji'] == pji_numer) & (temp['measurement'] == measure)]
    
    pass