# -*- coding: utf-8 -*-
# Author: Quentin Baghi 2021 <quentin.baghi@protonmail.com>
import pickle
import h5py
import numpy as np
import logging
from . import psd
from . import StochasticBackgroundResponse, Response
from scipy.signal.windows import blackmanharris, nuttall
from scipy.signal import get_window
logger = logging.getLogger(__name__)


def get_tdi_data(tdi_file, skip=200, skip_end=0, fs=0.2):
    """
    Function that loads and concatenate TDI data.

    Parameters
    ----------
    noise_tdi_file : str, 
        to use a noise data path, by default None
    skip : int, optional
        number of time samples to skip at the beginning of TDI data,
        by default 200
    skip_end : int, optional
        number of time samples to skip at the end of TDI data,
        by default 100
        
    Returns
    -------
    t : ndarray
        Array of time stamps
    xyz_data : ndarray
        TDI data of size n_data x 3
    fs : float
        The sampling frequency of the data
        
    """

    # Get TDI data
    hdf5 = h5py.File(tdi_file, 'r')
    if 'x2' in hdf5.keys():
        x2 = hdf5['x2'][()][skip:-skip_end]
        y2 = hdf5['y2'][()][skip:-skip_end]
        z2 = hdf5['z2'][()][skip:-skip_end]
    elif 'X2' in hdf5.keys():
        x2 = hdf5['X2'][()][skip:-skip_end]
        y2 = hdf5['Y2'][()][skip:-skip_end]
        z2 = hdf5['Z2'][()][skip:-skip_end]

    # Get the sampling frequency out of the data
    try:
        t = hdf5['t'][()][skip:-skip_end]
        fs = 1 / np.absolute(t[1]-t[0])
    except KeyError:
        print("No time information found!")
        t = np.arange(0, len(x2)) / fs

    hdf5.close()

    return t, np.array([x2, y2, z2]).T, fs


def load_simulation_data(noise_tdi_file, 
                         gw_tdi_file=None,
                         gal_tdi_file=None,
                         signal_scale=1.,
                         noise_scale=1.,
                         skip=200,
                         skip_end=100,
                         n_data=None,
                         breakup=False, central_freq=281600000000000.0):
    """
    Function that loads and concatenate TDI data from
    file paths indicated in a configuration file.

    Parameters
    ----------
    noise_tdi_file : str, 
        to use a noise data path, by default None
    gw_tdi_file : str, optional
        to use a signal data path, by default None
    signal_scale : float, optional
        re-scaling to apply to the GW signal, by default 1.0
    noise_scale : _type_, optional
        re-scaling to apply to the noise, by default 1.0
    skip : int, optional
        number of time samples to skip at the beginning of TDI data,
        by default 200
    skip_end : int, optional
        number of time samples to skip at the end of TDI data,
        by default 100
    n_data : float, optional
        if provided, the output will have minimal length n_data,
        by default None
    breakup : bool, optional
        if True, outputs noise and signal data separatly, by default False
    central_freq : float, optional
        central laser frequency used in TDI noise, by default 281600000000000.0

    Returns
    -------
    t : ndarray
        Array of time stamps
    xyz_data : ndarray
        TDI data of size n_data x 3
    fs : float
        The sampling frequency of the data
    """
    # Data loading
    # ------------
    xyz = {}
    # Get noise TDI Data
    t, xyz["noise"], fs_noise = get_tdi_data(noise_tdi_file, skip=skip, skip_end=skip_end)
    # Apply rescaling
    xyz["noise"] *= noise_scale / central_freq
    
    # Get signal TDI Data
    if gw_tdi_file is not None:
        t, xyz["signal"], fs_signal = get_tdi_data(gw_tdi_file, skip=skip, skip_end=skip_end)
        if (fs_noise != fs_signal):
            raise ValueError("Datasets should have the same sampling frequency")
        # Apply rescaling
        xyz["signal"] *= signal_scale
        
    if gal_tdi_file is not None:
        t, xyz["galaxy"], fs_gal = get_tdi_data(gal_tdi_file, skip=skip, skip_end=skip_end)

    # Size of the analyzed segment
    if n_data is None:
        ns = np.min([xyz[key].shape[0] for key in xyz.keys()])
    else:
        size_list = [xyz[key].shape[0] for key in xyz.keys()].append(n_data)
        ns = np.min(size_list) 
    
    # Resize the data if needed so that all components have the same length
    xyz_data = sum([xyz[key][0:ns] for key in xyz.keys()])

    # Prepare outputs
    # if (breakup) & ((gw_tdi_file is not None) | (gal_tdi_file is not None)):
    #     return t[0:ns], (xyz[key][0:ns] for key in xyz.keys()), fs
    if (breakup) & (gw_tdi_file is not None) & (gal_tdi_file is None):
        return t[0:ns], (xyz["noise"][0:ns], xyz["signal"][0:ns]), fs_noise
    elif (breakup) & (gw_tdi_file is not None) & (gal_tdi_file is not None):
        return t[0:ns], (xyz["noise"][0:ns], xyz["signal"][0:ns], xyz["galaxy"][0:ns]), fs_noise
    elif (breakup) & (gw_tdi_file is None) & (gal_tdi_file is not None):
        return t[0:ns], (xyz["noise"][0:ns], xyz["galaxy"][0:ns]), fs_noise
    
    return t, xyz_data, fs_noise


