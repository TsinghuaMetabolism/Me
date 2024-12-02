import math
import os
import numpy as np
import matplotlib.pyplot as plt

# === Visualize the results of baseline correction. ===
def plt_baseline_correction(x, y1, y2, y3, mph, output_dir):
    """
    Description:
    -----------
    Visualize the results of baseline correction.

    Parameter:
    ----------
    y1: Original data.

    y2: Baseline.

    y3: Data after baseline correction.

    height: Minimum peak value.

    output: result path.

    Return:
    -------
    """
    width = math.ceil(max(x)) * 6
    if width > 910:
        width = 910
    result_path1 = os.path.join(output_dir, 'plt_baselines.pdf')
    result_path2 = os.path.join(output_dir, 'plt_baselines_correction.pdf')

    # === 1) Plot a schematic diagram of the baseline calibration before correction. ===
    # Customize the width of plt.figure based on the number of indices.
    plt.figure(figsize=(width, 6))
    plt.xlim(min(x), max(x)+0.2)
    # Plot a white line to ensure the y-axis starts from 0.
    plt.axhline(0, color='white', linewidth=0.5)
    plt.plot(x, y1, color="black", linewidth=2.0, linestyle="solid", label="Raw data")
    plt.plot(x, y2, color="red", linewidth=2.0, linestyle="--", label="Baselines")
    plt.xticks(np.arange(0, math.floor(max(x)) + 1, 1.0))  # Add x-axis tick marks.
    if output_dir is not None:
        plt.savefig(result_path1)
        plt.close()
    plt.show()

    # === 2) Plot the calibration diagram of valid signals after baseline correction. ===
    plt.figure(figsize=(width, 6))
    plt.xlim(min(x), max(x)+0.2)
    plt.plot(x, y3, color="blue", linewidth=2.0, linestyle="solid", label="Signal")
    plt.plot(x, np.full(len(x), mph), color="orange", linewidth=2.0, linestyle="--", label="Minimum peaks")
    plt.xticks(np.arange(0, math.floor(max(x)) + 1, 1.0))  # Add x-axis tick marks.
    if output_dir is not None:
        plt.savefig(result_path2)
        plt.close()
    plt.show()

def plt_scm_events(x, data, scm_events_index, output_dir, figs_name ="plt_scm_events.pdf"):
    """
    Visualize the single-cell events annotated by marker.

    :param data: Original data.
    :param scm_events_index: Index of single-cell events.
    :param output_dir: path to output dir
    :param figs_name: figures name.
    :return: None
    """
    result_path = os.path.join(output_dir, figs_name)
    width = math.ceil(max(x)) * 6
    if width > 910:
        width = 910

    # 1) Plot the calibration of single-cell peaks annotated by TIC.
    plt.figure(figsize=(width, 6))
    plt.xlim(min(x), max(x) + 0.2)
    plt.plot(x, data, color="blue", linewidth=2.0, linestyle="solid", label="Raw data")
    plt.plot(x[scm_events_index], data[scm_events_index], "o", color="red", label="SCM events")
    plt.xticks(np.arange(0, math.ceil(max(x)) + 1, 1.0))  # Add x-axis tick marks.
    plt.savefig(result_path)
    plt.close()

def plt_merged_scm(x, data, scm_events_index, scm_events_only_index, output_dir):
    """
    Description:
    -----------
    Visualize the single-cell peaks annotated by merged scMetEvent.

    Parameter:
    ----------
    data(df)
    merged_scMetEvent_index(array)
    scMetEvent_only_index(dict) wwwwwww
    output_dir(str)

    Returns
    -------
    None
    """
    # Define the output path for the plot
    result_path = os.path.join(output_dir, 'plt_merged_scMetEvent.pdf')
    # Calculate the figure width based on the data range, with a maximum width limit
    custom_colors = ['#FFC125', '#9ACD32', '#7B68EE', '#EE7942', '#6CA6CD']
    width = min(math.ceil(max(x)) * 6, 910)

    # Create the figure with calculated dimensions
    plt.figure(figsize=(width, 6))
    plt.xlim(min(x), max(x) + 0.2)

    # Plot the raw TIC data
    plt.plot(x, data, color="blue", linewidth=2.0, linestyle="solid", label="Raw TIC data")

    # Plot single-cell events annotated by multiple strategies.
    plt.plot(x[scm_events_index], data[scm_events_index], "o", color="#B22222", label="scMetEvent annotated by multiple strategies.")

    for i, (key, value) in enumerate(scm_events_only_index.items()):
        # Plot single-cell events annotated by cell marker only
        plt.plot(x[value], data[value], "o", color=custom_colors[i], label=f"scMetEvent annotated by {key} only")

    # set x-axis ticks
    plt.xticks(np.arange(0, math.ceil(max(x)) + 1, 1.0))
    # Add legend to the plot
    plt.legend()
    # Save the plot to the specified output directory
    plt.savefig(result_path)
    plt.close()


def plt_cell_type_annotation():
    pass

