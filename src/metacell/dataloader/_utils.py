import pybaselines
import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde
from scipy.linalg import LinAlgError
from typing import Union, Literal, Tuple, Any
from .scMetData import scMetData
from ._plotting import plt_baseline_correction

def get_index(lst: list = None, item: str = ''):
    """
    Given a list, get the index where the value equals the item.
    """
    return [index for (index, value) in enumerate(lst) if value == item]


def get_tic_from_mzml(spectrum):
    # Use the correct access key.
    if spectrum.metaValueExists("MS:1000285"):
        # Ensure the conversion to float.
        return float(spectrum.getMetaValue("MS:1000285"))
        # Use a more generic key name.
    elif spectrum.metaValueExists("total ion current"):
        # Convert to float.
        return float(spectrum.getMetaValue("total ion current"))
    else:
        return None


def identify_intensity_threshold(intensity_data):
    """calculate the mean and median of all data in intensity_data"""
    all_intensities = np.concatenate(intensity_data)
    return np.mean(all_intensities), np.median(all_intensities)


def double_scan_feature_integration(mz_data: list,
                                    intensity_data: list,
                                    mz: float,
                                    ppm: int=10,
                                    mode: Literal["sum", "max", "nearest"]="nearest",) -> Tuple[Any, pd.DataFrame]:
    """
    2-step scanning to extract the mz and its corresponding intensity:
    - During the first scan, extract the corresponding data based on the theoretical m/z and determine the actual m/z using kernel density estimation.
    - During the second scan, extract the m/z value and the corresponding intensity for each data point using the actual m/z value.

    Returns
    -------
    mz_intensity: A data frame composed of mz, intensity, and number.
    """
    # (1) Use a 20 pm range for the first scan and confirm the actual Feature_mz axis with the median.
    mz_intensity = feature_integration(mz_data, intensity_data, mz, ppm=20)

    range_number = max(10000, len(mz_intensity['mz']))
    mz_density_center = identify_density_center_byKDE(mz_intensity['mz'], range_number=range_number)

    # (2) In the second scan, filter out all data points that meet the criteria of mz and its intensity combination in the data frame.
    # Use a 10 ppm range as the final scanning range.
    mz_intensity = feature_integration(mz_data, intensity_data, mz_density_center, ppm=ppm, mode=mode)
    return mz_density_center, mz_intensity



# === Extract mz and its corresponding intensity from each data point and ultimately integrate them into a single dataframe。
def feature_integration(mz_data: list,
                        intensity_data: list,
                        mz: float,
                        ppm: int=10,
                        mode: Literal["sum", "max", "nearest"]="nearest",
                        show_number_list: bool=False) -> pd.DataFrame:
    """
    Extract the mz and its corresponding intensity from each data point that meet the requirements,
    and ultimately integrate them into a single data frame.

    Parameters:
    ----------
    mz_data : list
        A list of numpy arrays containing mz values.
    intensity_data : list
        A list of numpy arrays containing intensity values.
    mz : float
        The target mz value to find in the data.
    mz_threshold_methods : int or str, optional
        The method to calculate the mz threshold, default is 10.
    mode : str, optional
        The mode of integration ('nearest', 'sum', 'max'), default is 'nearest'.
        - If the mode is set to nearest, it means that when multiple qualifying values appear within the scan range,
        the value closest to the mz will be selected as the final result.
        - If the mode is set to sum, the same applies, but the intensity will be the sum of all the values.
        - If the mode is set to max, the same applies, but the intensity will be the maximum among all the values.
    show_number_list : bool, optional
    Whether to show the number of data points returned by this function, default is False.
    Returns:
    -------
    pd.DataFrame
        A dataframe containing mz, intensity and number.
    """
    mz_list = []
    intensity_list = []
    number_list = []

    for mz_array, intensity_array in zip(mz_data, intensity_data):
        mz_lower, mz_upper = mz_threshold(mz, methods=ppm)
        valid_indices = (mz_array >= mz_lower) & (mz_array <= mz_upper)
        valid_mzs = mz_array[valid_indices]

        if valid_mzs.size == 0:
            mz_list.append(None)
            intensity_list.append(None)
            number_list.append(0)
        else:
            nearest_index = np.argmin(np.abs(valid_mzs - mz))
            nearest_mz = valid_mzs[nearest_index]
            number_list.append(valid_mzs.size)

            if mode == "sum":
                total_intensity = np.sum(intensity_array[valid_indices])
                intensity_list.append(total_intensity)
            elif mode == "max":
                max_intensity = np.max(intensity_array[valid_indices])
                intensity_list.append(max_intensity)
            else:  # mode == "nearest"
                nearest_intensity = intensity_array[valid_indices][nearest_index]
                intensity_list.append(nearest_intensity)

            mz_list.append(nearest_mz)
    if show_number_list:
        df = pd.DataFrame({'mz': mz_list, 'intensity': intensity_list, 'number': number_list})
    else:
        df = pd.DataFrame({'mz': mz_list, 'intensity': intensity_list})
    return df


