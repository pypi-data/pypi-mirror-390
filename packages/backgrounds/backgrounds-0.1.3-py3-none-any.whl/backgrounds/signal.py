# -*- coding: utf-8 -*-
# Author: Quentin Baghi 2022 <quentin.baghi@protonmail.com>
# This code provides routines for computing SGWB PSD from a response model
import numpy as np
import healpy as hp
import jax
import jax.numpy as jnp
from . import StochasticBackgroundResponse, tdi, utils

H0 = 3.24e-18 # s^{-1}


# Define the SGWB PSD
@jax.jit
def sgwb_psd(freq, spec_index=0.5, freq0=1e-3, omega_gw=1e-14, fmin=1e-5):
    """SGWB PSD in Hz^{-1}."""
    # This is in order to sample with multiple walkers
    omega_gw = jnp.atleast_1d(omega_gw)
    spec_index = jnp.atleast_1d(spec_index)
    f_shift = freq + fmin
    omega_gw_f = omega_gw * (f_shift / freq0) ** spec_index
    Sh = (3 * H0**2) * omega_gw_f.T / (4 * jnp.pi**2 * f_shift**3)
    return Sh.squeeze()

@jax.jit
def sgwb_psd_running(freq, spec_index=1.0, alpha=-0.1, freq0=1e-3, omega_gw=10**(-12.65),
                     fmin=1e-5):
    """SGWB PSD for a power law with running in Hz^{-1}."""
    f_shift = freq + fmin
    omega_gw_f = omega_gw * (f_shift / freq0) ** (spec_index + alpha * jnp.log(f_shift / freq0))
    return (3 * H0**2) * omega_gw_f / (4 * jnp.pi**2 * f_shift**3)

@jax.jit
def sgwb_psd_electroweak(freq, a=3, b=4, c=3, f_star=4e-4, omega_gw=10**(-7.2), fmin=1e-5):
    """SGWB PSD for a power law with running in Hz^{-1}."""
    f_shift = freq + fmin
    omega_gw_f = omega_gw / (b * (f_shift / f_star)**(-a/c) 
                             + a * (f_shift / f_star)**(b/c))**c

    return (3 * H0**2) * omega_gw_f / (4 * jnp.pi**2 * f_shift**3)

@jax.jit
def sgwb_psd_astro(freq, omega_gw=1.72e-11, spec_index=0.741, big_b=1.54e4, freq0=7.0e-3,
                   fmin=1e-5):
    """
    Astrophysical GW background PSD from https://arxiv.org/pdf/2407.10642

    Parameters
    ----------
    freq : ndarray
        frequencies
    big_a : float
        overall amplitude parameter
    big_b : float
        exponential decay rate
    freq0 : _type_, optional
        reference frequency, by default 7.e-3
    n : float, optional
        overall power law index, by default 0.741

    Returns
    -------
    psd: ndarray
        PSD computed at the given frequencies

    """
    f_shift = freq + fmin
    omega_gw_f = omega_gw*(f_shift/freq0)**spec_index * (
        1 + (f_shift/freq0)**4.15)**(-0.255) * jnp.exp(-big_b*f_shift**3)

    return (3 * H0**2) * omega_gw_f / (4 * jnp.pi**2 * freq**3)


@jax.jit
def sgwb_psd_fopt(freq, omega_gw, fp, n):

    # Compute eq. for FOPT from the LISA Red Book p. 63 
    S_fopt = omega_gw * (freq/fp)**3 * ( 7 / (4 + 3 * (freq/fp)**2 ) )**n
    S_fopt *= (3 * H0**2) / (4 * jnp.pi**2 * freq**3)

    return S_fopt.squeeze()

