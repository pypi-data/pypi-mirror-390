# -*- coding: utf-8 -*-
# Author: Quentin Baghi 2021 <quentin.baghi@protonmail.com>
import numpy as np
import jax
import jax.numpy as jnp
from interpax import interp1d, Interpolator1D, Akima1DInterpolator
from lisaconstants import SIDEREALYEAR_J2000DAY as YEAR_day
from lisaconstants import c
from . import utils, Response, tdi


known_noise_config = ["Proposal", "SciRDv1", "MRDv1", "MRD_MFR",
                      "sangria", "spritz", "redbook"]
YEAR = YEAR_day * 24 * 3600
MOSAS = ['12', '23', '31', '13', '32', '21']


class GeneralNoiseModel(Response):
    """
    General mother class for noise models
    """

    def __init__(self, freq, t0, orbits, orbit_interp_order=1,
                 tdi_tf_func=tdi.compute_tdi_tf, gen="2.0", average=True, ltt=None):
        """
        Class constructor.

        Parameters
        ----------
        freq : ndarray
            frequency array [Hz]
        t0 : ndarray or float
            time [s] at which the noise response is computed
        orbits : str
            orbit file path
        orbit_interp_order : int, optional
            order of the orbit interpolator, by default 1
        tdi_tf_func : callable, optional
            function yielding the TDI transfer function of the noise,
            by default tdi.compute_tdi_tf
        gen : str, optional
            TDI generation, by default "2.0"
        average : bool, optional
            If True, and if t0 is an array, computes the average of the TDI kernel matrix
            over all times. If False, compute_covariances will returns a 
            nf x nt x 3 x 3 array where the first dimension correspond to time samples.
        ltt : dictionary of callables
            light travel times. If None, they are computed from the orbit file. Default is None.

        """

        super().__init__(orbits, ltt=ltt, orbit_interp_order=orbit_interp_order,
                         tdi_tf_func=tdi_tf_func)

        self.freq = freq
        self.logfreq = np.log(self.freq)
        self.t0 = t0
        self.gen = gen
        self.average = average
        self.tdi_corr = []
        self.tdi_tf = self.compute_transfer_matrix(self.freq)
        # Dimension of the model
        self.ndim = 0

    def compute_transfer_matrix(self, freq):
        """
        Compute the transfer matrix to go from single-link measurements
        to TDI

        Parameters
        ----------
        freq : ndarray
            frequency array [Hz]
        """
        self.tdi_tf = self.tdi_tf_func(freq, self.ltt, self.t0, gen=self.gen)
        # Precompute quantities useful if equal, uncorrelated noises (nf x n_tdi x n_tdi) or
        # (nt x nf x n_tdi x n_tdi)
        if isinstance(self.t0, (np.ndarray, list)):
            self.tdi_corr = utils.multiple_dot(
                self.tdi_tf, np.swapaxes(self.tdi_tf.conj(), 2, 3))
            # Average the correlation matrix
            if self.average:
                self.tdi_corr = np.mean(self.tdi_corr, axis=1)
        else:
            self.tdi_corr = utils.multiple_dot(
                self.tdi_tf, np.swapaxes(self.tdi_tf.conj(), 1, 2))

        return self.tdi_tf

    def compute_link_psd(self, theta, **kwargs):
        """
        Compute the single-link PSD

        Parameters
        ----------
        args : iterable
            psd model parameters
        kwargs : dictionary
            psd model keyword arguments

        Returns
        -------
        s_n : ndarray
            psd 
        """
        raise NotImplementedError("compute_link_psd method not implemented.")

    def compute_link_log_psd(self, theta, **kwargs):
        """
        Computes single-link log-PSDs.

        Parameters
        ----------
        theta : ndarray, optional
            model parameters, by default None
        freq : ndarray
            frequency array [Hz]
        mosa : str, optional
            MOSA indices, by default '12'
        ffd : bool, optional
            if True, returns the PSD in units of fractional frequency deviation, by default True

        Returns
        -------
        log_s_n : ndarray
           log-psd computed at all frequencies freq.
        """

        return np.log(self.compute_link_psd(theta, **kwargs))

    def compute_covariances(self, theta, **kwargs):
        """
        Calculate the full covariances at frequencies finds.

        Parameters
        ----------
        theta : ndarray, optional
            model parameters, by default None
        freq : ndarray
            frequency array [Hz]
        mosa : str, optional
            MOSA indices, by default '12'
        ffd : bool, optional
            if True, returns the covariance in units of fractional frequency deviation,
            by default True

        Returns
        -------
        cov_tdi_n : ndarray
            matrix of covariances for all channels, size nf x 3 x 3 
            (if t0 is a float or average is True) or size nf x nt x 3 x 3
        """

        # Compute single-link PSD
        s_n = self.compute_link_psd(theta, **kwargs)
        # Apply TDI transfer matrix to the single-link PSDs
        cov_tdi_n = utils.compute_covariances(s_n, self.tdi_corr)

        return cov_tdi_n