def mz_threshold(mz: float,
                 methods: Union[str, float]=10):
    """
    Description:
    ------------
    Given mz and mz threshold methods, calculate the mz_upper and mz_lower ranges.

    Parameters:
    ----------
    mz : float
        The mz value to calculate the threshold for.
    methods : int or str, optional
        The method to calculate the mz threshold. Default is 10.
        If 'TypeI', use specific rules based on mz value:
            - When mz <= 400, the mz fluctuation range is a fixed 0.003 Da.
            - When mz > 400, the mz fluctuation range is 10 ppm.
        If an integer N, the mz fluctuation range is N ppm.

    Returns:
    -------
    tuple of float
        A tuple containing the mz_lower and mz_upper ranges.
    """
    if methods == "TypeI":
        if mz <= 400:
            # 0.003
            return mz - 0.003, mz + 0.003
        else:
            # 10ppm
            return mz - mz * 0.00001, mz + mz * 0.00001
    else:
        ppm = methods * 0.000001
        return mz - mz * ppm, mz + mz * ppm


#  === use kernel density estimation (KDE) to calculate the density. ===
def identify_density_center_byKDE(mz_list: np.array,
                                  range_number: int = 10000) -> float:
    """
    Description:
    ------------
    use kernel density estimation (KDE) to calculate the density,
    determine the density center within the range, and plot the KDE graph.

    Return:
    -------
    density_center(float)z: the density center within the range.

    """
    # use kernel density estimation (KDE) to calculate the density.
    kde = gaussian_kde(mz_list.dropna().values)

    # create an array of mz values over a broad range for assessing density
    mz_range = np.linspace(mz_list.min(), mz_list.max(), range_number)
    # calculate the density for each point within this range.
    density_values = kde.evaluate(mz_range)
    # obtain the density center within this range.
    density_center = float(mz_range[np.argmax(density_values)])
    return density_center


# === baseline correction by step and confirmation of valid signal index based on S/N threshold ===
def sliding_window_baseline_correction(data: pd.Series,
                                       times: pd.Series,
                                       sn_ratio: int,
                                       output2figures: str=None,
                                       window_size: int=100,
                                       p: float=0.5):
    """
    Baseline correction by step and confirmation of valid signal index based on Signal-to-Noise ratio (SN) threshold.

    Params:
    ----------
    data: data signal to be processed.
    times: data times.
    sn_ratio: avg +- sn_ratio * var.
    output2Figures: output path to Figures.
    window_size: set the data scan window size.
    p: Penalty weight factor.

    Returns:
    -------
    ind: The index of all data points that meet the requirements of the data signal.
    df:  A data frame that combines raw data, data baselines, and baseline-corrected data.

    """
    # segment the data according to the window size.
    segments = segment_data(data, window_size)

    # get baselines
    baselines = get_baselines(segments, p=p, max_iter=100)

    # flatten the list of baselines
    total_baselines = [baseline for segment_baselines in baselines for baseline in segment_baselines]

    df = pd.DataFrame({'baselines': total_baselines, 'data': data, 'time': times})

    # 1. If baselines are NaN or baselines are greater than or equal to data, then signal equals 0.
    # 2. Otherwise, signal = data - baselines.
    df['signal'] = np.where((df['baselines'].isna()) | (df['baselines'] >= df['data']), 0, df['data'] - df['baselines'])

    # Calculate the threshold based on the baseline mean and standard deviation.
    mph = calculate_baselines_threshold(df['signal'], multiplier=sn_ratio)

    # Select the index of data points greater than the minimum peak value.
    # ind = np.array(df[df['signal'] > mph].index)

    # plt_baseline_correction outputs a plot showing the data before and after baseline correction.
    if output2figures is not None:
        plt_baseline_correction(df['time'], df['data'], df['baselines'], df['signal'], mph, output2figures)

    return df


