# -*- coding: utf-8 -*-
"""
Plotters Functions Module
Comprehensive collection of plotting and visualization utilities for data exploration and presentation
"""

# third-party data science imports
import pandas as pd
import numpy as np

# visualization imports
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

# other plotters
from statsmodels.nonparametric.smoothers_lowess import lowess

def df_boxplot_plotter(df_name, col_xplot, col_yplot, type_plot: int, save_path=None, *args):
    """create box plot to visualize outliers. type_plot: 0 for dist, 1 for money, 2 for general"""
    # usage: df_boxplotter(df, 'col_x', 'col_y', type_plot=0, 'horizontalalignment')
    # input: df_name - pandas DataFrame, col_xplot - column name for x-axis, col_yplot - column name for y-axis, type_plot - type of plot (0 for dist, 1 for money, 2 for general), args - optional arguments for plot customization
    # optional input: save_path - optional path to save the plot 
    # output: box plot figure
    name_plot = "Boxplot_x-{}_y-{}.png".format(col_xplot, col_yplot)
    fig, ax = plt.subplots(figsize=(8, 6), dpi=100)
    sns.boxplot(x=df_name[col_xplot], y=df_name[col_yplot], ax=ax)
    plt.title('{} box plot to visualise outliers'.format(col_yplot))
    
    if type_plot == 0:
        plt.ylabel('{} in miles'.format(col_yplot))
    elif type_plot == 1:
        plt.ylabel('{} in $'.format(col_yplot))
    else:
        plt.ylabel('{}'.format(col_yplot))
    
    if args:
        plt.xticks(rotation=0, horizontalalignment=args[0])
    
    ax.yaxis.grid(True)
    if save_path:
        plt.savefig(save_path)
    plt.show()


def df_histogram_plotter(df_name, col_plot, type_plot: int, bins=10, save_path=None, *args):
    """create histogram plot. type_plot: 0 for dist, 1 for money"""
    # usage: df_histplotter(df, 'col_name', type_plot=0, bins=20)
    # input: df_name - pandas DataFrame, col_plot - column name to plot, type_plot - type of plot (0 for dist, 1 for money), bins - number of bins
    # output: histogram figure
    name_plot = "Histogram_{}.png".format(col_plot)
    fig, ax = plt.subplots(figsize=(8, 6), dpi=100)
    df_name[col_plot].hist(bins=bins, ax=ax)
    plt.title('{} histogram'.format(col_plot))
    
    if type_plot == 0:
        plt.xlabel('{} in miles'.format(col_plot))
    elif type_plot == 1:
        plt.xlabel('{} in $'.format(col_plot))
    else:
        plt.xlabel('{}'.format(col_plot))
    
    plt.ylabel('Frequency')
    ax.grid(True)
    if save_path:
        plt.savefig(save_path)
    plt.show()


def df_grouped_histogram_plotter(df_name, col_groupby: str, col_plot: str, type_plot: int, bins=20, save_path=None):
    """create grouped histogram plots"""
    # usage: df_grouped_histplotter(df, 'col_groupby', 'col_plot', type_plot=0, bins=20)
    # input: df_name - pandas DataFrame, col_groupby - column name to group by, col_plot - column name to plot, type_plot - type of plot (0 for dist, 1 for money), bins - number of bins
    # output: grouped histogram figure
    groups = df_name.groupby(col_groupby)
    fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
    
    for name, group in groups:
        group[col_plot].hist(bins=bins, alpha=0.7, label=name, ax=ax)
    
    plt.title('{} histogram grouped by {}'.format(col_plot, col_groupby))
    plt.xlabel(col_plot)
    plt.ylabel('Frequency')
    plt.legend()
    if save_path:
        plt.savefig(save_path)
    plt.show()


def df_grouped_barplotter(df_name, col_groupby: str, col_plot: str, type_plot: int, save_path=None):
    """create grouped bar plots"""
    # usage: df_grouped_barplotter(df, 'col_groupby', 'col_plot', type_plot=0)
    # input: df_name - pandas DataFrame, col_groupby - column name to group by, col_plot - column name to plot, type_plot - type of plot (0 for dist, 1 for money)
    # output: bar plot figure
    grouped_data = df_name.groupby(col_groupby)[col_plot].mean()
    fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
    grouped_data.plot(kind='bar', ax=ax)
    plt.title('{} by {}'.format(col_plot, col_groupby))
    plt.xlabel(col_groupby)
    plt.ylabel(col_plot)
    plt.xticks(rotation=45)
    if save_path:
        plt.savefig(save_path)
    plt.show()


def df_scatter_plotter(df_grouped, col_xplot, col_yplot, save_path=None):
    """create scatter plot between two variables"""
    # usage: df_scatterplotter(df, 'col_x', 'col_y')
    # input: df_grouped - pandas DataFrame with columns col_xplot and col_yplot
    # output: scatter plot figure
    fig, ax = plt.subplots(figsize=(8, 6), dpi=100)
    df_grouped.plot.scatter(x=col_xplot, y=col_yplot, ax=ax)
    plt.title('Scatter plot: {} vs {}'.format(col_xplot, col_yplot))
    if save_path:
        plt.savefig(save_path)
    plt.show()


