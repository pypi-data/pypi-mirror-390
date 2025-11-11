# -*- coding: utf-8 -*-
# Author: Quentin Baghi 2021 <quentin.baghi@protonmail.com>
# This code provides routines for PSD estimation using a peace-continuous model
# that assumes that the logarithm of the PSD is linear per peaces.
import numpy as np
from scipy import optimize, interpolate, sparse
from scipy import signal as sig
from scipy.signal.windows import blackmanharris, nuttall
# FTT modules
try:
    import pyfftw
    from pyfftw.interfaces.numpy_fft import fft, ifft
except ImportError:
    from numpy.fft import fft, ifft
from . import utils

try:
    from pywavelet.transforms import from_time_to_wavelet
    from pywavelet.types import TimeSeries
except ImportError:
    pass


def periodogram(x, fs, wd_func=blackmanharris, wisdom=None):
    """Compute the periodogram of a time series using the
    Blackman window

    Parameters
    ----------
    x : ndarray
        intput time series
    fs : float
        sampling frequency
    wd_func : callable
        tapering window function in the time domain

    Returns
    -------
    ndarray
        periodogram at Fourier frequencies
    """

    # Getting some FFT plan wisdom to speed up
    if wisdom is not None:
        pyfftw.import_wisdom(wisdom)

    wd = wd_func(x.shape[0])
    k2 = np.sum(wd**2)
    if x.ndim == 1:
        per = np.abs(fft(x * wd))**2 * 2 / (k2*fs)
    elif x.ndim == 2:
        per = np.abs(fft(x * wd[:, np.newaxis], axis=0))**2 * 2 / (k2*fs)

    return per


def spectrogram(x, fs, nf, nt, mult=4):
    """Compute the spectrogram of a time series using the 
    WDM wavelet transform

    Parameters
    ----------
    x : ndarray
        intput time series
    fs : float
        sampling frequency

    Returns
    -------
    ndarray
        spectrogram at wavelet time and frequency bins
        size nf x nt
    """

    x_time_obj = TimeSeries(x, time=np.arange(x.size) / fs)
    x_wavelet = from_time_to_wavelet(x_time_obj, Nf=nf, Nt=nt, mult=mult)

    return np.abs(x_wavelet)**2 * 2.0 / fs # To be consistent with a PSD


def cross_periodogram(x, y, fs, wd_func=blackmanharris, wisdom=None):
    """Compute the cross-periodogram of two time series using the
    Blackman window

    Parameters
    ----------
    x : ndarray
        first intput time series
    y : ndarray
        second intput time series
    fs : float
        sampling frequency
    wd_func : callable
        tapering window function in the time domain

    Returns
    -------
    ndarray
        periodogram at Fourier frequencies
    """

    # Getting some FFT plan wisdom to speed up
    if wisdom is not None:
        pyfftw.import_wisdom(wisdom)

    wd = wd_func(x.shape[0])
    k2 = np.sum(wd**2)
    x_wfft = fft(x * wd)
    y_wfft = fft(y * wd)
    return x_wfft * np.conj(y_wfft) * 2 / (k2*fs)


def cross_spectrogram(x, y, fs, nf, nt, mult=4):
    """Compute the cross spectrogram of two time series using the 
    WDM wavelet transform

    Parameters
    ----------
    x : ndarray
        first intput time series
    y : ndarray
        second intput time series
    fs : float
        sampling frequency

    Returns
    -------
    ndarray
        spectrogram at wavelet time and frequency bins
        size nf x nt
    """

    time_vector = np.arange(x.size) / fs
    x_time_obj = TimeSeries(x, time=time_vector)
    x_wavelet = from_time_to_wavelet(x_time_obj, Nf=nf, Nt=nt, mult=mult)
    y_time_obj = TimeSeries(y, time=time_vector)
    y_wavelet = from_time_to_wavelet(y_time_obj, Nf=nf, Nt=nt, mult=mult)

    return x_wavelet * y_wavelet * 2 / fs