def get_window_function(window_type):
    """
    From string to 

    Parameters
    ----------
    window_type : str
        window name

    Returns
    -------
    wd_func : callable
        window function

    Raises
    ------
    ValueError
        if window_type is unknown
    """

    if window_type.lower() == 'rectangular':
        wd_func = np.ones
    elif window_type.lower() == 'blackman':
        wd_func = np.blackman
    elif window_type.lower() in ['bh92', 'blackmanharris']:
        wd_func = blackmanharris
    elif window_type.lower() == 'hanning':
        wd_func = np.hanning
    elif window_type.lower() == 'nuttall':
        wd_func = nuttall
    else:
        return lambda nx: get_window(window_type, nx)

    return wd_func


def time_to_frequency(xyz_data, fs=None, fmin=1e-4, fmax=2.9e-2,
                      size_min=100, size_max=15000, averaging="SmoothAdaptive",
                      smoothingbandwidth=5e-5, nperseg=None, wisdom=None,
                      window_type="bh92", normalize_by_nenbw=True):
    """
    Convert time series to frequency domain data (averaged periodogram)

    Parameters
    ----------
    xyz_data : ndarray
        TDI time series, size n_data x 3
    fs : _type_, optional
        Sampling frequency in Hz, by default None
    fmin : float, optional
        Minimum analysis frequency, by default 1e-4
    fmax : float, optional
        Maximum analysis frequency, by default 2.9e-2
    size_min : int, optional
        Number of frequency bins in the smallest segment, by default 100
    size_max : int, optional
        Number of frequency bins in the largest segment, by default 15000
    averaging : str, optional
        Type of periodogram smoothing, by default "SmoothAdaptive"
    smoothingbandwidth : _type_, optional
        Banwidth of the smoothing in Hz, if averaging type is "smooth". By default 5e-5
    nperseg : int, optional
        Size of averaged semgents if the averaging type is "welch", by default None
    wisdom : _type_, optional
        pyfftw wisdom object (computational plan memory), by default None
    window_type : str, optional
        Tapering window, by default "bh92"

    Returns
    -------
    fper : float
        frequency bins of the smoothed periodogram, size nf
    per_xyz_smoothed : ndarray
        periodogram matrix, size nf x 3 x 3
    k_seg : ndarray
       effective number of frequency bins in each segment.

    Raises
    ------
    TypeError
        _description_
    ValueError
        _description_
    ValueError
        _description_
    """

    if fs is None:
        raise TypeError("The sampling frequency 'fs' is needed. ")
    # Size of input time series
    ns = xyz_data.shape[0]
    # To build the frequency grid
    if nperseg is None:
        nperseg = int(24 * 3600 * fs)

    # Choose window
    if isinstance(window_type, str):
        wd_func = get_window_function(window_type)
    else:
        wd_func = window_type

    if averaging.lower() == "welch":
        # Size of segments in which we will devide the data
        nperseg = int(24*3600*fs)
        # Number of segments
        segment_sizes = ns // nperseg
        # Welch periodogram frequencies
        fper = np.fft.fftfreq(nperseg) * fs
        # Compute periodograms
        per_xyz_smoothed = psd.welch_matrix(
            xyz_data.T, fs, nperseg, wd_func=wd_func)

    elif averaging.lower() == "welchadaptive":
        f_segments = np.array([0, 1e-3, 1e-2, 1e-1, 1.0])
        d_max = 2 * 24 * 3600
        d_min = 1000
        n_segs = len(f_segments)-1
        segment_durations = d_max * \
            (d_min / d_max) ** (np.arange(0, n_segs)/(n_segs-1))
        segment_sizes = (segment_durations * fs).astype(int)
        fper, per_xyz_smoothed, segment_sizes = psd.welch_matrix_adaptive(
            xyz_data.T, fs, segment_sizes, f_segments, wd_func=wd_func, output_freqs=True)

    elif averaging.lower() == "smooth":
        # Compute full periodogram
        per_xyz_data = psd.periodogram_matrix(xyz_data.T, fs, wd_func=wd_func,
                                              wisdom=wisdom)
        # Start and end frequencies
        df = fs / ns
        k_min = int(fmin/ df)
        k_max = int(fmax / df)
        band_size = k_max - k_min + 1
        # All segments have the same size
        size = int(smoothingbandwidth / df)
        # Number of segments
        n_seg = band_size // size
        segment_sizes = np.ones(n_seg) * size
        # Compute the smoothed spectrum
        i_mid, per_xyz_smoothed = psd.smooth(per_xyz_data, k_min, segment_sizes)
        # Segment middle frequencies
        fper = i_mid * df

    elif averaging.lower() == "smoothadaptive":
        # Compute full periodogram
        per_xyz_data = psd.periodogram_matrix(xyz_data.T, fs, wd_func=wd_func,
                                              wisdom=wisdom)
        # Start and end frequencies
        df = fs / ns
        k_min = int(fmin/ df)
        k_max = int(fmax / df)
        # Choose segment sizes
        segment_sizes = psd.index_grid(size_min, size_max, k_min, k_max)
        # Compute the smoothed spectrum
        i_mid, per_xyz_smoothed = psd.smooth(per_xyz_data, k_min, segment_sizes)
        # Segment middle frequencies
        fper = i_mid * df

    else:
        raise ValueError(f"Unknown averaging method [{averaging}]")

    if normalize_by_nenbw:
        nenbw = psd.normalized_equivalent_noise_bandwidth(wd_func)
        k_seg = segment_sizes / nenbw
    else:
        k_seg = segment_sizes

    return fper, per_xyz_smoothed, k_seg