# === Slice the data into segments of fixed-length windows. ===
def segment_data(data: pd.Series,
                 window_size: int=100):
    """
    Slice the data into segments of fixed-length windows.
    """
    segments = []
    for i in range(0, len(data), window_size):
        segment = data[i:i + window_size]
        segments.append(segment)
    # the length of last segment may < 2, which could cause issues in subsequent analyses.
    # therefore, we merge segments[-2] and segments[-1].
    segments[-2] = pd.concat([segments[-2], segments[-1]], ignore_index=True)
    segments.pop()
    return segments


# === get baselines from segments ===
def get_baselines(segments: list,
                  p: float=0.5,
                  max_iter: int=100):
    """
    To handle segments containing NaN values,
    we need to add some logic in the get_baselines function to check if each segment is entirely NaN values.
    If it is, then set the corresponding baseline directly to NaN.
    If the segment contains valid data, use only this data to calculate the baseline.
    After calculation, place the NaN values back into their original positions.

    Return:
    -------
    baselines:
    """
    baselines = []
    for segment in segments:
        # Check if 80% or more values are NaN
        if np.isnan(segment).sum() >= 0.8 * len(segment):
            # If 80% or more values are NaN, append a baseline of NaNs
            baseline = np.full_like(segment, np.nan)
        else:
            # Find the indices of non-NaN values
            valid_indices = ~np.isnan(segment)
            valid_data = segment[valid_indices]

            # Calculate the baseline using only non-NaN values
            median_value = np.median(valid_data)
            segment[np.isnan(segment)] = median_value / 2

            try:
                baseline_non_nan, params = pybaselines.spline.mixture_model(segment, p=p, max_iter=max_iter)
            except LinAlgError:
                baseline_non_nan = np.full(len(segment), median_value)
                #baselines.append(baseline)
                print("Warning: LinAlgError encountered. Using median value as baseline.")
                #continue

            # Create a new baseline array filled with NaNs
            baseline = np.full_like(segment, np.nan)
            # Replace non-NaN positions with calculated baseline values
            baseline[valid_indices] = baseline_non_nan[valid_indices]

        baselines.append(baseline)
    return baselines

# === Calculate the threshold based on the baseline mean and standard deviation. ===
def calculate_baselines_threshold(baseline, multiplier=5) -> float:
    """
    Description:
    -----------
    Calculate the threshold based on the baseline mean and standard deviation.

    Parameters:
    -----------
    - baseline(array)
    - multiplier(int or float)

    Returns:
    --------
    threshold
    """
    # Calculate Q1 (5th percentile) and Q3 (95th percentile)
    Q1 = np.percentile(baseline, 5)
    Q3 = np.percentile(baseline, 95)
    # Remove outliers: keep only data points between Q1 and Q3
    filtered_baseline = baseline[(baseline >= Q1) & (baseline <= Q3)]
    # Calculate the mean and standard deviation of the filtered baseline
    mean_baseline = np.mean(filtered_baseline)
    std_baseline = np.std(filtered_baseline)

    # Calculate the threshold
    threshold = mean_baseline + multiplier * std_baseline

    return threshold