def periodogram_matrix(x_list, fs, wd_func=blackmanharris, wisdom=None, transform=None):
    """
    Computes the matrix of periodograms and cross periodograms of the 
    multivariate time series x_list.
    

    Parameters
    ----------
    x_list : list of ndarrays
        list of intput time series. They should all have the same size N.
    fs : float
        sampling frequency
    wd_func : callable
        tapering window function in the time domain
    transform : ndarray or None
        transfer function to apply in the frequency domain

    Returns
    -------
    ndarray
        periodogram matrix of size N x p x p where p is the length of x_list.
    
    """

    # Getting some FFT plan wisdom to speed up
    if wisdom is not None:
        pyfftw.import_wisdom(wisdom)

    # Transform data to array
    x_arr = np.asarray(x_list, dtype=complex).T
    n_data = x_arr.shape[0]
    # Compute the window
    wd = wd_func(n_data)
    # Norm related to windowing
    k2 = np.sum(wd**2)
    # Fourier transform the whole vector (size n_data x p)
    x_tf = fft(wd[:, np.newaxis] * x_arr, axis=0) * np.sqrt(2 / (k2*fs))
    # Apply transfer function if necessary
    if transform is not None:
        x_tf = utils.multiple_dot_vect(transform, x_tf)
    # Compute the periodogram matrix
    mat = utils.multiple_dot(x_tf[:, :, np.newaxis], np.conj(x_tf[:, np.newaxis, :]))

    return mat


def stft_matrix(x_list, fs, nperseg, **kwargs):
    """
    Computes the matrix of short-time Fourier transform periodograms 
    and cross periodograms of the multivariate time series x_list.
    

    Parameters
    ----------
    x_list : list of ndarrays
        list of intput time series. They should all have the same size N.
    fs : float
        sampling frequency
    nperseg : int
        size of segments
    wd_func : callable
        tapering window function in the time domain

    Returns
    -------
    ndarray
        periodogram matrix of size N x p x p where p is the length of x_list.
    
    """

    # Initialization
    f_bins, t_bins, x0_stft = sig.stft(x_list[0], fs=fs, nperseg=nperseg, **kwargs)
    nc = len(x_list)
    nt = len(t_bins)
    nf = len(f_bins)
    mat = np.zeros((nf, nt, nc, nc), dtype=complex)
    mat[..., 0, 0] = x0_stft

    for i in range(nc):
        if i != 0:
            f_bins, t_bins, xi_stft = sig.stft(x_list[i], fs=fs, nperseg=nperseg, **kwargs)
        else:
            xi_stft = x0_stft
        mat[..., i, i] = np.abs(xi_stft)**2

        for j in range(i+1, nc):
            _, _, xj_stft = sig.stft(x_list[i], fs=fs, nperseg=nperseg, **kwargs)
            mat[..., i, j] = xi_stft * np.conj(xj_stft)
            mat[..., j, i] = np.conj(mat[..., i, j])

    return f_bins, t_bins, 2*mat


def spectrogram_matrix(x_list, fs, nf, nt, mult=4):
    """
    Computes the matrix of wavelet spectrograms and cross spectrograms of the 
    multivariate time series x_list.
    

    Parameters
    ----------
    x_list : list of ndarrays
        list of intput time series. They should all have the same size N.
    fs : float
        sampling frequency
    wd_func : callable
        tapering window function in the time domain

    Returns
    -------
    ndarray
        periodogram matrix of size N x p x p where p is the length of x_list.
    
    """

    n_c = len(x_list)
    mat = np.zeros((nf, nt, n_c, n_c), dtype=float)

    for i in range(n_c):
        mat[..., i, i] = spectrogram(x_list[i], fs, nf, nt, mult=mult)

        for j in range(i+1, n_c):
            mat[..., i, j] = cross_spectrogram(x_list[i], x_list[j], fs,
                                             nf, nt, mult=mult)
            mat[..., j, i] = mat[..., i, j]

    return mat


def welch(x, fs, nperseg, wd_func=blackmanharris):
    """Welch periodogram with non-overlapping segments

    Parameters
    ----------
    x : ndarray
        intput time series
    fs : float
        sampling frequency
    nperseg : int
        segment size
    wd_func : callable
        tapering window function in the time domain

    Returns
    -------
    ndarray
        Welch periodogram
    """

    k_seg = x.shape[0] // nperseg
    per = sum([periodogram(x[j*nperseg:(j+1)*nperseg], fs, wd_func=wd_func)
               for j in range(k_seg)]) / k_seg

    return per