class AnalyticOMSNoiseModel(GeneralNoiseModel):
    """
    General class to represent a single-link analytical OMS noise model
    """

    def __init__(self, freq, t0, orbits, orbit_interp_order=1, tdi_tf_func=tdi.compute_tdi_tf,
                 gen="2.0",
                 central_freq=281600000000000.0,
                 oms_isi_carrier_asds=7.9e-12,
                 oms_fknees=0.002, fs=None, duration=None, average=True, ltt=None):
        """
        Class constructor.

        Parameters
        ----------
        freq : ndarray
            frequency array [Hz]
        t0 : float
            time [s] at which the noise response is computed
        orbits : str
            orbit file path
        orbit_interp_order : int, optional
            order of the orbit interpolator, by default 1
        gen : str, optional
            TDI generation, by default "2.0"
        central_freq : float, optional
            laser central frequency, by default 281600000000000.0
        isi_carrier_asds : float or dic, optional
            ASDs [unit/sqrt{Hz}] of the science interferometer noises, by default 7.9e-12
        fknees : float or dic, optional
            Knee frequencies [Hz] of the science interferometer noises, by default 0.002
        """

        super().__init__(freq, t0, orbits, orbit_interp_order=orbit_interp_order,
                         tdi_tf_func=tdi_tf_func, gen=gen, average=average, ltt=ltt)

        self.central_freq = central_freq
        self.ndim = 1
        self.fs = fs
        self.duration = duration

        if isinstance(oms_isi_carrier_asds, float):
            self.oms_isi_carrier_asds = {mosa: oms_isi_carrier_asds
                                         for mosa in MOSAS}
        if isinstance(oms_fknees, float):
            self.oms_fknees = {mosa: oms_fknees
                               for mosa in MOSAS}

    def compute_link_psd(self, theta, **kwargs):
        """Model for OMS noise PSD in ISI carrier beatnote fluctuations.
        
        Parameters
        ----------
        theta : float
            Correction amplitude parameter. Applies a factor 10**theta
            in front of the PSD model.
        freq : ndarray or float
            Frequencies [Hz] where to compute the PSD
        mosa : str
            MOSA index ij

        Returns
        -------
        psd_hertz : PDD in Hz / Hz or /Hz

        """
        freq = kwargs.get('freq', None)
        mosa = kwargs.get('mosa', '12')
        if freq is None:
            freq = self.freq

        asd = self.oms_isi_carrier_asds[mosa]
        fknee = self.oms_fknees[mosa]

        return compute_oms_link_psd(theta, freq, self.fs, self.duration, asd=asd, fknee=fknee)

    def compute_ref_psd(self, freq):
        """Reference Model for OMS noise PSD in ISI carrier beatnote fluctuations.
        
        Parameters
        ----------
        freq : ndarray or float
            Frequencies [Hz] where to compute the PSD

        Returns
        -------
        psd_hertz : PDD in Hz / Hz or /Hz

        """

        return self.compute_link_psd(0.0, freq=freq, mosa='12')


