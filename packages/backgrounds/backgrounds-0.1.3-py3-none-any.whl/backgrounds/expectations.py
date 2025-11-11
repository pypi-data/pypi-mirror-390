# -*- coding: utf-8 -*-
# Author: Quentin Baghi 2023 <quentin.baghi@protonmail.com>
import healpy as hp
import numpy as np
from . import psd, utils, tdi, noise, instru, signal, loadings
from . import StochasticBackgroundResponse
from lisaconstants import SIDEREALYEAR_J2000DAY as YEAR


def load_expectation_data(orbit_file, fs, tobs, t0,
                          noise_model='lisainstrument',
                          sgwb_func=signal.sgwb_psd,
                          sgwb_args=None,
                          sgwb_kwargs=None,
                          nside=8,
                          signal_scale=1.0,
                          noise_scale=1.0,
                          gen="2.0",
                          breakup=False,
                          skynorm=None,
                          galaxy_on=False,
                          galaxy_amp=None,
                          output_classes=False):
    """
    Create a frequency-domain periodogram matrix that is equal to the statistical expectation
    of the sample periodogram.

    Parameters
    ----------
    orbits : _type_
        _description_
    fs : _type_
        _description_
    tobs : _type_
        _description_
    noise_args : _type_
        _description_
    noise_model : str, optional
        _description_, by default 'lisainstrument'
    sgwb_args : _type_, optional
        _description_, by default None
    sgwb_kwargs : _type_, optional
        _description_, by default None
    skynorm : float, optional
        skymap normalisation


    Returns
    -------
    fper : float
        frequency bins of the smoothed periodogram, size nf
    per_xyz_smoothed : ndarray
        periodogram matrix, size nf x 3 x 3
    k_seg : ndarray
       effective number of frequency bins in each segment.

    """

    # Choosing a subset of frequencies
    nf = 500
    f_minimum = 1/tobs
    f_maximum = fs/2
    f_subset = f_minimum * (f_maximum/f_minimum) ** (np.arange(0, nf) / (nf-1))
    # Create the skymap with JB's normalization
    npix = hp.nside2npix(nside)
    if skynorm is None:
        skynorm = np.sqrt(npix) * np.sqrt((2 / (4 * np.pi)))
    m = np.ones(npix) / skynorm
    if sgwb_args is None:
        sgwb_args = []
    if sgwb_kwargs is None:
        sgwb_kwargs = {}
    # Instantiate SGWB class
    sgwb_cls = StochasticBackgroundResponse(m, orbits=orbit_file)

    # Noise model
    # ===========
    noise_classes_true = []
    if noise_model == "lisainstrument":
        link_model = instru.InstrumentModel()
        # OMS noise
        noise_classes_true.append(noise.AnalyticNoiseModel(f_subset, t0, orbit_file,
                                                           link_model.oms_in_isi_carrier,
                                                           tdi_tf_func=tdi.compute_tdi_tf,
                                                           gen=gen,
                                                           ndim=1))
        # TM noise
        noise_classes_true.append(noise.AnalyticNoiseModel(f_subset, t0, orbit_file,
                                                           link_model.testmass_in_tmi_carrier,
                                                           tdi_tf_func=tdi.compute_tdi_tf_tm,
                                                           gen=gen,
                                                           ndim=1))
    elif noise_model == "custom":
        link_model = noise.LinkNoiseModel()
        # OMS noise
        noise_classes_true.append(noise.AnalyticNoiseModel(f_subset, t0, orbit_file,
                                                           link_model.oms_noise_model,
                                                           tdi_tf_func=tdi.compute_tdi_tf,
                                                           gen=gen,
                                                           ndim=1))
        # TM noise
        noise_classes_true.append(noise.AnalyticNoiseModel(f_subset, t0, orbit_file,
                                                           link_model.acceleration_noise_model,
                                                           tdi_tf_func=tdi.compute_tdi_tf_tm,
                                                           gen=gen,
                                                           ndim=1))

    elif noise_model == "redbook":
        link_model = noise.AnalyticNoise(f_subset, model="SciRDv1", wd=round(tobs/YEAR))
        # OMS noise
        noise_classes_true.append(noise.AnalyticNoiseModel(f_subset, t0, orbit_file,
                                                           link_model.oms_noise_model,
                                                           tdi_tf_func=tdi.compute_tdi_tf,
                                                           gen=gen,
                                                           ndim=1))
        # TM noise
        noise_classes_true.append(noise.AnalyticNoiseModel(f_subset, t0, orbit_file,
                                                           link_model.acceleration_noise_model,
                                                           tdi_tf_func=tdi.compute_tdi_tf_tm,
                                                           gen=gen,
                                                           ndim=1))

    # Compute the TDI spectrum from OMS and TM noise
    cov_tdi_n_comps = [nc.compute_covariances(f_subset) for nc in noise_classes_true]
    # Compute the full TDI noise spectrum
    cov_tdi_n = sum(cov_tdi_n_comps)

    # Signal model
    # ============
    # Compute the response kernel for TDI AET on a subset of frequencies
    g_mat_tdi_subset = sgwb_cls.compute_tdi_kernel(f_subset, t0, tdi_var='xyz', gen=gen)
    cov_tdi_sgwb = g_mat_tdi_subset * sgwb_func(
        f_subset, *sgwb_args, **sgwb_kwargs)[:, np.newaxis, np.newaxis]

    if galaxy_on:
        galaxy_cls = noise.GalacticNoise(f_subset, tobs, tdi_var='xyz')
        cov_tdi_gal = galaxy_cls.compute_covariances(np.log10(galaxy_amp))
    else:
        cov_tdi_gal = np.zeros_like(cov_tdi_sgwb)

    if breakup:
        outputs = f_subset, (noise_scale**2 * cov_tdi_n, signal_scale**2 * cov_tdi_sgwb,
                             cov_tdi_gal)
        if output_classes:
            return outputs + (noise_classes_true, sgwb_cls)
        return outputs

    # Full model
    # ==========
    cov_tdi = noise_scale**2 * cov_tdi_n + signal_scale**2 * cov_tdi_sgwb + cov_tdi_gal

    if output_classes:
        return f_subset, cov_tdi, noise_classes_true, sgwb_cls

    return f_subset, cov_tdi