def welch_csd(x, y, fs, nperseg, wd_func=blackmanharris):
    """Welch periodogram with non-overlapping segments

    Parameters
    ----------
    x : ndarray
        first intput time series
    y : ndarray
        second intput time series
    fs : float
        sampling frequency
    nperseg : int
        segment size
    wd_func : callable
        tapering window function in the time domain

    Returns
    -------
    ndarray
        Welch periodogram
    """

    k_seg = x.shape[0] // nperseg
    per = sum([cross_periodogram(x[j*nperseg:(j+1)*nperseg], y[j*nperseg:(j+1)*nperseg], fs,
                                wd_func=wd_func)
               for j in range(k_seg)]) / k_seg

    return per


def welch_matrix(x_list, fs, nperseg, wd_func=blackmanharris,
                 output_freqs=False):
    """Computes all Welch cross-periodograms for a list 
    of synchronous time series.

    Parameters
    ----------
    x_list : list or ndarray
        list of n_c intput time series of size n
    fs : float
        sampling frequency
    nperseg : int, or array_like
        segment size. If freq_segments is provided, must
        be a vector of size len(freq_segments) - 1
    wd_func : callable
        tapering window function in the time domain
    output_freqs : bool
        If True, outputs frequency abscissa
        

    Returns
    -------
    ndarray
        Welch periodogram matrix, size nperseg x n_c x n_c
    """

    k_seg = x_list[0].shape[0] // nperseg
    per = sum([periodogram_matrix([x[j*nperseg:(j+1)*nperseg] for x in x_list], fs,
                                 wd_func=wd_func)
               for j in range(k_seg)]) / k_seg

    if output_freqs:
        f_per = np.fft.fftfreq(nperseg) * fs

        return f_per, per
    else:
        return per


def welch_matrix_adaptive(x_list, fs, nperseg, freq_segments, wd_func=blackmanharris,
                          output_freqs=False):
    """Computes all Welch cross-periodograms for a list 
    of synchronous time series, with adaptative averaging depending 
    on frequency segments.

    Parameters
    ----------
    x_list : list or ndarray
        list of n_c intput time series of size n
    fs : float
        sampling frequency
    nperseg : int, or array_like
        time segment size. Must be a vector of size len(freq_segments) - 1
    freq_segments : ndarray
        Frequency segments bounds. To have frequency-dependent averaging. 
        Periodograms ordinates between frequencies 
        freq_segments[j] and freq_segments[j+1] are computed
        by averaging n/nperseg[j] segments of size nperseg[j]
    wd_func : callable
        tapering window function in the time domain
    output_freqs : bool
        if True, outputs the Welch frequency vector

    Returns
    -------
    f_per : ndarray
        Frequency abscissa, size J
    per : ndarray
        Welch periodogram matrix, size J x n_c x n_c
    k_seg_vect :
        Number of time segments averaged to compute P(f)
        as a function of f.

    """

    # Number of frequency segments
    n_seg = len(freq_segments)-1
    # Number of time segments
    f_per_full = [np.fft.fftfreq(nperseg[q]) * fs for q in range(n_seg)]
    ii = [np.where((f_per_full[q]>=freq_segments[q]) & (f_per_full[q]<freq_segments[q+1]))[0]
          for q in range(n_seg)]
    # Welch matrix for each time segment sizes
    per = np.vstack([welch_matrix(x_list, fs, nperseg[q], wd_func=wd_func)[ii[q]]
                       for q in range(n_seg)])
    # Stacked frequencies
    f_per = np.hstack([f_per_full[q][ii[q]] for q in range(n_seg)])
    # Vector of segment sizes as a function of frequencies
    k_seg_vect = np.hstack([x_list[0].shape[0] // nperseg[q] * np.ones(len(ii[q]))
                            for q in range(n_seg)])

    if output_freqs:
        return f_per, per, k_seg_vect
    else:
        return per, k_seg_vect


def taper_window(nu, nu0, m):

    return 1 / (1 + (nu / nu0)**(2*m))


def rect_window(nu, k0):
    """
    Fourier transform of the rectangular window
    centered in 0 and of length k0

    Parameters
    ----------
    nu : ndarray
        normalized frequency vector
    k0 : int
        width of the window, in number of samples

    Returns
    -------
    ndarray
        window in the frequency domain
    """

    out = np.zeros_like(nu)
    out[nu == 0] = 1.0
    out[nu != 0] = np.sin((2*k0+1)*np.pi*nu[nu != 0]) / \
        (np.sin(np.pi * nu[nu != 0])) / (2*k0+1)

    return out