class AnalyticTMNoiseModel(GeneralNoiseModel):
    """
    General class to represent a single-link analytical TM noise model
    """

    def __init__(self, freq, t0, orbits, orbit_interp_order=1, tdi_tf_func=tdi.compute_tdi_tf_tm,
                 gen="2.0",
                 central_freq=281600000000000.0,
                 tm_isi_carrier_asds=2.4e-15,
                 tm_fknees=0.0004, fs=None, duration=None, average=True, ltt=None):
        """
        Class constructor.

        Parameters
        ----------
        freq : ndarray
            frequency array [Hz]
        t0 : float
            time [s] at which the noise response is computed
        orbits : str
            orbit file path
        orbit_interp_order : int, optional
            order of the orbit interpolator, by default 1
        gen : str, optional
            TDI generation, by default "2.0"
        central_freq : float, optional
            laser central frequency, by default 281600000000000.0
        isi_carrier_asds : float or dic, optional
            ASDs [unit/sqrt{Hz}] of the science interferometer noises, by default 7.9e-12
        fknees : float or dic, optional
            Knee frequencies [Hz] of the science interferometer noises, by default 0.002
        fs : float
            Sampling frequency (optional). If provided, it is used to compute the effect 
            of filters in the simulation.
        duration : float
            Observation duration (optional).
        """

        super().__init__(freq, t0, orbits, orbit_interp_order=orbit_interp_order,
                         tdi_tf_func=tdi_tf_func, gen=gen, average=average, ltt=ltt)

        self.central_freq = central_freq
        self.fs = fs
        self.duration = duration
        self.ndim = 1

        if isinstance(tm_isi_carrier_asds, float):
            self.testmass_asds = {mosa: tm_isi_carrier_asds
                                         for mosa in MOSAS}
        if isinstance(tm_fknees, float):
            self.testmass_fknees = {mosa: tm_fknees
                               for mosa in MOSAS}

    def compute_link_psd(self, theta, **kwargs):
        """Model for OMS noise PSD in ISI carrier beatnote fluctuations.
        
        Parameters
        ----------
        theta : float
            Correction amplitude parameter. Applies a factor 10**theta
            in front of the PSD model.
        freq : ndarray or float
            Frequencies [Hz] where to compute the PSD
        mosa : str
            MOSA index ij
        ffd : bool
            if ffd is True, returns the PSD in fractional frequency deviation

        Returns
        -------
        psd_hertz : PDD in Hz / Hz or /Hz

        """
        freq = kwargs.get('freq', None)
        mosa = kwargs.get('mosa', '12')
        if freq is None:
            freq = self.freq

        asd = self.testmass_asds[mosa]
        fknee = self.testmass_fknees[mosa]

        return compute_tm_link_psd(theta, freq, self.fs, self.duration, asd=asd, fknee=fknee)

    def compute_ref_psd(self, freq):
        """Reference Model for OMS noise PSD in ISI carrier beatnote fluctuations.
        
        Parameters
        ----------
        freq : ndarray or float
            Frequencies [Hz] where to compute the PSD

        Returns
        -------
        psd_hertz : PDD in Hz / Hz or /Hz

        """

        return self.compute_link_psd(0.0, freq=freq, mosa='12')


