# -*- coding: utf-8 -*-
# Author: Quentin Baghi 2021 <quentin.baghi@protonmail.com>
"""
Code based on Jean-Baptiste Bayle's LISA GW Response to explore possibilities
to extend it to stationnary PSDs.
"""

import logging
from multiprocessing.dummy import Pool
import numpy as np
from numpy import cos, sin, pi, exp
from scipy.interpolate import InterpolatedUnivariateSpline
from packaging.version import Version
from packaging.specifiers import SpecifierSet
import lisagwresponse
from lisaconstants import c
from lisagwresponse.utils import dot, norm
from lisagwresponse.psd import white_generator
import healpy
import h5py
from .utils import multiple_dot, transform_covariance
from .tdi import compute_tdi_tf, aet_mat, convert

logger = logging.getLogger(__name__)


class Response(object):
    """
    General class to compute the GW response from an orbit file.
    """

    def __init__(self, orbits, orbit_interp_order=1, ltt=None, tdi_tf_func=compute_tdi_tf):

        self.orbits_path = orbits
        self.orbit_interp_order = orbit_interp_order
        self.x = None
        self.y = None
        self.z = None
        self.ltt = None
        self.LINKS = [12, 23, 31, 13, 32, 21]
        self.SC = [1, 2, 3]
        self.tdi_tf_func = tdi_tf_func

        if ltt is None:
            self._interpolate_orbits()
        else:
            self._constant_ltt(ltt)

    def _constant_ltt(self, ltt):

        def raise_error(t):
            raise RuntimeError("trying to interpolate SC position")

        self.x = {
            sc: raise_error
            for sc in self.SC
        }
        self.y = {
            sc: raise_error
            for sc in self.SC
        }
        self.z = {
            sc: raise_error
            for sc in self.SC
        }
        self.ltt = {
            link: lambda t, x=x: np.array(x)
            for link, x in ltt.items()
        }
        return None

    def _interpolate_orbits(self):
        """Interpolate orbit data (spacecraft positions and light travel times).

        Also check that orbit file is valid and supported.

        Raises:
            ValueError if orbit file is not supported.
        """
        logger.debug("Computing spline interpolation for orbits")
        interpolate = lambda t, data: InterpolatedUnivariateSpline(
                t, data, k=self.orbit_interp_order, ext='raise')

        with h5py.File(self.orbits_path, 'r') as orbitf:

            # Warn for orbit file development version
            version = Version(orbitf.attrs['version'])
            logger.debug("Using orbit file version %s", version)
            try:
                self.t0 = orbitf.attrs['t0']
            except:
                logger.warning("Not able to set the t0 from the orbits file")
                self.t0 = None
            if version.is_devrelease:
                logger.warning("You are using an orbit file in a development version")

            if version in SpecifierSet('== 1.*', True):
                self.x = {
                    sc: interpolate(orbitf['tcb/t'], orbitf[f'tcb/sc_{sc}']['x'])
                    for sc in self.SC
                }
                self.y = {
                    sc: interpolate(orbitf['tcb/t'], orbitf[f'tcb/sc_{sc}']['y'])
                    for sc in self.SC
                }
                self.z = {
                    sc: interpolate(orbitf['tcb/t'], orbitf[f'tcb/sc_{sc}']['z'])
                    for sc in self.SC
                }
                self.ltt = {
                    link: interpolate(orbitf['tcb/t'], orbitf[f'tcb/l_{link}']['tt'])
                    for link in self.LINKS
                }
            elif version in SpecifierSet('== 2.*', True):
                times = orbitf.attrs['t0'] + np.arange(orbitf.attrs['size']) * orbitf.attrs['dt']
                self.x = {
                    sc: interpolate(times, orbitf['tcb/x'][:, i, 0])
                    for i, sc in enumerate(self.SC)
                }
                self.y = {
                    sc: interpolate(times, orbitf['tcb/x'][:, i, 1])
                    for i, sc in enumerate(self.SC)
                }
                self.z = {
                    sc: interpolate(times, orbitf['tcb/x'][:, i, 2])
                    for i, sc in enumerate(self.SC)
                }
                self.ltt = {
                    link: interpolate(times, orbitf['tcb/ltt'][:, i])
                    for i, link in enumerate(self.LINKS)
                }
            else:
                raise ValueError(f"unsupported orbit file version '{version}'")

    def compute_tdi_design_matrix(self, freqs, t0, gen='2.0', average=True):
        """Compute the TDI transfer function matrix

        Parameters
        ----------
        freqs : ndarray
            frequency array [Hz]
        t0 : ndarray
            time (or time vector of size nt) where to compute the TDI design matrix or its average.
        gen : str, optional
            TDI generation, by default '2.0'
        average : bool, optional
            if True, compute the average of the design matrix over all times in t0

        Returns
        -------
        tdi_mat_eval
            TDI transfer function matrix for XYZ, array of size nf x 3 x 6 or size nf x nt x 3 x 6

        Raises
        ------
        ValueError
            TDI generation can only be 1.5 or 2.0.
        """
        # If we average over times
        if isinstance(t0, np.ndarray) & average:
            return np.mean(self.tdi_tf_func(freqs, self.ltt, t0, gen=gen), axis=1)
        # Otherwise we output the full matrix
        return self.tdi_tf_func(freqs, self.ltt, t0, gen=gen)