def index_grid(size_min, size_max, k_min, k_max, enforce_odd=False):
    """
    Generate a grid of exponentially increasing segment sizes between size_min and size_max.

    Parameters
    ----------
    size_min : int
        segment minimum size
    size_max : int
        segment maximum size
    k_min : int
        initial frequency index
    k_max : int
        final frequency index
    enforce_odd : bool
        if True, all segment sizes are forced to be odd

    Returns
    -------
    segment_sizes : ndarray
        Array of segment sizes
    """

    # Number of frequencies
    dk = k_max - k_min
    if not enforce_odd:
        # Common ratio of the geometric series
        r = (dk - size_min) / (dk - size_max)
        # Compute the numver of segments
        n_seg = np.ceil(np.log(r * size_max / size_min) / np.log(r))
        # Define the segment sizes
        segment_sizes = size_min * r**(np.arange(n_seg))
    else:
        # The segment sizes have the form 2*n+1
        n_max = (size_max - 1) // 2
        n_min = (size_min - 1) // 2
        # Common ratio of the geometric series
        r = (dk - n_min) / (dk - n_max)
        # Compute the numver of segments
        n_seg = np.ceil(np.log(r * n_max / n_min) / np.log(r))
        # Define the segment sizes
        n_sizes = n_min * r**(np.arange(n_seg))
        # Convert to odd segment sizes
        segment_sizes = 2 * n_sizes.astype(int) + 1

    # Convert to integer
    segment_sizes = segment_sizes.astype(int)
    # Now check that the segment sizes sum up to the number of frequencies
    total_size = np.sum(segment_sizes)
    # If the total size is smaller than dk, we need to adjust
    if total_size < dk:
        difference = dk - total_size
        # If the difference is larger than the maximum segment size, add more segments
        if difference > segment_sizes[-1]:
            # Calculate how many segments we need to add
            n_add = int(np.ceil(difference / segment_sizes[-1]))
            # Extend the segment sizes with the maximum size
            segment_sizes = np.concatenate((segment_sizes, np.ones(n_add) * segment_sizes[-1]))
        # Re-compute the total size and check again if it matches dk
        total_size = np.sum(segment_sizes)
        if total_size < dk:
            # If too small, add the difference to the last segment
            segment_sizes[-1] += dk - total_size
        elif total_size > dk:
            # If too large, remove the difference from the last segment
            segment_sizes[-1] -= total_size - dk

    return segment_sizes


def frequency_grid(df_min, df_max, f_min, f_max):
    """
    Generate a grid of exponentially increasing frequency steps between df_min and df_max.

    Parameters
    ----------
    df_min : float
        minimum frequency step
    df_max : float
        maximum frequency step
    f_min : float
        minimum frequency
    f_max : float
        maximum frequency

    Returns
    -------
    freq_steps : ndarray
        Array of frequency steps
    """

    # Full frequency bandwidth
    df = f_max - f_min
    # Ratio between longest and smallest segment
    q = df_max / df_min
    # Target number of segments assuming geometric series
    a = np.log((df*q-df_max)/(df-df_max)) / np.log(q)
    n_seg = int(a / (a-1))

    s = np.arange(1, n_seg+1)
    freq_steps = df_min * (df_max/df_min)**((s-1)/(n_seg-1))

    return freq_steps


def smooth(y, k_min, sizes):
    """
    Average a vector of values y over segments.

    Parameters
    ----------
    y : ndarray
        input values
    k_min : int
        starting index in y
    sizes : ndarray
        array of segment sizes

    Returns
    -------
    i_mid : ndarray
        indices of the middle of each segment
    smoothed_y : ndarray
        averaged values
    """

    # Vector of segment frequency indices
    i_seg = np.zeros(sizes.size + 1, dtype=int)
    i_seg[0] = k_min
    i_seg[1:] = k_min + np.cumsum(sizes)

    n_seg = len(sizes)
    # Compute the averages over each segment
    smoothed_y = np.array(
        [np.mean(y[i_seg[j]:i_seg[j+1]], axis=0) for j in range(n_seg)], dtype=y.dtype)

    # Compute middle frequency indices
    i_mid = (i_seg[:-1] + i_seg[1:]) // 2

    return i_mid, smoothed_y