# === Detect peaks in data based on their amplitude and other features. ===
def detect_peaks(x, mph=None, mpd=1, threshold=0, edge='rising',
                 kpsh=False, valley=False):
    """
    Description:
    ------------
    Detect peaks in data based on their amplitude and other features.

    Parameters
    ----------
    x : 1D array_like
        data.
    mph : {None, number}, optional (default = None)
        detect peaks that are greater than minimum peak height.
    mpd : positive integer, optional (default = 1)
        detect peaks that are at least separated by minimum peak distance (in
        number of data).
    threshold : positive number, optional (default = 0)
        detect peaks (valleys) that are greater (smaller) than `threshold`
        in relation to their immediate neighbors.
    edge : {None, 'rising', 'falling', 'both'}, optional (default = 'rising')
        for a flat peak, keep only the rising edge ('rising'), only the
        falling edge ('falling'), both edges ('both'), or don't detect a
        flat peak (None).
    kpsh : bool, optional (default = False)
        keep peaks with same height even if they are closer than `mpd`.
    valley : bool, optional (default = False)
        if True (1), detect valleys (local minima) instead of peaks.
    Returns
    -------
    ind : 1D array_like
        indeces of the peaks in `x`.
    Notes
    -----
    The detection of valleys instead of peaks is performed internally by simply
    negating the data: `ind_valleys = detect_peaks(-x)`

    The function can handle NaN's
    See this IPython Notebook [1]_.
    References
    ----------
    "Marcos Duarte, https://github.com/demotu/BMC"
    [1] http://nbviewer.ipython.org/github/demotu/BMC/blob/master/notebooks/DetectPeaks.ipynb
    """

    x = np.atleast_1d(x).astype('float64')
    if x.size < 3:
        return np.array([], dtype=int)
    if valley:
        x = -x
    # find indexes of all peaks
    dx = x[1:] - x[:-1]
    # handle NaN's
    indnan = np.where(np.isnan(x))[0]
    if indnan.size:
        x[indnan] = np.inf
        dx[np.where(np.isnan(dx))[0]] = np.inf
    ine, ire, ife = np.array([[], [], []], dtype=int)
    if not edge:
        ine = np.where((np.hstack((dx, 0)) < 0) & (np.hstack((0, dx)) > 0))[0]
    else:
        if edge.lower() in ['rising', 'both']:
            ire = np.where((np.hstack((dx, 0)) <= 0) & (np.hstack((0, dx)) > 0))[0]
        if edge.lower() in ['falling', 'both']:
            ife = np.where((np.hstack((dx, 0)) < 0) & (np.hstack((0, dx)) >= 0))[0]
    ind = np.unique(np.hstack((ine, ire, ife)))
    # handle NaN's
    if ind.size and indnan.size:
        # NaN's and values close to NaN's cannot be peaks
        ind = ind[np.in1d(ind, np.unique(np.hstack((indnan, indnan - 1, indnan + 1))), invert=True)]
    # first and last values of x cannot be peaks
    if ind.size and ind[0] == 0:
        ind = ind[1:]
    if ind.size and ind[-1] == x.size - 1:
        ind = ind[:-1]
    # remove peaks < minimum peak height
    if ind.size and mph is not None:
        ind = ind[x[ind] >= mph]
    # remove peaks - neighbors < threshold
    if ind.size and threshold > 0:
        dx = np.min(np.vstack([x[ind] - x[ind - 1], x[ind] - x[ind + 1]]), axis=0)
        ind = np.delete(ind, np.where(dx < threshold)[0])
    # detect small peaks closer than minimum peak distance
    if ind.size and mpd > 1:
        ind = ind[np.argsort(x[ind])][::-1]  # sort ind by peak height
        idel = np.zeros(ind.size, dtype=bool)
        for i in range(ind.size):
            if not idel[i]:
                # keep peaks with the same height if kpsh is True
                idel = idel | (ind >= ind[i] - mpd) & (ind <= ind[i] + mpd) \
                       & (x[ind[i]] > x[ind] if kpsh else True)
                idel[i] = 0  # Keep current peak
        # remove the small peaks and sort back the indexes by their occurrence
        ind = np.sort(ind[~idel])

    return ind


def extract_mz_intensity_from_scm_events(mdata: scMetData):
    """
    Extract m/z and intensity data from single-cell metabolomics events.

    Parameters:
    - scMetEvent: List or array-like structure containing indices of metabolomics events.
    """

    scm_events_index = np.array(mdata.scm_events.index)

    scan_id = pd.Series(np.array(mdata.scm_events['scan_Id']))
    cellnumber = pd.Series(np.array(mdata.scm_events['CellNumber']))
    mz_data = [mdata.mz_data[i] for i in scm_events_index]
    intensity_data = [mdata.intensity_data[i] for i in scm_events_index]

    scm_scan_id = scan_id.repeat([len(arr) for arr in mz_data]).reset_index(drop=True)
    scm_cellnumber = cellnumber.repeat([len(arr) for arr in mz_data]).reset_index(drop=True)
    scm_mz_data = pd.Series(np.concatenate(mz_data))
    scm_intensity_data = pd.Series(np.concatenate(intensity_data))

    scm_mz_intensity = pd.DataFrame({
        'scan_Id': scm_scan_id,
        'mz': scm_mz_data,
        'intensity': scm_intensity_data,
        'CellNumber': scm_cellnumber
    })
    scm_mz_intensity = scm_mz_intensity.sort_values(by='mz', ascending=True).reset_index(drop=True)

    return scm_mz_intensity


def filter_intensity(data: pd.DataFrame, intensity_threshold: float) -> pd.DataFrame:
    """
    筛选高强度的 m/z 数据点。
    Args:
        data (pd.DataFrame): 输入数据框，包含intensity列。
        intensity_threshold (float): 强度筛选阈值。
    Returns:
        pd.DataFrame: 筛选后的数据。
    """
    return data[data['intensity'] >= intensity_threshold].copy()
