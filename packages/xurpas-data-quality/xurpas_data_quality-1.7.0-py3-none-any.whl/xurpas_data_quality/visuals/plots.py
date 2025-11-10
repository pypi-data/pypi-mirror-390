

import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

from wordcloud import WordCloud

from xurpas_data_quality.visuals.utils import error_handler, plot_to_base64



@error_handler
@plot_to_base64
def create_tiny_histogram(histogram: tuple, **kwargs):
    counts, bins = histogram
    fig, ax = plt.subplots()

    bin_width = bins[1] - bins[0]
    bin_centers = bins[:-1] + bin_width / 2
    ax.bar(bin_centers, counts, width=bin_width)

    ax.set(frame_on=False)
    ax.set_yticks([])

    
    return fig

@error_handler
@plot_to_base64
def create_horizontal_histogram(value_counts: dict, **kwargs):
    fig, ax = plt.subplots()
    ax.barh(list(value_counts.keys()), list(value_counts.values()))
    ax.set(frame_on=False)
    ax.set_xticks([])

    return fig

@error_handler
@plot_to_base64
def create_histogram(histogram: tuple, **kwargs):
    try:
        counts, bins = histogram
        fig, ax = plt.subplots(figsize=(12,4))

        bin_width = bins[1] - bins[0]
        bin_centers = bins[:-1] + bin_width / 2
        ax.bar(bin_centers, counts, width=bin_width)
    except:
        fig, ax = plt.subplots()
        ax.set(frame_on=False)
        ax.set_yticks([])
        ax.set_xticks([])
    return fig

@error_handler
@plot_to_base64
def create_word_cloud(value_counts: dict, **kwargs):        
    fig = plt.figure()
    if not isinstance(value_counts, list):
        value_counts = [value_counts]

    try:
        for i, series_data in enumerate(value_counts):
                word_dict = series_data.to_dict()
                wordcloud = WordCloud(
                    background_color="white", random_state=123, width=300, height=200, scale=2
                ).generate_from_frequencies(word_dict)

                ax = fig.add_subplot(1, len(value_counts), i + 1)
                ax.imshow(wordcloud)
                ax.axis("off")
    
    except Exception as e:
         print(f"Error in creating plot: {e}")
        
    return fig

@error_handler
@plot_to_base64
def create_tiny_counts(series, **kwargs):
    # Assuming 'df' is your DataFrame and 'Pclass' is your column

    fig, ax = plt.subplots()
    series.plot(kind='barh', ax=ax)

    return fig

@error_handler
@plot_to_base64
def create_heatmap(df: pd.DataFrame, **kwargs):
    # Create a figure and a set of subplots
    fig, ax = plt.subplots()
    plt.box(False)
    # Create the heatmap
    heatmap = ax.imshow(df, cmap='RdYlBu', interpolation='nearest', vmin=-1.0, vmax=1.0)

    # Set the column names as x-axis labels
    ax.set_xticks(np.arange(len(df.columns)))
    ax.set_xticklabels(df.columns)

    # Set the column names as y-axis labels
    ax.set_yticks(np.arange(len(df.columns)))
    ax.set_yticklabels(df.columns)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    # Create a colorbar
    cbar = plt.colorbar(heatmap)
    cbar.outline.set_visible(False)

    return fig

@error_handler
@plot_to_base64
def create_distribution_plot(column: pd.Series, subplot_size=5, **kwargs):
    fig, axs = plt.subplots(ncols=2, figsize=(2*subplot_size, subplot_size))

    axs[0].boxplot(column)

    axs[1].violinplot(column)

    fig.suptitle(f'{column.name} distribution')

    return fig

@error_handler
@plot_to_base64
def create_interaction_plot(x: pd.Series, y: pd.Series, **kwargs):
    fig = plt.figure(figsize=(8,4))
    plt.scatter(x,y,edgecolor="black", linewidth=0.25)

    return fig

@error_handler
@plot_to_base64
def create_missing_bar_plot(df: pd.DataFrame, **kwargs):
    non_null_counts = df.count()
    fig, ax = plt.subplots(figsize=(12,4))
    # create a bar chart
    ax.bar(non_null_counts.index, non_null_counts.values)
    ax.set(frame_on=False)
    plt.xticks(rotation=45)

    return fig

@error_handler
@plot_to_base64
def create_distribution_from_dataframe(df: pd.DataFrame, **kwargs):
    if 'employee_code' in df.columns:
        df = df.drop('employee_code', axis=1)

    fig = plt.figure()
    boxplot = df.boxplot(figsize=(15,3))
    return fig