class FunctionalNoiseModel(GeneralNoiseModel):
    """
    Noise model class implementing models where the log-PSD is an arbitrary function
    log PSD = f(theta).
    """

    def __init__(self, freq, t0, orbits, log_psd_func,
                 orbit_interp_order=1, ndim=0,
                 tdi_tf_func=tdi.compute_tdi_tf, gen="2.0",
                 ref_psd_func=None, average=True, ltt=None):
        """
        Class constructor.

        Parameters
        ----------
        freq : ndarray
            frequency array [Hz]
        t0 : float
            time [s] at which the noise response is computed
        orbits : str
            orbit file path
        log_psd_func : callable
            function that computes the single-link PSDs as a function of frequency freq
            and parameters theta
        orbit_interp_order : int, optional
            order of the orbit interpolator, by default 1
        ndim : int, optional
            dimension of the noise parameters
        tdi_tf_func : callable, optional
            function yielding the TDI transfer function of the noise,
            by default tdi.compute_tdi_tf
        gen : str, optional
            TDI generation, by default "2.0"
        ref_psd_func : callable
            If provided, the model parameters describe deviations from a reference log-PSD, 
            which can be computed through ref_psd_func. Otherwise, they describe the log_psd itself.
        average : bool, optional
            If True, and if t0 is an array, computes the average of the TDI kernel matrix
            over all times. If False, compute_covariances will returns a 
            nf x nt x 3 x 3 array where the first dimension correspond to time samples.
        ltt : dictionary of callables
            light travel times. If None, they are computed from the orbit file. Default is None.
        """

        super().__init__(freq, t0, orbits, orbit_interp_order=orbit_interp_order,
                         tdi_tf_func=tdi_tf_func, gen=gen, average=average, ltt=ltt)

        # Log-PSD function describing the single-link model
        self.log_psd_func = log_psd_func
        # If we are describing deviations from a reference PSD
        self.ref_psd_func = ref_psd_func
        if callable(ref_psd_func):
            self.ref_log_psd = np.log(self.ref_psd_func(self.freq))
        elif isinstance(ref_psd_func, (np.ndarray, list)):
            self.ref_log_psd = np.log(ref_psd_func)
        else:
            self.ref_log_psd = 0
        # Dimension of the parameter space
        self.ndim = ndim

    def compute_link_psd(self, theta, **kwargs):
        """
        Compute the single-link PSD

        Parameters
        ----------
        args : iterable
            psd model parameters
        kwargs : dictionary
            psd model keyword arguments

        Returns
        -------
        s_n : ndarray
            psd 
        """

        return jnp.exp(self.compute_link_log_psd(theta,  **kwargs))

    def compute_link_log_psd(self, theta, **kwargs):
        """
        Computes single-link log-PSDs.

        Parameters
        ----------
        theta : ndarray, optional
            model parameters, by default None

        Returns
        -------
        log_s_n : ndarray
           log-psd computed at all frequencies freq.
        """

        return self.log_psd_func(self.freq, theta) + self.ref_log_psd


