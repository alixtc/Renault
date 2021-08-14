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
    temp.reset_index(drop= True, inplace=True)
    temp.reset_index(inplace=True)
    
    return sns.scatterplot(data=temp, x='index', y='dataValue')


def plot_fluids(df, x, y):
    """Plot a scatter plot for x and y;
    with separate suplots for each fluid"""
    
    fig, ax = plt.subplots(1, 3, figsize= (14, 5))
    temp = df[df['fluid'] ==  'FRFluid']
    sns.scatterplot(data=temp, x=x, y=y, ax=ax[0], color='g')
    ax[0].set_title('FRFluid')

    temp = df[df['fluid'] == 'HFOFluid']
    sns.scatterplot(data=temp, x=x, y=y,  ax=ax[1], color='b')
    ax[1].set_title('HFOFluid')

    temp = df[df['fluid'] == 'RMFluid']
    sns.scatterplot(data=temp, x=x, y=y,  ax=ax[2], color='r')
    ax[2].set_title('RMFluid')
    
    return fig, ax