@jax.jit
def fopt_wrapper(freq, params, **sgwb_kwargs):
    """
    Wrapper of the First Order Phase Transitions sgwb_psd function

    NOTE: Only the Sound-Waves part is modelled here. The Turbulence part
    is missing. See [] for details.

    Parameters
    ----------
    freq : ndarray
        frequency array [Hz]
    params : ndarray
        SGWB parameters, where the first entry is log10(Omega)
        the second entry is the fp, and the third the spectral index.
    sgwb_kwargs : dictionnary
        Dictionary of keyword parameters
        
    Returns
    -------
    psd : ndarray
        SGWB PSD

    """
    # Get individual parameters
    log10_omega_gw, fp, n = jnp.split(params, 3)
    omega_gw =  jnp.atleast_1d(10 ** log10_omega_gw)

    return sgwb_psd_fopt(freq, omega_gw, fp, n)

@jax.jit
def sgwb_wrapper(freq, params, **sgwb_kwargs):
    """
    Wrapper of the powerl-law sgwb_psd function

    Parameters
    ----------
    freq : ndarray
        frequency array [Hz]
    params : ndarray
        SGWB parameters, where the first entry is log10(Omega)
        and the second entry is the spectral index
    sgwb_kwargs : dictionnary
        Dictionary of keyword parameters
        
    Returns
    -------
    psd : ndarray
        SGWB PSD

    """

    # Get individual parameters
    [omega_power, n] = jnp.split(params, 2)
    omega_gw =  10 ** omega_power

    return sgwb_psd(freq, spec_index=n, omega_gw=omega_gw, **sgwb_kwargs)


def sgwb_wrapper_omegaonly(freq, log10omega, **sgwb_kwargs):
    """
    Wrapper of the powerl-law sgwb_psd function with fixed spectral index.

    Parameters
    ----------
    freq : ndarray
        frequency array [Hz]
    log10omega : float
        log10(Omega)
    sgwb_kwargs : dictionnary
        Dictionary of keyword parameters
        
    Returns
    -------
    psd : ndarray
        SGWB PSD

    """

    return sgwb_psd(freq, omega_gw=10**log10omega, **sgwb_kwargs)


def sgwb_wrapper_astro(freq, params, **sgwb_kwargs):
    """_summary_

    Parameters
    ----------
    freq : ndarray
        frequency array [Hz]
    params : ndarray
        SGWB parameters, where the first entry is log10(Omega)
        the second entry is the fp, and the third the spectral index.
    big_b : flaot, optional
        exponential decay rate, by default 1.54e4
    freq0 : float, optional
        reference frequency, by default 7.0e-3

    Returns
    -------
    psd: ndarray
        PSD computed at the given frequencies
    """
    log10_omega, n = jnp.split(params, 2)
    omega_gw = 10**log10_omega

    return sgwb_psd_astro(freq, omega_gw=omega_gw, spec_index=n, **sgwb_kwargs)

@jax.jit
def params_wrapper_log10_omegaonly(param):
    """
    Wrapper to convert sampling parameters to physical parameters
    for a power-law model with 2 parameters

    Parameters
    ----------
    params : ndarray
        SGWB power-law parameters log10(omega) and n

    Returns
    -------
    spec_index, omega_gw
        spectral index and Omega_GW
    """
    omega_gw = 10**param

    return jnp.atleast_1d(omega_gw)