def choose_frequency_knots(n_knots, freq_min=1e-5, freq_max=1.0, base=10):
    """Provide an array of frequency knots that are spaced logarithmically 
    according to a given base.

    Parameters
    ----------
    n_knots : int
        requested number of knots
    freq_min : float, optional
        minimum frequency, by default 1e-5
    freq_max : float, optional
        maximum frequency, by default 1.0
    base : int, optional
        logarithmic base, by default 10

    Returns
    -------
    ndarray
        knot frequencies
    """
    # Choose the frequency knots
    ns = - np.log(freq_min) / np.log(base)
    n0 = - np.log(freq_max) / np.log(base)
    jvect = np.arange(0, n_knots)
    alpha_guess = 0.8
    def targetfunc(x):
        return n0 - (1 - x ** (n_knots)) / (1 - x) - ns
    result = optimize.fsolve(targetfunc, alpha_guess)
    alpha = result[0]
    n_knots = n0 - (1 - alpha ** jvect) / (1 - alpha)
    f_knots = base ** (-n_knots)
    f_knots = f_knots[(f_knots > freq_min) & (f_knots < freq_max)]

    return np.unique(np.sort(f_knots))


def periodogram_mean(func, fs, n_data, wd_func,
                     n_freq=None, n_points=None, n_conv=None, normal=True):
    """
    Compute the expectation of any periodogram depending on the time series
    size and the window function.
    
    Parameters
    ----------
    func: callable
        function returning the PSD vs frequency. Can return a PSD matrix.
    fs : float
        sampling frequency
    n_data : int
        size of the time series
    wd_func : callable
        time-domain tappering window function. Should take the data size as 
        an argument.
    n_freq : int, optional
        Size of the output frequency grid, with frequencies k f / n_freq
    n_points : int, optional
        Number of points used in the disrete approximation of the integral
    n_conv : int, optional
        number of points for the zero-padding of the window FFT
    
    Returns
    -------
    Pm_mat : ndarray
        Theoretical expectation of the periodogram matrix 
        with shape n_freq x p x p
    
    """

    if n_freq is None:
        n_freq = n_data
    if n_conv is None:
        n_conv = 2 * n_data - 1

    # Calculation of the sample autocovariance of the mask
    mask = wd_func(n_data)
    fx = fft(mask, n_conv)

    if normal:
        k2 = np.sum(mask ** 2)
    else:
        k2 = n_data
    lambda_N = np.real(ifft(fx * np.conj(fx))) / k2

    if n_points is None:
        n_points = 2 * n_data

    k_points = np.arange(0, n_points)
    frequencies = fs * (k_points / float(n_points) - 0.5)
    i = np.where(frequencies == 0)
    frequencies[i] = fs / (10 * n_points)

    # Compute the whole PSD matrix
    Z = func(frequencies)
    Z_ifft = ifft(Z, axis=0)
    n = np.arange(0, n_data)

    if len(np.shape(Z)) == 2:
        n = n[:, np.newaxis]
        lambda_N = lambda_N[:, np.newaxis]
    elif len(np.shape(Z)) == 3:
        n = n[:, np.newaxis, np.newaxis]
        lambda_N = lambda_N[:, np.newaxis, np.newaxis]

    R = fs / float(n_points) * (Z[0] * 0.5 * (
        np.exp(1j * np.pi * n) - np.exp(-1j * np.pi * n)) \
            + n_points * Z_ifft[0:n_data] * np.exp(
        -1j * np.pi * n))

    # 3. Calculation of the of the periodogram mean vector
    X = R[0:n_data] * lambda_N[0:n_data]
    Pm_mat = fft(X, n_freq, axis=0) + n_freq * ifft(X, n_freq, axis=0) - R[0] * lambda_N[0]

    return Pm_mat * 2 / fs