class StochasticPointSourceResponse(Response):
    """Generate response for a point-like gravitational-wave stochastic source.

    The +/x-polarized strains are white Gaussian noise.
    """

    def __init__(self, gw_beta, gw_lambda, **kwargs):

        super().__init__(**kwargs)

        self.gw_beta = gw_beta
        self.gw_lambda = gw_lambda
        self.compute_source_localization_vector(gw_beta, gw_lambda)

    @classmethod
    def from_gw(cls, pt_src):
        """Load StochasticPointSourceResponse arguments from StochasticPointSource object

        Parameters
        ----------
        pt_src : lisagwresponse.StochasticPointSource instance
             instance

        Returns
        -------
        class
            StochasticPointSourceResponse object
        """

        resp = cls(gw_beta=pt_src.gw_beta, gw_lambda=pt_src.gw_lambda, orbits=pt_src.orbits_path)

        return resp

    def compute_source_localization_vector(self, gw_beta, gw_lambda):
        """

        theta in [-pi, pi]
        phi in [0, 2pi]

        beta = theta - pi/2 in [-pi/2, pi/2]
        lambda = phi - pi [-pi, pi]

        Therefore 
        cos(theta) = sin(beta)


        Parameters
        ----------
        gw_beta : float
            ecliptic latitude of gravitational-wave source [rad]
        gw_lambda : float
            ecliptic longitude of gravitational-wave source [rad]
        """

        self.gw_beta = float(gw_beta)
        self.gw_lambda = float(gw_lambda)

        # Compute source-localization vector basis
        self.k = np.array([
            -cos(self.gw_beta) * cos(self.gw_lambda),
            -cos(self.gw_beta) * sin(self.gw_lambda),
            -sin(self.gw_beta),
        ])
        self.u = np.array([
            sin(self.gw_lambda),
            -cos(self.gw_lambda),
            0
        ])
        self.v = np.array([
            -sin(self.gw_beta) * cos(self.gw_lambda),
            -sin(self.gw_beta) * sin(self.gw_lambda),
            cos(self.gw_beta),
        ])

    def compute_kernel(self, links, f, t, deriv=0, t_shift=False, approx=False):
        """
        Compute LISA's single-link response to monochromatic GWs.

        Parameters
        ----------
        links : array_like
            list of single-links
        f : array_like
            frequency array where to compute the response. If f has more than one element,
            t should have only one element, and vice versa.
        t : array_like
            time array where to compute the response. If t has more than one element,
            f should have only one element, and vice versa.
        deriv : int, optional
            If greater than 0, compute the ith derivative, by default 0
        t_shift : bool, optional
            if t_shift is True, the response is shifted by exp(2*pi*f*t). Default is False.
        approx : bool, optional
            If True, use the cardinal sine approximation of the response, by default False

        Returns
        -------
        g_plus, g_cross : array_like
            Response kernels for + and x polarizations. Should have size len(links) x len(f),
            or len(links) x len(t) x len(f)

        Raises
        ------
        ValueError
            [description]
        """
        # pylint: disable=too-many-locals
        if isinstance(links, str):
            links = [links]

        # Compute emission and reception time at spacecraft
        trec = t  # (t)
        temi = np.repeat(trec[np.newaxis],
                            len(links), axis=0)  # (link, t)
        for link_index, link in enumerate(links):
            temi[link_index] -= self.ltt[link](t)

        # Compute spacecraft positions at emission and reception
        try:
            xrec = np.empty((len(links), len(t), 3))  # (link, t, coord)
            for link_index, link in enumerate(links):
                receiver = int(str(link)[0])
                xrec[link_index, :, 0] = self.x[receiver](trec)
                xrec[link_index, :, 1] = self.y[receiver](trec)
                xrec[link_index, :, 2] = self.z[receiver](trec)
            xemi = np.empty((len(links), len(t), 3))  # (link, t, coord)
            for link_index, link in enumerate(links):
                emitter = int(str(link)[1])
                xemi[link_index, :, 0] = self.x[emitter](temi[link_index])
                xemi[link_index, :, 1] = self.y[emitter](temi[link_index])
                xemi[link_index, :, 2] = self.z[emitter](temi[link_index])
        except ValueError as error:
            raise ValueError(
                "missing orbit information, use longer orbit file or adjust sampling") from error

        # Compute link unit vector
        n = xrec - xemi  # (link, t, coord)
        n /= norm(n)[..., np.newaxis]

        # Compute equivalent emission and reception time at the Sun
        trec_sun = trec[np.newaxis] - dot(xrec, self.k) / c  # (link, t)
        temi_sun = temi - dot(xemi, self.k) / c  # (link, t)
        # so temi = t - L - r_i.k / c

        # Compute antenna pattern functions
        xiplus = dot(n, self.u)**2 - dot(n, self.v)**2  # (link, t)
        xicross = 2 * dot(n, self.u) * dot(n, self.v)  # (link, t)

        if not t_shift:
            # size (link, t)
            dtrec = trec_sun - t[np.newaxis, :]
            dtemi = temi_sun - t[np.newaxis, :]
        else:
            dtrec = trec_sun[:]
            dtemi = temi_sun[:]

        if not approx:
            # dtemi and dtrec have dimension (link, t)
            # g must be (link, t, f)
            g = (2j*pi*dtemi[..., np.newaxis])**deriv * exp(2j*pi*f*dtemi[..., np.newaxis]) - \
                (2j*pi*dtrec[..., np.newaxis])**deriv * exp(2j*pi*f*dtrec[..., np.newaxis])
            # The denominator has size (link, t, f)
            denom = 2 * (1 - dot(n, self.k))
            # g+ and gx have dimension (link, t, f)
            g_plus = g * xiplus[..., np.newaxis] / denom[..., np.newaxis]
            g_cross = g * xicross[..., np.newaxis] / denom[..., np.newaxis]
        else:
            lvect = np.array(
                [self.ltt[link](t)*np.ones(f.shape[0]) for link in links])
            kn = dot(n, self.k)
            g = (pi * f * lvect / 2) * np.sinc(f *
                                                  lvect * (1 - kn)) * exp(-1j*pi*f*lvect*(1-kn))
            g += (pi * f * lvect / 2) * np.sinc(f *
                                                   lvect * (1 + kn)) * exp(-1j*pi*f*lvect*(3-kn))
            g_plus = g * xiplus
            g_cross = g * xicross

        # If there is only one time value, then we can get rid of the last dimension
        if t.size == 1:
            return g_plus[:, 0, :], g_cross[:, 0, :]
        # g_plus and g_cross should have dimensions link, t, f
        return g_plus, g_cross

    def compute_correlations(self, links, f, t, deriv=0, t_shift=False, approx=False):
        """
        Compute the correlation matrices from a stochastic point source, by polarization.

        Parameters
        ----------
        links : array_like
            list of single-links
        f : array_like
            frequency array where to compute the response. If f has more than one element,
            t should have only one element, and vice versa.
        t : array_like
            time array where to compute the response. If t has more than one element,
            f should have only one element, and vice versa.
        deriv : int, optional
            If greater than 0, compute the ith derivative, by default 0
        t_shift : bool, optional
            if t_shift is True, the response is shifted by exp(2*pi*f*t). Default is False.
        approx : bool, optional
            If True, use the cardinal sine approximation of the response, by default False

        Returns
        -------
        g_plus_mat, g_cross_mat : array_like
            Point-source correlation matrix, such that is S(f) is the GW source PSD, then
            the single-link spectrum matrix will be (g_plus_mat + g_cross_mat) * S(f)
            The size of g_plus_mat is nf x nt x 6 x 6

        """
        # Compute pixel response. Has dimension (links, t, f)
        gp, gc = self.compute_kernel(
            links, f, t, deriv=deriv, t_shift=t_shift, approx=approx)
        # Compute cross-PSD model
        g_plus_mat = multiple_dot(gp.T[..., np.newaxis],
                                  np.swapaxes(gp.T[..., np.newaxis].conj(), gp.ndim-1, gp.ndim))
        g_cross_mat = multiple_dot(gc.T[..., np.newaxis],
                                   np.swapaxes(gc.T[..., np.newaxis].conj(), gp.ndim-1, gp.ndim))

        return g_plus_mat, g_cross_mat

    def compute_tdi_kernel(self, fr, t0, tdi_var='aet', gen='2.0'):
        """
        Compute the SGWB covariance matrix in the TDI domain

        Parameters
        ----------
        fr : array_like
            frequency array where to compute the response.
        t0 : array_like
            time array where to compute the response.
        tdi_var : str, optional
            Chosen TDI variables. Default is 'aet', can be 'xyz'.
        gen : str, optional
            TDI generation, by default 2.0

        Returns
        -------
        g_mat : ndarray
            correlation matrix of size nt x nf x 3 x 3 (if t0 is a vector),
            otherwise array of nf x 3 x 3 
        """
        # Compute single-link kernel matrix
        gp, gc = self.compute_correlations(self.LINKS, fr, np.array([t0]))
        # Compute TDI transfer function
        tdi_mat = self.compute_tdi_design_matrix(fr, t0, gen=gen)
        # Transformation matrix
        if tdi_var == 'aet':
            if isinstance(t0, (np.ndarray, list)):
                tdi_mat = multiple_dot(aet_mat[np.newaxis, np.newaxis, :, :], tdi_mat)
            else:
                tdi_mat = multiple_dot(aet_mat[np.newaxis, :, :], tdi_mat)
        # Compute TDI kernel
        gp_ordered = gp[..., convert, :]
        gp_ordered = gp_ordered[..., convert]
        gc_ordered = gc[..., convert, :]
        gc_ordered = gc_ordered[..., convert]
        g_mat = transform_covariance(
            tdi_mat, gp_ordered) + transform_covariance(tdi_mat, gc_ordered)
        return g_mat