class GeneralSignalModel(StochasticBackgroundResponse):
    """
    General class for SGWB inference.
    """

    def __init__(self, skymap, freq, time, orbits, gw_psd, ndim, sgwb_kwargs=None,
                 orbit_interp_order=1, tdi_tf_func=tdi.compute_tdi_tf,
                 tdi_var='xyz', gen="2.0", ltt=None, parallel=False, average=False):
        """instanciate GeneralSignalModel class

            Parameters
            ----------
            freq : ndarray
                frequency array [Hz]
            time : ndarray or float
                time [s] at which the noise response is computed
            orbits : str
                orbit file path
            gw_psd : callable
                SGWB spectrum function (of frequency)
            ndim : int
                Dimension of the SGWB parameter space
            sgwb_kwargs : dic
                keyword arguments for the SGWB PSD
            orbit_interp_order : int, optional
                order of the orbit interpolator, by default 1
            tdi_tf_func : callable, optional
                function yielding the TDI transfer function of the noise,
                by default tdi.compute_tdi_tf
            gen : str, optional
                TDI generation, by default "2.0"
            ltt : list, optional
                list of light travel time delays functions (of time). If provided,
                they are used instead of the orbit file.
            parallel : bool, optional
                if True, the TDI kernel matrix is computed using parallelization over
                the skymap pixels.
            average : bool, optional
                if True, the response matrix is averaged over all times.

        """

        super().__init__(skymap, orbits=orbits, ltt=ltt, orbit_interp_order=orbit_interp_order,
                         tdi_tf_func=tdi_tf_func)

        # Frequencies
        self.freq = freq
        self.time = time

        # SGWB transfer function
        self.gen = gen
        self.tdi_var = tdi_var

        # SGWB input PSD model
        self.gw_psd = gw_psd
        if sgwb_kwargs is None:
            self.sgwb_kwargs = {}
        else:
            self.sgwb_kwargs = sgwb_kwargs
        # Dimension of the model parameters
        self.ndim = ndim
        # Compute the GW TDI response matrix (nf x 6 x 6 or nt x nf x 6 x 6)
        self.g_mat = self.compute_tdi_kernel(self.freq, self.time, tdi_var=self.tdi_var,
                                             gen=self.gen, parallel=parallel)
        # Only the diagonal elements for PSDs only
        self.g_mat_diag = np.array([self.g_mat[..., i, i]
                                    for i in range(self.g_mat.shape[-1])]).T
        # Average over all times if required
        if (average) & (self.g_mat.ndim == 4):
            self.g_mat = np.mean(self.g_mat, axis=1)
            self.g_mat_diag = np.mean(self.g_mat_diag, axis=1)

    def compute_covariances(self, params):
        """Compute the full covaraince contribution from the SGWB

        Parameters
        ----------
        params : ndarray
            SGWB sampling parameters

        Returns
        -------
        psd : ndarray
            nf x 3 x 3 frequency-domain covariances, or nf x nt x 3 x 3 time-frequency covariances
        """

        s_h = self.gw_psd(self.freq, params, **self.sgwb_kwargs)

        return utils.compute_covariances(s_h, self.g_mat)

    def compute_strain_psds(self, params, freqs=None):
        """
        Compute SGWB strain PSD (without LISA nor TDI response)

        Parameters
        ----------
        params : ndarray
            SGWB parameters (log Omega, n)
        freqs : ndarray
            Frequency array, if different from self.freq

        Returns
        -------
        link_psd : ndarray
            nf 
        
        """

        if freqs is None:
            freq = self.freq
        else:
            freq = freqs

        # Compute PSD
        s_h = self.gw_psd(freq, params, self.sgwb_kwargs)

        return s_h