def time_to_timefrequency(xyz_data, nt=12, mult=4, fs=None, fmin=1e-4, fmax=2.9e-2,
                          size_min=100, size_max=15000, averaging="SmoothAdaptive",
                          smoothingbandwidth=5e-5, method="wavelets", window_type="bh92",
                          noverlap=None, transform=None, nperseg=None):
    """
    Convert time series to frequency domain data (averaged periodogram)

    Parameters
    ----------
    xyz_data : ndarray
        TDI time series, size n_data x 3
    nt : int
        Number of desired time bins
    mult : int
        Multiplicating factor for zero-padding in wavelet transform
    fs : _type_, optional
        Sampling frequency in Hz, by default None
    fmin : float, optional
        Minimum analysis frequency, by default 1e-4
    fmax : float, optional
        Maximum analysis frequency, by default 2.9e-2
    size_min : int, optional
        Number of frequency bins in the smallest segment, by default 100
    size_max : int, optional
        Number of frequency bins in the largest segment, by default 15000
    averaging : str, optional
        Type of periodogram smoothing, by default "SmoothAdaptive"
    smoothingbandwidth : _type_, optional
        Banwidth of the smoothing in Hz, if averaging type is "smooth". By default 5e-5
    nperseg : int, optional
        Size of averaged segments if the averaging type is "welch", by default None
    method : str
        Time-frequency method among {'wavelets', 'periodograms', 'stft'}
    window_type : str, optional
        Tapering window, by default "bh92"
    noverlap : int
        Overlap length if STFT method is chosen. If None, it is set to the default value of 
        npserseg // 2.

    Returns
    -------
    fper : ndarray
        frequency bins of the smoothed periodogram, size nf
    t_bins : ndarray
        time bins of the smoothed periodogram, size nt
    per_xyz_smoothed : ndarray
        periodogram matrix, size nf x 3 x 3
    k_seg : ndarray
       effective number of frequency bins in each segment.
    """
    if fs is None:
        raise TypeError("The sampling frequency 'fs' is needed. ")
    # Time series size
    nd = xyz_data.shape[0]
    # Choose window
    if isinstance(window_type, str):
        wd_func = get_window_function(window_type)
    else:
        wd_func = window_type

    # TIME-FREQUENCY BINNING
    if method == "wavelets":
        if nd % nt != 0:
            logger.warning("No integer number of segments in time series length")
        # Number of frequency bins (or segment sizes)
        nf = int(nd / nt)
        # Time bin
        delta_t = nf / fs
        # Compute full spectrogram
        spectrum_xyz = psd.spectrogram_matrix(xyz_data.T, fs, nf, nt, mult=mult)
        logger.debug("Spectrogram matrix computed.")
        # Create frequency and time bin arrays
        delta_f = 1 / (2 * delta_t)
        f_bins = np.arange(0, nf) * delta_f
        t_bins = np.arange(0, nt) * delta_t
    elif method == "periodograms":
        if noverlap is None:
            # We take a 50 percent overlap
            nf = int(2 * nd / (nt + 1))
            noverlap = nf // 2
        else:
            # Size of segments
            nf = int(((nd + noverlap * (nt-1))/nt))
        # Split the data into segments
        # segment_list = np.split(xyz_data, nt, axis=0)
        segment_list = [xyz_data[(nf-noverlap)*i:(nf-noverlap)*i+nf] for i in range(nt)]
        # Time bins at the start of the segments
        delta_t = nf / fs
        t_bins = ((nf-noverlap) * np.arange(nt)) / fs
        # Compute periodograms
        per_xyz_list = [psd.periodogram_matrix(segment.T, fs, wd_func=wd_func, transform=transform)
                        for segment in segment_list]
        # Merge them
        spectrum_xyz = np.swapaxes(np.asarray(per_xyz_list), 0, 1)
        logger.debug("Periodogram matrix computed.")
    elif method == "stft":
        wd = wd_func(nf)
        f_bins, t_bins, spectrum_xyz = psd.stft_matrix(xyz_data.T, fs=fs, window=wd,
                        nperseg=nf,
                        noverlap=noverlap, nfft=None, detrend=False, return_onesided=True,
                        boundary='zeros', padded=False, axis=-1, scaling='psd')
        logger.debug("STFT matrix computed.")
    elif method == "welch":
        # Split the data into segments
        segment_list = np.split(xyz_data, nt, axis=0)
        # Compute periodograms
        per_xyz_list = [psd.welch_matrix(segment.T, fs, nperseg, wd_func=wd_func)
                        for segment in segment_list]
        # Time bins at the start of the segments
        delta_t = nperseg / fs
        t_bins = np.arange(0, nt) * delta_t
        # Merge them
        spectrum_xyz = np.swapaxes(np.asarray(per_xyz_list), 0, 1)
        logger.debug("Welch matrix computed.")
    else:
        raise ValueError(f"Unknown time-frequency method [{averaging}]")

    # APPLY SMOOTHING
    if averaging.lower() == "smooth":
        # Start and end frequencies
        df = fs / nf
        k_min = int(fmin/ df)
        k_max = int(fmax / df)
        band_size = k_max - k_min + 1
        # All segments have the same size
        size = int(smoothingbandwidth / df)
        # Number of segments
        n_seg = band_size // size
        segment_sizes = np.ones(n_seg) * size
        # Compute the smoothed spectrum
        i_mid, spectrum_xyz_smoothed = psd.smooth(spectrum_xyz, k_min, segment_sizes)
        # Segment middle frequencies
        f_bins = i_mid * df

    elif averaging.lower() == "smoothadaptive":
        # Start and end frequencies
        df = fs / nf
        k_min = int(fmin / df)
        k_max = int(fmax / df)
        # Choose segment sizes
        segment_sizes = psd.index_grid(size_min, size_max, k_min, k_max)
        # Compute the smoothed spectrum
        i_mid, spectrum_xyz_smoothed = psd.smooth(spectrum_xyz, k_min, segment_sizes)
        # Segment middle frequencies
        f_bins = i_mid * df

    elif (averaging.lower() == "welch") | (method == "welch"):
        spectrum_xyz_smoothed = spectrum_xyz[:]
        segment_sizes = nf // nperseg
        f_bins = np.fft.fftfreq(nf)*fs

    else:
        raise ValueError(f"Unknown averaging method [{averaging}]")

    return f_bins, t_bins, spectrum_xyz_smoothed, segment_sizes