def df_pairplot_plotter(df_name, save_path=None):
    """create pairplot for data exploration"""
    # usage: df_pairplot(df)
    # input: df - pandas DataFrame, with features to plot
    # output: pairplot figure
    sns.pairplot(df_name)
    if save_path:
        plt.savefig(save_path)
    plt.show()


def df_heatmap_plotter(df_name, col_list: list, save_path=None):
    """create heatmap for correlation matrix"""
    # usage: df_heatmap(df, ['col1', 'col2', 'col3'])
    # input: df - pandas DataFrame, col_list - list of column names to include in correlation
    # output: heatmap figure
    corr = df_name[col_list].corr()
    plt.figure(figsize=(10, 8), dpi=100)
    sns.heatmap(corr, annot=True, fmt=".2f", cmap='coolwarm', square=True)
    plt.title('Correlation Heatmap')
    if save_path:
        plt.savefig(save_path)
    plt.show()


def df_lowess_plotter(x, y, frac=0.1, title="LOWESS Smoothing", save_path=None):
    """create LOWESS smoothed plot"""
    # usage: df_lowess_plotter(x, y, frac=0.1)
    # input: x - array-like, y - array-like, frac - smoothing parameter
    # output: LOWESS smoothed plot
    lowess_smoothed = lowess(y, x, frac=frac)
    smoothed_x = lowess_smoothed[:, 0]
    smoothed_y = lowess_smoothed[:, 1]   
    plt.figure(figsize=(10, 6), dpi=100)
    plt.scatter(x, y, alpha=0.5, label='Data Points')
    plt.plot(smoothed_x, smoothed_y, color='red', label='LOWESS Smoothed', linewidth=2)
    plt.title(title)
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.legend()
    plt.grid(True)
    if save_path:
        plt.savefig(save_path)
    plt.show()


def df_candlestick_plotter(df, title="Candlestick Chart", save_path=None):
    """create candlestick plot for time series data"""
    # usage: df_candlestick_plotter(df)
    # input: df - pandas DataFrame with columns 'Date', 'Open', 'High', 'Low', 'Close'
    # output: candlestick plot
    fig = go.Figure(data=[go.Candlestick(x=df['Date'],
                                         open=df['Open'],
                                         high=df['High'],
                                         low=df['Low'],
                                         close=df['Close'])])
    fig.update_layout(title=title, xaxis_title='Date', yaxis_title='Price')
    if save_path:
        fig.write_image(save_path)
    fig.show()


def df_timeseries_plotter(df, col_date, col_value, title="Time Series Plot", save_path=None):
    """create time series plot"""
    # usage: df_time_series_plotter(df, 'Date', 'Value')
    # input: df - pandas DataFrame, col_date - column name for date, col_value - column name for value
    # output: time series plot
    plt.figure(figsize=(10, 6), dpi=100)
    plt.plot(df[col_date], df[col_value], marker='o', linestyle='-')
    plt.title(title)
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.grid(True)
    if save_path:
        plt.savefig(save_path)
    plt.show()


def df_barplot_plotter(df, col_x, col_y, title="Bar Plot", save_path=None): 
    """create bar plot"""
    # usage: df_barplotter(df, 'col_x', 'col_y')
    # input: df - pandas DataFrame, col_x - column name for x-axis, col_y - column name for y-axis
    # output: bar plot
    plt.figure(figsize=(10, 6), dpi=100)
    sns.barplot(x=df[col_x], y=df[col_y])
    plt.title(title)
    plt.xlabel(col_x)
    plt.ylabel(col_y)
    plt.xticks(rotation=45)
    if save_path:
        plt.savefig(save_path)
    plt.show()


def df_piechart_plotter(df, col_labels, col_values, title="Pie Chart", save_path=None):
    """create pie chart"""
    # usage: df_piechart_plotter(df, 'col_labels', 'col_values')
    # input: df - pandas DataFrame, col_labels - column name for labels, col_values - column name for values
    # output: pie chart
    plt.figure(figsize=(8, 8), dpi=100)
    plt.pie(df[col_values], labels=df[col_labels], autopct='%1.1f%%', startangle=140)
    plt.title(title)
    if save_path:
        plt.savefig(save_path)
    plt.show()


def df_lineplot_plotter(df, col_x, col_y, title="Line Plot", save_path=None):
    """create line plot"""
    # usage: df_lineplotter(df, 'col_x', 'col_y')
    # input: df - pandas DataFrame, col_x - column name for x-axis, col_y - column name for y-axis
    # output: line plot
    plt.figure(figsize=(10, 6), dpi=100)
    sns.lineplot(x=df[col_x], y=df[col_y])
    plt.title(title)
    plt.xlabel(col_x)
    plt.ylabel(col_y)
    plt.grid(True)
    if save_path:
        plt.savefig(save_path)
    plt.show()


