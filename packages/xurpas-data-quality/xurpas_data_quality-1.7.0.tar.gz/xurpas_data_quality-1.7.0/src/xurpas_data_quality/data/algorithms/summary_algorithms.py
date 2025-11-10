import numpy as np
import pandas as pd


def compute_histogram(series: pd.Series,
                      name:str="histogram")-> dict:
    summary = {}
    if len(series) == 0:
        return {name: []}
    
    bins = np.histogram_bin_edges(series, bins='auto')
    summary[name] = np.histogram(series, bins=bins)
    return summary

def get_percentage(divisor: int, dividend: int):
    if dividend != 0:
        return (divisor / dividend) * 100
    else:
        return 0