def process_expectation_data(f_subset, cov_tdi, fs, tobs,
                             fmin=1e-4,
                             fmax=2.9e-2,
                             size_min=100,
                             size_max=15000,
                             averaging="SmoothAdaptive",
                             smoothingbandwidth=5e-5,
                             nperseg=None,
                             window_type="blackman",
                             kind="linear",
                             leakage=False):

    # Interpolation
    cov_funcs = utils.CovarianceInterpolator(f_subset, cov_tdi, kind=kind)
    # Data size
    ns = int(tobs * fs)

    # Periodogram expectation
    # -----------------------
    # Choose window
    if isinstance(window_type, str):
        wd_func = loadings.get_window_function(window_type)
    else:
        wd_func = window_type

    if averaging == "Welch":
        # Number of segments
        k_seg = ns // nperseg
        # Welch periodogram frequencies
        fper = np.fft.fftfreq(nperseg) * fs
        # The Welch periodogram is also applying a convolution
        if leakage:
            pers = psd.periodogram_mean(cov_funcs, fs, nperseg, wd_func)
        else:
            pers = cov_funcs(fper)

    elif averaging == "WelchAdaptive":
        f_segments = np.array([0, 1e-3, 1e-2, 1e-1, 1.0])
        d_max = 2 * 24 * 3600
        d_min = 1000
        n_segs = len(f_segments)-1
        segment_durations = d_max * \
            (d_min / d_max) ** (np.arange(0, n_segs)/(n_segs-1))
        segment_sizes = (segment_durations * fs).astype(int)
        # psd_func, fs, nperseg, wd_func, freq_segments,
        fper, pers, k_seg = psd.welch_expectation_adaptive(cov_funcs, fs, ns, segment_sizes,
                                                           wd_func, f_segments,
                                                           output_freqs=True)
    elif averaging == 'Smooth':
        # Frequency vector for raw data
        freqs = np.fft.fftfreq(ns) * fs
        f_abs = np.abs(freqs)
        f_abs[0] = f_abs[1]
        # Account for the finite window
        if leakage:
            pers_f = psd.periodogram_mean(cov_funcs, fs, ns, wd_func)
        else:
            pers_f = cov_funcs(f_abs)
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
        i_mid, pers = psd.smooth(pers_f, k_min, segment_sizes)
        # Segment middle frequencies
        fper = i_mid * df
        # Effective segment size
        nenbw = psd.normalized_equivalent_noise_bandwidth(cov_funcs)
        k_seg = segment_sizes  / nenbw

    elif averaging == 'SmoothAdaptive':
        # Frequency vector for raw data
        freqs = np.fft.fftfreq(ns) * fs
        f_abs = np.abs(freqs)
        f_abs[0] = f_abs[1]
        # Account for the finite window
        if leakage:
            pers_f = psd.periodogram_mean(cov_funcs, fs, ns, wd_func)
        else:
            pers_f = cov_funcs(f_abs)
        # Start and end frequencies
        df = fs / ns
        k_min = int(fmin/ df)
        k_max = int(fmax / df)
        # Choose segment sizes
        segment_sizes = psd.index_grid(size_min, size_max, k_min, k_max)
        # Compute the smoothed spectrum
        i_mid, pers = psd.smooth(pers_f, k_min, segment_sizes)
        # Segment middle frequencies
        fper = i_mid * df
        # Effective segment size
        nenbw = psd.normalized_equivalent_noise_bandwidth(wd_func)
        k_seg = segment_sizes  / nenbw

    else:
        raise ValueError("Averaging method not recognized")

    return fper, pers, k_seg