class Galaxy:
    """A class to compute galactic matter density map and confusion foreground PSD model.
    """

    def __init__(self, a=0.25, rb=0.5, rd=2.5, zd=0.2, rho0=1.0, tobs_yrs=1.0, params=None,
                 snr=7.0, nside=32):
        """
        Constructor of the Galaxy class.

        Parameters
        ----------
        a : float, optional
            Relative weight of the stellar density in the buldge compared to the disk,
            by default 0.25
        rb : float, optional
            Characteristic radius of the buldge [kpc], by default 0.5
        rd : float, optional
            Characteristic radius of the disk [kpc], by default 2.5
        zd : float, optional
            Characteristic height of the disk [kpc], by default 0.2
        rho0 : float, optional
            Stellar density normalization, by default 1.0
        tobs_yrs : float, optional
            Observation time in years, by default 1.0
        params : _type_, optional
            Parameters of the Galaxy foreground frequency PSD, by default None
        snr : float, optional
            _description_, by default 7.0
        nside : int, optional
            Skymap resolution parameter

        Raises
        ------
        NotImplementedError
            _description_
        NotImplementedError
            _description_
        """

        # Relative weight of the stellar density in the buldge compared to the disk
        self.a = a
        # Characteristic radius of the buldge [kpc]
        self.rb = rb
        # Characteristic radius of the disk [kpc]
        self.rd = rd
        # Characteristic height of the disk [kpc]
        self.zd = zd
        # Stellar density normalization
        self.rho0 = rho0

        self.omega0 = 2e-11
        self.amp = 1.0

        self.tobs_yrs = tobs_yrs
        self.tmin = 0.25
        self.tmax = 10.0

        # Healpix galactic map parameters
        self.nside = nside
        self.npix = hp.nside2npix(self.nside)

        if snr not in [5.0, 7.0]:
            print('We accept SNR to be 5 or 7', 'given', snr)
            raise NotImplementedError

        if params is None:
            if snr == 5:
                l6_snr5 = [1.14e-44, 1.66, 0.00059, -0.15, -2.78, -0.34, -2.55]
                self.Ampl, self.alpha, self.fr2, self.af1, self.bf1, self.afk, self.bfk = l6_snr5
            elif snr == 7:
                l6_snr7 = [1.15e-44, 1.56, 0.00067, -0.15, -2.72, -0.37, -2.49]
                self.Ampl, self.alpha, self.fr2, self.af1, self.bf1, self.afk, self.bfk = l6_snr7
        else:
            self.Ampl, self.alpha, self.fr2, self.af1, self.bf1, self.afk, self.bfk = params

        if (self.tobs_yrs < self.tmin or self.tobs_yrs > self.tmax):
            print('Galaxy fit is valid between 3 months and 10 years')
            print('we do not extrapolate', self.tobs_yrs, ' not in', self.tmin, self.tmax)
            raise NotImplementedError("")

        self.fr1 = 10.**(self.af1 * np.log10(self.tobs_yrs) + self.bf1)
        self.frk = 10.**(self.afk * np.log10(self.tobs_yrs) + self.bfk)

    @staticmethod
    def sech(z):
        """
        Inverse hyperbolic cosine function.

        Parameters
        ----------
        z : ndarray or float
            variable

        Returns
        -------
        ndarray or float
            1/cosh(z)
        """

        return 2 / (np.exp(z) + np.exp(-z))

    @staticmethod
    def change_coord(m, coord):
        """ Change coordinates of a HEALPIX map

        Parameters
        ----------
        m : map or array of maps
        map(s) to be rotated
        coord : sequence of two character
        First character is the coordinate system of m, second character
        is the coordinate system of the output map. As in HEALPIX, allowed
        coordinate systems are 'G' (galactic), 'E' (ecliptic) or 'C' (equatorial)

        Example
        -------
        The following rotate m from galactic to equatorial coordinates.
        Notice that m can contain both temperature and polarization.
        >>>> change_coord(m, ['G', 'C'])
        """
        # Basic HEALPix parameters
        npix = m.shape[-1]
        nside = hp.npix2nside(npix)
        ang = hp.pix2ang(nside, np.arange(npix))

        # Select the coordinate transformation
        rot = hp.Rotator(coord=reversed(coord))

        # Convert the coordinates
        new_ang = rot(*ang)
        new_pix = hp.ang2pix(nside, *new_ang)

        return m[..., new_pix]

    def density(self, x, y, z):
        """
        Coordinates in pc.
        
        Parameters
        ----------
        x, y, z : ndarrays
            galactocentric cartesian coordinates [kpc]

        Returns
        -------
        rho : ndarray
            Galaxy matter density as a function of location.
        """

        u2 = x**2 + y**2
        r2 = u2 + z**2

        rho = self.rho0 * (
            self.a * np.exp(-r2/(0.5*self.rb**2)) \
            + (1-self.a)*np.exp(-np.sqrt(u2)/self.rd)*(self.sech(z/self.zd))**2)

        return rho

    def integrate_line(self, xp, yp, zp, n_points=1000, lmin=1e-3, lmax=20.0, xsun=-8.1,
                       ysun=0.0, zsun=0.0):
        """_summary_

        Parameters
        ----------
        xp : ndarray
            x coordinate on the line of sight [kpc]
        yp : ndarray
            x coordinate on the line of sight [kpc]
        zp : ndarray
            x coordinate on the line of sight [kpc]
        n_points : int, optional
            number of points to approximate the integral by Riemann, by default 1000
        lmin : float, optional
            minimum line of sight distance, by default 1e-3 [kpc]
        lmax : float, optional
            maximum line of sight distance, by default 20.0 [kpc]
        xsun : float, optional
            x coordinate of the Sun in the Galactocentric coordinate system, by default -8.1
        ysun : float, optional
            y coordinate of the Sun in the Galactocentric coordinate system, by default 0
        zsun : float, optional
            z coordinate of the Sun in the Galactocentric coordinate system, by default 0

        Returns
        -------
        float
            integral of the Galactic matter density along the line of sight
        """

        # Line of sight vector
        n_vect = np.arange(0, n_points)
        u_max = np.log(lmax)
        u_min = np.log(lmin)
        du = (u_max - u_min) / n_points
        un = du * n_vect + u_min
        ln = np.exp(un)
        x = ln * xp + xsun
        y = ln * yp + ysun
        z = ln * zp + zsun

        return np.sum(self.density(x, y, z) * du * ln)

    def get_map_cartesian_coords(self):
        """Compute the cartesian coordinates of the vectors pointing towards each pixel
        in the skymap

        Returns
        -------
        ndarray
            Cartesian coordinates in the Galacto-centric coordinate system of the vectors pointing 
            towards each pixel in the skymap, size npix x 3
        """

        return np.asarray([hp.pixelfunc.pix2vec(self.nside, ipix) for ipix in range(self.npix)])

    def compute_map(self, n_points=1000, lmin=1e-3, lmax=20, xsun=-8.1, coord="G", normalize=False):
        """_summary_

        Parameters
        ----------
        n_points : int, optional
            number of points to approximate the integral by Riemann, by default 1000
        lmin : float, optional
            minimum line of sight distance, by default 1e-3 [kpc]
        lmax : float, optional
            maximum line of sight distance, by default 20.0 [kpc]
        xsun : float, optional
            x coordinate of the Sun in the Galactocentric coordinate system, by default -8.1
        coord : str, optional
            coordinate system in which the map must be computed among. Should be "G" for Galactic
            and "E" for ecliptic. Default is "G".

        Returns
        -------
        map_tot : ndarray
            healpix map of the Galaxy matter density
        
        """

        # Get map pixel coordinates
        coords = self.get_map_cartesian_coords()
        # Integrate along each line of sight
        map_tot = np.asarray([self.integrate_line(point[0], point[1], point[2], n_points=n_points,
                              lmin=lmin, lmax=lmax, xsun=xsun)
                              for point in coords])
        if coord == "E":
            map_tot = self.change_coord(map_tot, ["G", "E"])
        if normalize:
            map_min = np.min(map_tot)
            map_max = np.max(map_tot)
            map_tot = (map_tot - map_min) / (map_max - map_min)

        return map_tot

    def psd(self, freq):
        """Galactic foreground PSD model assuming a SNR threshold for bright GB subtraction.

        Parameters
        ----------
        freq : ndarray
            frequency array [Hz]

        Returns
        -------
        ndarray
            one-sided power spectral density in relative frequency shift (1/Hz)
        """

        sg = self.Ampl*np.exp(-(freq/self.fr1)**self.alpha) *\
              (freq**(-7./3.))*0.5*(1.0 + np.tanh(-(freq-self.frk)/self.fr2))

        return sg

    def psd_wrapper(self, freq, params, minimum=1e-49):
        """
        Galactic foreground PSD model assuming parametrized amplitude
        """
        ampl = 10**params
        sg = ampl * np.exp(-(freq/self.fr1)**self.alpha) *\
          (freq**(-7./3.))*0.5*(1.0 + np.tanh(-(freq-self.frk)/self.fr2))
        sg[sg<minimum] = minimum

        return sg