def welch_expectation_adaptive(psd_func, fs, n_data, nperseg, wd_func, freq_segments,
                               output_freqs=False):
    """Computes the expectation of the Welch matrix for a list, with adaptative averaging depending 
    on frequency segments.

    Parameters
    ----------
    psd_func : callable
        True PSD function of frequency
    fs : float
        Sampling frequency
    n_data : int
        size of the entire time series
    nperseg : int, or array_like
        time segment sizes. Must be a vector of size len(freq_segments) - 1
    freq_segments : ndarray
        Frequency segments bounds. To have frequency-dependent averaging. 
        Periodograms ordinates between frequencies 
        freq_segments[j] and freq_segments[j+1] are computed
        by averaging n/nperseg[j] segments of size nperseg[j]
    wd_func : callable, default is blackmanharris
        Time window function (of data size)
    output_freqs : bool
        if True, outputs the Welch frequency vector


    Returns
    -------
    f_per : ndarray
        Frequency abscissa, size J
    per : ndarray
        Expectation of the Welch periodogram matrix, size J x n_c x n_c
    k_seg_vect :
        Number of time segments averaged to compute P(f)
        as a function of f.

    """

    # Number of frequency segments
    n_seg = len(freq_segments)-1
    # Number of time segments
    k_seg = [n_data // nperseg[q] for q in range(n_seg)]
    f_per_full = [np.fft.fftfreq(nperseg[q]) * fs for q in range(n_seg)]
    ii = [np.where((f_per_full[q]>=freq_segments[q]) & (f_per_full[q]<freq_segments[q+1]))[0]
          for q in range(n_seg)]
    # Welch matrix for each time segment sizes
    per = np.vstack([periodogram_mean(psd_func, fs, nperseg[q], wd_func)[ii[q]] 
                     for q in range(n_seg)])
    # Stacked frequencies
    f_per = np.hstack([f_per_full[q][ii[q]] for q in range(n_seg)])
    # Vector of segment sizes as a function of frequencies
    k_seg_vect = np.hstack([k_seg[q] * np.ones(len(ii[q])) for q in range(n_seg)])

    if output_freqs:
        return f_per, per, k_seg_vect
    else:
        return per, k_seg_vect


def normalized_equivalent_noise_bandwidth(wd_func, nd=2**10):
    """
    Compute the normalized equivalent noise bandwidth associated to a 
    time window

    Parameters
    ----------
    wd_func : callable
        window function
    nd : int
        size of the time series if known. Used only if the window is different from
        rectangular, blackman, hanning and nuttal.

    Returns
    -------
    nenbw : int
        normalized equivalent noise bandwidth
    """

    if wd_func is np.ones:
        nenbw = 1.0
    elif wd_func is np.blackman:
        nenbw = 1.726757479056736 # 2.0044
    elif wd_func is blackmanharris:
        nenbw = 2.0044
    elif wd_func is np.hanning:
        nenbw = 1.5000
    elif wd_func is nuttall:
        nenbw = 1.9761
    else:
        wd = wd_func(nd)
        nenbw = nd * np.sum(wd**2) / np.sum(wd)**2

    return nenbw


def white_psd(f):
    """
    Function returning a constant PSD equal to 1.
    """
    return np.ones(f.size)


class FrequencyCovariance:
    """
    Class to compute the covariance of the windowed Fourier transform
    """
    def __init__(self, wd, fs, psd_func=white_psd, npoints=None):
        """
        Class constructor.

        Parameters
        ----------
        wd : ndarray
            time window function
        fs : float
            Sampling frequency [Hz]
        psd_func : callable
            One-sided PSD or CSD function (in 1/Hz)
        npoints : int
            Number of points to compute the DFT

        """

        self.wd = wd
        self.nd = wd.size
        self.psd_func = psd_func
        self.fs = fs
        self.tobs = self.nd / self.fs
        if npoints is None:
            self.npoints = 2 * self.nd
        else:
            self.npoints = npoints
        self.k2 = np.sum(self.wd**2)
        self.wind_dft = np.fft.fft(self.wd, self.npoints) * np.sqrt(2 / (self.fs*self.k2))
        self.n = int((self.npoints-1)/2)
        self.freqs = np.fft.fftfreq(self.npoints) * self.fs
        self.psd_arr = self.psd_func(np.abs(self.freqs))

        # DFT of the window function
        self.wd_fft_real_func = interpolate.interp1d(np.fft.fftshift(self.freqs),
                                                     np.fft.fftshift(self.wind_dft.real))
        self.wd_fft_imag_func = interpolate.interp1d(np.fft.fftshift(self.freqs),
                                                     np.fft.fftshift(self.wind_dft.imag))

    def wind_dft_func(self, fr):
        """
        interpolant of the window Fourier transform 

        Parameters
        ----------
        fr : ndarray
            frequency

        Returns
        -------
        wd_fft : ndarray
            DFT of the window function
        """

        return self.wd_fft_real_func(fr) + 1j * self.wd_fft_imag_func(fr)

    def bin_correlation(self, f1, f2, bandwidth=1e-5):
        """
        Compute the covariance of the windowed Fourier transform

        Parameters
        ----------
        f1 : float
            First frequency (Hz). Assumed positive.
        f2 : float
            Second frequency (Hz). Assumed positive.
        bandwidth : float
            Frequency difference (in Hz) above which the Fourier transform of the window is assumed
            to be zero. |W(f)| = 0 for |f| > bandwidth.

        Returns
        -------
        corr : float
            covariance value

        """

        # Indices where the integrand is nonzero
        f_low = np.max([f1, f2]) - bandwidth
        f_up = np.min([f1, f2]) + bandwidth
        ii = np.where((self.freqs>=f_low) & (self.freqs <= f_up))[0]
        df = self.fs / self.npoints

        fnonzero = self.freqs[ii]
        if len(fnonzero) == 0:
            return 0.0
        # Maybe it would be best to use an interpolation of wind_dft
        return np.sum(self.wind_dft_func(f1 - fnonzero) \
                      * np.conj(self.wind_dft_func(f2 - fnonzero)) * self.psd_arr[ii]) * df / 2.0

    def compute_covariance_matrix(self, f0, size=10, bandwidth=1e-5, assume_toeplitz=False,
                                  sparse_output=True):
        """
        Compute a subet of the covariance matrix of the windowed Fourier transforms of X
        with a specified size.

        Parameters
        ----------
        f0 : float
            Frequency [Hz] corresponding to the 00 entry.
        size : int
            Size of the subset
        bandwidth : float
            Frequency difference (in Hz) above which the Fourier transform of the window is assumed
            to be zero. |W(f)| = 0 for |f| > bandwidth.
        assume_toeplitz : bool
            Assumes that the matrix is only defined by its first row.
        sparse_output : bool
            If True, returns a sparse matrix

        Returns
        -------
        cov_mat : ndarray or float
            covariance value

        """

        # Frequency resolution
        df = 1 / self.tobs
        # Frequency grid
        f_grid = f0 + np.arange(size) * df
        # Maximum difference in frequency bins above which the correlation is zero
        # Note: for such a frequency difference, there are frequencies in the integral that
        # contribute to w(f-f1) but not to w(f-f2). This can lead to inaccuracies.
        diag_max = 2 * int(bandwidth * self.tobs)
        # Build the covariance matrix
        if not sparse_output:
            cov_mat = np.zeros((size, size), dtype=complex)

            if not assume_toeplitz:
                for i in range(size):
                    imax = np.min([i+diag_max, size])
                    for j in range(i, imax):
                        cov_mat[i, j] = self.bin_correlation(f_grid[i], f_grid[j],
                                                             bandwidth=bandwidth)
            else:
                row_size = np.min([diag_max, size])
                first_row = np.asarray([self.bin_correlation(f0, f_grid[j], bandwidth=bandwidth)
                                        for j in range(row_size)])
                for i in range(size):
                    imax = np.min([i+diag_max, size])
                    cov_mat[i, i:imax] = first_row[:imax-i]

            cov_mat = cov_mat + cov_mat.T.conj() - np.diag(np.diag(cov_mat))

        else:
            data =[]
            rows = []
            cols = []

            if not assume_toeplitz:
                for i in range(size):
                    imax = np.min([i+diag_max, size])
                    for j in range(i, imax):
                        data.append(self.bin_correlation(f_grid[i], f_grid[j],
                                                         bandwidth=bandwidth))
                        rows.append(i)
                        cols.append(j)
                        # Add the symmetric conjugate element
                        if i != j:
                            data.append(np.conj(data[-1]))
                            rows.append(j)
                            cols.append(i)
                # Construct the sparse matrix
                cov_mat = sparse.coo_matrix((data, (rows, cols)), shape=(size, size))
            else:
                # Toeplitz matrix with constant diagonals
                row_size = np.min([diag_max, size])
                first_row = np.asarray([self.bin_correlation(f0, f_grid[j], bandwidth=bandwidth)
                                        for j in range(row_size)])
                data = []
                offsets = []
                # Central diagonal
                data.append(first_row[0] * np.ones(size))
                offsets.append(0)
                for i in range(row_size):
                    # Upper diagonals
                    data.append(first_row[i] * np.ones(size-i))
                    offsets.append(i)
                    # Lower diagonals
                    data.append(np.conj(first_row[i]) * np.ones(size-i))
                    offsets.append(-i)
                # Construct the sparse matrix
                cov_mat = sparse.diags(data, offsets, shape=(size, size))

        return cov_mat

    def compute_covariance_first_row(self, f0, size, bandwidth=1e-5, normalize_by_variance=False):
        """
        Compute the first row of the frequency-domain covariance, only for frequencies where 
        the correlation is non-zero.

        Parameters
        ----------
        f0: float
            Reference frequency to compute the correlation matrix
        size : int
            Size of the covariance matrix block
        bandwidth : float
            Frequency difference (in Hz) above which the Fourier transform of the window is assumed
            to be zero. |W(f)| = 0 for |f| > bandwidth.
        """
        # Frequency resolution
        df = 1 / self.tobs
        # Maximum difference in frequency bins above which the correlation is zero
        diff_max = np.min([2 * int(bandwidth * self.tobs), size])
        # Frequency grid
        f_grid = f0 + np.arange(size) * df
        # Compute non-zero elements of the covariance's first row
        first_row = np.asarray([self.bin_correlation(f0, f_grid[j], bandwidth=bandwidth)
                                     for j in range(diff_max)])
        if normalize_by_variance:
            first_row = first_row / np.sqrt(self.psd_func(f0)*self.psd_func(f_grid))
        if diff_max < size:
            first_row = np.concatenate([first_row, np.zeros(size-diff_max)])

        return first_row

    def compute_gamma_parameters(self, f0, segment_sizes, bandwidth=1e-5,
                                 normalize_by_variance=False, first_row=None):
        """

        Parameters
        ----------
        f0: float
            Reference frequency to compute the correlation matrix
        segment_sizes : ndarray
            Size of averaged frequency segments
        bandwidth : float
            Frequency difference (in Hz) above which the Fourier transform of the window is assumed
            to be zero. |W(f)| = 0 for |f| > bandwidth.
            
        Returns
        -------
        alphas : ndarray
            Frequency-dependent gamma shape parameter
        thetas : ndarray
            Frequency-dependent gamma scale parameter
        
        """

        # Instantiate covariance class
        k_max = np.max(segment_sizes)
        # Maximum difference in frequency bins above which the correlation is zero
        diag_max = np.min([2 * int(bandwidth * self.tobs), k_max])
        # Compute the first row of the covariance if necessary
        if first_row is None:
            first_row = self.compute_covariance_first_row(
                f0, k_max, bandwidth=bandwidth, normalize_by_variance=normalize_by_variance)
        else:
            first_row = first_row[0:k_max]

        alphas = np.zeros(segment_sizes.size)
        thetas = np.zeros(segment_sizes.size)

        for i, k in enumerate(segment_sizes):
            # If there are at least 2 bins in the segment
            if k > 1:
                k_diag = np.min([k, diag_max])
                if k > 2:
                    diagonals_up_to_k = np.concatenate([first_row[j]*np.ones(k-j)
                                                        for j in range(1, k_diag)])
                else:
                    diagonals_up_to_k = first_row[1]
                # Sum of correlation coefficients involved
                correlation_sum = np.sum(np.abs(diagonals_up_to_k)**2)
            else:
                correlation_sum = 0.0
            # Gamma function parameters
            u = 2 * (1 + 2 * correlation_sum / k)
            # Equivalent alpha parameter (shape)
            alphas[i] = 2 * k / u
            # Equivalent theta parameter (scale)
            thetas[i] = u / k

        return alphas, thetas

    def normalized_window_correlation(self, k, s):
        """
        Compute the normalized window correlation function for a bin distance k and a segment
        overlap s.

        Parameters
        ----------
        k : int
            segment bin separation
        s : int
            inter-segment shift = segment size - overlap
        """

        if (k <= int(self.nd/s)) & (s < self.nd):
            return np.abs(np.sum(self.wd[0:self.nd-k*s] * self.wd[k*s:self.nd]) / self.k2)**2
        else:
            return 0.0

    def compute_welch_equivalent_dof(self, s, n_segments):
        """
        Compute the equivalent number of degrees of freedom for the Welch method
        with a given segment overlap.

        Parameters
        ----------
        s : int
            inter-segment shift = segment size - overlap
        """

        correlation_sum = np.sum(
            [(n_segments - k) * self.normalized_window_correlation(k, s)
             for k in range(1, n_segments)])

        return 2 * n_segments / (1 + 2 * correlation_sum/n_segments)