class SplineNoiseModel(FunctionalNoiseModel):
    """
    Class constructing a noise model with a spline describing the
    single-link measurement noise PSD. Assumes orthogonal TDI
    """

    def __init__(self, freq, t0, orbits,
                 orbit_interp_order=1,
                 tdi_tf_func=tdi.compute_tdi_tf, gen="2.0", ref_psd_func=None,
                 average=True, ltt=None,
                 n_coeffs=5,
                 fixed_knots=False, f_knots=None, spline_type="akima"):
        """
        Likelihood with noise-only model.

        Parameters
        ----------
        freq : ndarray
            frequency array [Hz]
        t0 : float
            time [s] at which the noise response is computed
        orbits : str
            orbit file path
        orbit_interp_order : int, optional
            order of the orbit interpolator, by default 1
        tdi_tf_func : callable, optional
            function yielding the TDI transfer function of the noise,
            by default tdi.compute_tdi_tf
        gen : str, optional
            TDI generation, by default "2.0"
        ref_psd_func : callable
            If provided, the model parameters describe deviations from a reference log-PSD, 
            which can be computed through ref_psd_func. Otherwise, they describe the log_psd itself.
        average : bool, optional
            If True, and if t0 is an array, computes the average of the TDI kernel matrix
            over all times. If False, compute_covariances will returns a 
            nf x nt x 3 x 3 array where the first dimension correspond to time samples.
        ltt : dictionary of callables
            light travel times. If None, they are computed from the orbit file. Default is None.
        n_coeffs : int
            Number of spline coefficients
        f_knots : ndarray or None
            Spline interior knot frequencies. Used only if fixed_knots is False.
        fixed_knots : bool
            if True, the knot locations are fixed. Default is False.

        spline_type : str
            Type of splines between {bsplines, akimasplines}

        """

        # Number of spline coefficients
        self.n_coeffs = n_coeffs
        self.x_min = np.log(freq[0])
        self.x_max = np.log(freq[-1])
        self.spline_type = spline_type
        # Fixed knots flag
        self.fixed_knots = fixed_knots
        # Spline interior knot frequencies if provided
        self.f_knots = f_knots
        if self.f_knots is not None:
            self.logf_knots = np.log(f_knots)
        else:
            self.logf_knots = np.linspace(self.x_min, self.x_max, self.n_coeffs)[1:-1]
            self.f_knots = np.exp(self.logf_knots)
        # Number of parameters to fit
        if not fixed_knots:
            ndim = 2*self.n_coeffs - 2
        else:
            ndim = self.n_coeffs

        if fixed_knots:
            log_psd_func = self.log_psd_fixed_knots
        else:
            log_psd_func = self.log_psd_varying_knots

        super().__init__(freq, t0, orbits, log_psd_func,
                         orbit_interp_order=orbit_interp_order, ndim=ndim,
                         tdi_tf_func=tdi_tf_func, gen=gen,
                         ref_psd_func=ref_psd_func, average=average, ltt=ltt)

        # Spline design matrix
        self.x_mat = self.compute_design_matrix()

    def log_psd_fixed_knots(self, freq, theta):
        """
        Function computing the log PSD with splines.

        Parameters
        ----------
        freq : ndarray
            frequency array [Hz]
        theta : ndarray
            vector of parameters, including spline coefficients and spline locations
            (if fixed_knots is False)

        Returns
        -------
        ndarray
            log-PSD computed at the frequencies freq.
        """
        x_knots = jnp.concatenate([jnp.atleast_1d(self.x_min), self.logf_knots,
                                   jnp.atleast_1d(self.x_max)])

        return interp1d(self.logfreq, x_knots, theta, method=self.spline_type)

    def log_psd_varying_knots(self, freq, theta):
        """
        Function computing the log PSD with splines.

        Parameters
        ----------
        freq : ndarray
            frequency array [Hz]
        theta : ndarray
            vector of parameters, including spline coefficients and spline locations
            (if fixed_knots is False)

        Returns
        -------
        ndarray
            log-PSD computed at the frequencies freq.
        """

        y_knots, x_interior_knots = jnp.split(theta, [self.n_coeffs])

        x_knots = jnp.concatenate([jnp.atleast_1d(self.x_min), x_interior_knots,
                                   jnp.atleast_1d(self.x_max)])

        return interp1d(self.logfreq, x_knots, y_knots, method=self.spline_type)

    def compute_design_matrix(self, freq=None, basis_args=None):
        """
        Computation of the spline design matrix.

        Parameters
        ----------
        freq : ndarray or None
            frequencies where to compute the design matrix.
            if None, use the frequencies provided when 
            instantiating the class.
        intknots : ndarray
            parameters for interior knots locations (log-frequencies)

        Returns
        -------
        ndarray
            design matrix A such that the PSD can be written A.dot(coeffs)
        """

        if freq is None:
            logfreq = self.logfreq
        else:
            logfreq = jnp.log(freq)

        if basis_args is None:
            intknots = self.logf_knots
        else:
            intknots = basis_args

        x_knots = intknots[:]
        # # Recontruct knot vector
        # Add boundaries of the domain to the interior knots
        knots_list = [logfreq[0]] + list(x_knots) + [logfreq[-1]]
        logf_knots = jnp.asarray(knots_list)
        # Change the data and reset the spline class
        return interp1d(logfreq, logf_knots, jnp.eye(self.n_coeffs), method=self.spline_type)