def df_violinplot_plotter(df, col_x, col_y, title="Violin Plot", save_path=None):
    """create violin plot"""
    # usage: df_violinplotter(df, 'col_x', 'col_y')
    # input: df - pandas DataFrame, col_x - column name for x-axis, col_y - column name for y-axis
    # output: violin plot
    plt.figure(figsize=(10, 6), dpi=100)
    sns.violinplot(x=df[col_x], y=df[col_y])
    plt.title(title)
    plt.xlabel(col_x)
    plt.ylabel(col_y)
    if save_path:
        plt.savefig(save_path)
    plt.show()


def df_areaplot_plotter(df, col_x, col_y, title="Area Plot", save_path=None):
    """create area plot"""
    # usage: df_area_plotter(df, 'col_x', 'col_y')
    # input: df - pandas DataFrame, col_x - column name for x-axis, col_y - column name for y-axis
    # output: area plot
    plt.figure(figsize=(10, 6), dpi=100)
    plt.fill_between(df[col_x], df[col_y], alpha=0.5)
    plt.title(title)
    plt.xlabel(col_x)
    plt.ylabel(col_y)
    if save_path:
        plt.savefig(save_path)
    plt.show()


def df_scattermatrix_plotter(df, cols_list, title="Scatter Matrix", save_path=None):
    """create scatter matrix plot"""
    # usage: df_scatter_matrix_plotter(df, ['col1', 'col2', 'col3'])
    # input: df - pandas DataFrame, cols_list - list of column names to include in scatter matrix
    # output: scatter matrix plot
    pd.plotting.scatter_matrix(df[cols_list], figsize=(10, 10), diagonal='kde')
    plt.suptitle(title)
    if save_path:
        plt.savefig(save_path)
    plt.show()


def df_lollipop_plotter(df, col_x, col_y, title="Lollipop Plot", save_path=None):
    """create lollipop plot"""
    # usage: df_lollipop_plotter(df, 'col_x', 'col_y')
    # input: df - pandas DataFrame, col_x - column name for x-axis, col_y - column name for y-axis
    # output: lollipop plot
    plt.figure(figsize=(10, 6), dpi=100)
    plt.stem(df[col_x], df[col_y], basefmt=" ", use_line_collection=True)
    plt.title(title)
    plt.xlabel(col_x)
    plt.ylabel(col_y)
    if save_path:
        plt.savefig(save_path)
    plt.show()


def df_ridgeplot_plotter(df, col_x, col_y, title="Ridge Plot", save_path=None):
    """create ridge plot"""
    # usage: df_ridge_plotter(df, 'col_x', 'col_y')
    # input: df - pandas DataFrame, col_x - column name for x-axis, col_y - column name for y-axis
    # output: ridge plot
    plt.figure(figsize=(10, 6), dpi=100)
    sns.violinplot(x=df[col_x], y=df[col_y], scale='width', inner='quartile')
    plt.title(title)
    plt.xlabel(col_x)
    plt.ylabel(col_y)
    if save_path:
        plt.savefig(save_path)
    plt.show()


def df_bubbleplot_plotter(df, col_x, col_y, col_size, title="Bubble Plot", save_path=None):
    """create bubble plot"""
    # usage: df_bubble_plotter(df, 'col_x', 'col_y', 'col_size')
    # input: df - pandas DataFrame, col_x - column name for x-axis, col_y - column name for y-axis, col_size - column name for bubble size
    # output: bubble plot
    plt.figure(figsize=(10, 6), dpi=100)
    plt.scatter(df[col_x], df[col_y], s=df[col_size]*10, alpha=0.5)
    plt.title(title)
    plt.xlabel(col_x)
    plt.ylabel(col_y)
    if save_path:
        plt.savefig(save_path)
    plt.show()


def df_scatterplot_boundingboxes_plotter(df, col_x, col_y, boxes, title="Plot with Bounding Boxes", save_path=None):
    """create plot with bounding boxes"""
    # usage: df_plot_bounding_boxes(df, 'col_x', 'col_y', boxes)
    # input: df - pandas DataFrame, col_x - column name for x-axis, col_y - column name for y-axis, boxes - list of bounding box coordinates
    # output: plot with bounding boxes
    plt.figure(figsize=(10, 6), dpi=100)
    plt.scatter(df[col_x], df[col_y], alpha=0.5)
    for box in boxes:
        x1, y1, x2, y2 = box
        plt.gca().add_patch(plt.Rectangle((x1, y1), x2 - x1, y2 - y1,
                                          fill=False, edgecolor='red', linewidth=2))
    plt.title(title)
    plt.xlabel(col_x)
    plt.ylabel(col_y)
    if save_path:
        plt.savefig(save_path)
    plt.show()