def restrict_frequencies(sgwb_cls, fper, t0,
                         output_freqs=False, fmin=1e-4, fmax=2.9e-2,
                         df_margin=2e-4):

    if not isinstance(sgwb_cls, (Response, StochasticBackgroundResponse)):
        orbits = sgwb_cls
        sgwb_cls = Response(orbits)

    # Restrict the frequency band if not already done
    # To avoid resctricting too much, pick the grid point closest to the required extrema
    i_min = np.argmin(np.abs(fmin-fper))
    i_max = np.argmin(np.abs(fmax-fper))
    # Cut the extermal frequencies
    # inds = np.arange(i_min, i_max+1)
    autorized = [fper >= fper[i_min], fper <= fper[i_max]]
    # Avoid blind frequencies
    f_star = 1 / np.mean(sgwb_cls.ltt[12](t0))
    excluded_freqs = [j*f_star/4 for j in range(1, 5)]
    autorized += [np.abs(fper-f_star) > df_margin for f_star in excluded_freqs]
    inds = np.where(np.logical_and.reduce(np.asarray(autorized)))[0]

    if output_freqs:
        return inds, excluded_freqs
    return inds


def loadall(filename):
    with open(filename, "rb") as f:
        while True:
            try:
                yield pickle.load(f)
            except EOFError:
                break


def unpickle(filename, concatenate=False, axis=2):

    items = loadall(filename)

    item_list = []
    for it in items:
        # print(it.shape)
        item_list.append(it)

    if not concatenate:
        return item_list
    else:
        return np.concatenate(item_list, axis=axis)