@jax.jit
def compute_oms_link_psd(theta, freq, fs, duration, asd=7.9e-12,
                         fknee=0.002, central_freq=281600000000000.0):
    """Model for OMS noise PSD in ISI carrier beatnote fluctuations.
    
    Parameters
    ----------
    theta : float
        Correction amplitude parameter. Applies a factor 10**theta
        in front of the PSD model.
    freq : ndarray or float
        Frequencies [Hz] where to compute the PSD

    Returns
    -------
    psd_hertz : PDD in Hz / Hz or /Hz

    """

    if (fs is None) | (duration is None):
        psd_meters = asd**2 * (1 + (fknee / freq) ** 4)
        psd_hertz = (2 * jnp.pi * freq * central_freq / c) ** 2 * psd_meters
    else:
        fmin = 1.0 / duration
        psd_highfreq = (asd * fs * central_freq / c) ** 2 * jnp.sin(
            2 * jnp.pi * freq / fs
        ) ** 2
        psd_lowfreq = (
            (2 * jnp.pi * asd * central_freq * fknee**2 / c) ** 2
            * jnp.abs(
                (2 * np.pi * fmin)
                / (
                    1
                    - jnp.exp(-2 * jnp.pi * fmin / fs)
                    * jnp.exp(-2j * jnp.pi * freq / fs)
                )
            ) ** 2
            * 1 / (fs * fmin) ** 2
        )
        psd_hertz = psd_highfreq + psd_lowfreq

    return 10**theta * psd_hertz/central_freq**2


@jax.jit
def compute_tm_link_psd(theta, freq, fs, duration, asd=2.4e-15,
                        fknee=0.0004, central_freq=281600000000000.0):
    """Model for OMS noise PSD in ISI carrier beatnote fluctuations.
    
    Parameters
    ----------
    freq : ndarray or float
        Frequencies [Hz] where to compute the PSD
    mosa : str
        MOSA index ij
    ffd : bool
        if ffd is True, returns the PSD in fractional frequency deviation


    Returns
    -------
    psd : PDD in fractional frequency Hz / Hz

    """


    if (fs is None) | (duration is None):
        psd_acc = asd**2 * (1 + (fknee / freq) ** 2)
        psd_hertz = (2 * central_freq / (2 * jnp.pi * c * freq)) ** 2 * psd_acc
    else:
        fmin = 1.0 / duration
        psd_highfreq = (
            (2 * asd * central_freq / (2 * jnp.pi * c)) ** 2
            * jnp.abs(
                (2 * jnp.pi * fmin)
                / (
                    1
                    - jnp.exp(-2 * jnp.pi * fmin / fs)
                    * jnp.exp(-2j * jnp.pi * freq / fs)
                )
            )
            ** 2
            * 1
            / (fs * fmin) ** 2
        )
        psd_lowfreq = (
            (2 * asd * central_freq * fknee / (2 * jnp.pi * c)) ** 2
            * jnp.abs(
                (2 * jnp.pi * fmin)
                / (
                    1
                    - jnp.exp(-2 * jnp.pi * fmin / fs)
                    * jnp.exp(-2j * jnp.pi * freq / fs)
                )
            )
            ** 2
            * 1
            / (fs * fmin) ** 2
            * jnp.abs(1 / (1 - jnp.exp(-2j * jnp.pi * freq / fs))) ** 2
            * (2 * jnp.pi / fs) ** 2
        )
        psd_hertz = psd_lowfreq + psd_highfreq

    # if ffd:
    #     return 10**theta * psd_hertz / (2*central_freq)**2
    # return 10**theta * psd_hertz
    return 10**theta * psd_hertz / (2*central_freq)**2