class StochasticBackgroundResponse(Response):
    """Generate response for a stochastic gravitational-wave background.

    The +/x-polarized strains are white Gaussian noise.
    """

    def __init__(self, skymap, **kwargs):

        super().__init__(**kwargs)

        self.skymap = skymap
        self.npix = len(skymap)
        self.nside = healpy.npix2nside(self.npix)
        # To store further computations
        self.f = None
        self.t = None
        self.links = self.LINKS
        self.g_plus_mat = None
        self.g_cross_mat = None

    @classmethod
    def from_gw(cls, sgwb):
        """Instantiate the class from a LISA GW Response's StochasticBackground object

        Parameters
        ----------
        gw : StochasticBackground instance
            SGWB LISA Response class
        """

        # Just choose the first pixel
        # Theta and phi are colatitude and longitude, respectively (healpy conventions)
        # They are converted to beta and lambda, latitude and longitude (LDC conventions)
        gw_theta, gw_phi = healpy.pix2ang(sgwb.nside, 0)
        gw_beta, gw_lambda = pi / 2 - gw_theta, gw_phi

        # Instantiate Strain object just to compute the orbits
        gw_src = lisagwresponse.StochasticPointSource(generator=white_generator(1.0),
                                                      gw_lambda=gw_lambda, gw_beta=gw_beta,
                                                      orbits=sgwb.orbits_path,
                                                      orbit_interp_order=sgwb.orbit_interp_order,
                                                      dt=sgwb.dt, size=sgwb.size, t0=sgwb.t0)

        # Instantiate the StochasticBackgroundResponse class
        resp = cls(skymap=sgwb.skymap, orbits=gw_src.orbits_path)

        return resp

    def add_pixel_response(self, pixel, deriv=0, t_shift=False, approx=False):
        """Add the response of a single pixel to the correlation matrices.
        This used is for sky-averaged response.

        Parameters
        ----------
        pixel : _type_
            _description_
        deriv : int, optional
            _description_, by default 0
        t_shift : bool, optional
            _description_, by default False
        approx : bool, optional
            _description_, by default False
        """

        gw_theta, gw_phi = healpy.pix2ang(self.nside, pixel)
        gw_beta, gw_lambda = pi / 2 - gw_theta, gw_phi
        source = StochasticPointSourceResponse(
            gw_beta, gw_lambda, orbits=self.orbits_path)
        # Compute pixel correlations matrix
        gp_mat, gc_mat = source.compute_correlations(
            self.links, self.f, self.t, deriv=deriv, t_shift=t_shift, approx=approx)
        # Compute cross-PSD model
        self.g_plus_mat += gc_mat * self.skymap[pixel]**2
        self.g_cross_mat += gp_mat * self.skymap[pixel]**2

    def compute_correlations(self, links, f, t, deriv=0, t_shift=False, approx=False,
                             parallel=False):
        """
        Compute the correlation matrices from a stochastic GW background, by polarization.

        Parameters
        ----------
        links : array_like
            list of single-links
        f : array_like
            frequency array where to compute the response.
        t : array_like or float
            time array where to compute the response.
        deriv : int, optional
            If greater than 0, compute the ith derivative, by default 0
        t_shift : bool, optional
            if t_shift is True, the response is shifted by exp(2*pi*f*t). Default is False.
        approx : bool, optional
            If True, use the cardinal sine approximation of the response, by default False

        Returns
        -------
        g_plus_mat, g_cross_mat : array_like
            SGWB correlation matrix, such that is S(f) is the GW source PSD, then
            the single-link spectrum matrix will be (g_plus_mat + g_cross_mat) * S(f)
            The size of teh output matrices is nf x nt x 6 x 6
        """

        self.f = f
        self.t = t
        self.links = links
        nf = len(self.f)
        nt = len(self.t)
        if nt == 1:
            self.g_plus_mat = np.zeros((nf, len(links), len(links)), dtype=complex)
            self.g_cross_mat = np.zeros((nf, len(links), len(links)), dtype=complex)
        else:
            self.g_plus_mat = np.zeros((nf, nt, len(links), len(links)), dtype=complex)
            self.g_cross_mat = np.zeros((nf, nt, len(links), len(links)), dtype=complex)

        if parallel:
            with Pool() as pool:
                # pool.map(self.add_pixel_response, range(self.npix))
                for _ in pool.imap_unordered(self.add_pixel_response, range(self.npix)):
                    pass
        else:
            for pixel in range(self.npix):
                self.add_pixel_response(pixel, deriv=deriv, t_shift=t_shift, approx=approx)

        return self.g_plus_mat, self.g_cross_mat

    def compute_tdi_kernel(self, fr, t0, tdi_var='aet', gen='2.0', parallel=False):
        """
        Compute the SGWB covariance matrix in the TDI domain

        Parameters
        ----------
        fr : array_like
            frequency array where to compute the response, size nf.
        t0 : array_like
            time array where to compute the response, size nt.
        tdi_var : str, optional
            Chosen TDI variables. Default is 'aet', can be 'xyz'.
        gen : str, optional
            TDI generation, by default 2.0

        Returns
        -------
        g_mat : ndarray
            correlation matrix of size nt x nf x 3 x 3 (if t0 is a vector),
            otherwise the size is nf x 3 x 3
        """

        # Compute single-link kernel matrix
        if isinstance(t0, (np.ndarray, list)):
            gp, gc = self.compute_correlations(self.LINKS, fr, t0,
                                               parallel=parallel)
        else:
            gp, gc = self.compute_correlations(self.LINKS, fr, np.asarray([t0]),
                                               parallel=parallel)
        # Compute TDI transfer function
        tdi_mat = self.tdi_tf_func(fr, self.ltt, t0, gen=gen)
        # Make an additional transformation if AET is requested
        if tdi_var == 'aet':
            tdi_mat = multiple_dot(aet_mat[np.newaxis, :, :], tdi_mat)
        # Compute TDI kernel
        gp_ordered = gp[..., convert, :]
        gp_ordered = gp_ordered[..., convert]
        gc_ordered = gc[..., convert, :]
        gc_ordered = gc_ordered[..., convert]
        g_mat = transform_covariance(
            tdi_mat, gp_ordered) + transform_covariance(tdi_mat, gc_ordered)

        return g_mat
