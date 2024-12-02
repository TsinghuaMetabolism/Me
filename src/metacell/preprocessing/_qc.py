import pandas as pd
from typing import Union, Tuple

# Calculate quality control metrics.
def calculate_qc_metrics() -> Union[Tuple[pd.DataFrame, pd.DataFrame], None]:
    pass

# Filter cell outliers based on counts and the number of genes expressed.
def filter_cells():
    pass

# Filter metabolic feature based on number of cells or intensity.
def filter_metabolites():
    pass


# Principal component analysis.
def pca():
    pass


# Subsample to a fraction of the number of observations.
def subsample():
    pass

# Downsample counts from count matrix.
def downsample_counts():
    pass


'''
Multiplet refers to two or more cells that have not benn completely separated during the isolation process and 
are captured and analyzed as a single unit. This results in the analysis containing mixed information from two or more cells,
thereby affecting the accuracy of the experimental data.
'''
#  Detect and remove multiplets from the data.
def remove_multiplets():
    pass

