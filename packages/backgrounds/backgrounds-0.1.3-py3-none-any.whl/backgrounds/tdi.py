# -*- coding: utf-8 -*-
# Author: Quentin Baghi 2021 <quentin.baghi@protonmail.com>
from collections.abc import Iterable
import numpy as np
from . import utils


# AET matrix
aet_mat = np.array([[-1/np.sqrt(2), 0, 1/np.sqrt(2)],
                    [1/np.sqrt(6), -2/np.sqrt(6), 1/np.sqrt(6)],
                    [1/np.sqrt(3), 1/np.sqrt(3), 1/np.sqrt(3)]])
# Index conventions adopted below
mosa_order = ['12', '23', '31', '13', '21', '32']
# Flip the order of the two last MOSAs to convert to LISA GW Response convention and back
convert = np.array([0, 1, 2, 3, 5, 4])


def delay_operator(fr, delta_t):
    """Simple delay operator in the frequency domain, assuming
    infinite continuous observation time.

    Parameters
    ----------
    fr : ndarray
        frequency array (Hz)
    delta_t : float
        time delay (s)

    Returns
    -------
    exponential phase
        Frequency-domain delay operator
    """
    return np.exp(-2j * np.pi  * fr * delta_t)


def compute_tdi_tf(fr, tt, t_vect, gen='2.0', use_lisagwresponse_convention=False):
    """Compute the TDI transfer function matrix from eta variables to 
    TDI. It's valid for readout (OMS) noises.

    Parameters
    ----------
    fr : ndarray
        frequency array [Hz], size nf
    tt : dict
        dictionary of arm light travel times [s], size nt
    t_vect : ndarray
        time vector where to cumpute the light travel time.
    gen : str, optional
        TDI generation, by default '2.0'.
    use_lisagwresponse_convention : bool, optional
        If True, use the LISA GW Response convention for the TDI transfer function, by default
        False. If False, it assumes the following MOSA order: 12, 23, 31, 13, 21, 32.
        If True, it uses the LISA GW Response convention: 12, 23, 31, 13, 32, 21.

    Returns
    -------
    tdi_mat_eval
        TDI transfer function matrix for XYZ, array of size nf x nt x 3 x 6

    Raises
    ------
    ValueError
        TDI generation can only be 1.5 or 2.0.
    """

    if isinstance(t_vect, Iterable):
        fr_arr = np.asarray(fr)[:, np.newaxis]
    else:
        fr_arr = fr

    # Make sure that we have dimensions nf x nt
    d1 = delay_operator(fr_arr, tt[23](t_vect)).T
    d2 = delay_operator(fr_arr, tt[31](t_vect)).T
    d3 = delay_operator(fr_arr, tt[12](t_vect)).T
    d1p = delay_operator(fr_arr, tt[32](t_vect)).T
    d2p = delay_operator(fr_arr, tt[13](t_vect)).T
    d3p = delay_operator(fr_arr, tt[21](t_vect)).T
    # Build TDI transformation matrix
    zer = np.zeros(np.shape(d1))
    # TDI 1.5
    if gen == '1.5':
        tdi_mat = np.array(
            [[d2*d2p-1, zer, -(d3*d3p-1) * d2p, -(d3*d3p-1), (d2*d2p-1) * d3, zer],
                [-(d1*d1p-1) * d3p, d3*d3p-1, zer, zer, -(d1*d1p-1), (d3*d3p-1) * d1],
                [zer, - d1p * (d2*d2p-1), d1*d1p-1, (d1*d1p-1) * d2, zer, -(d2*d2p-1)]])
    # TDI 2.0
    elif gen == '2.0':
        tdi_mat = np.array(
                [[d2p*d2 + d2p*d2*d3*d3p - 1 - d3*d3p*d2p*d2*d2p*d2,
                zer,
                d2p + d2p*d2*d3*d3p*d3*d3p*d2p - d3*d3p*d2p - d3*d3p*d2p*d2*d2p,
                1 + d2p*d2*d3*d3p*d3*d3p - d3*d3p - d3*d3p*d2p*d2,
                d2p*d2*d3 + d2p*d2*d3*d3p*d3 - d3 - d3*d3p*d2p*d2*d2p*d2*d3,
                zer],
                [d3p + d3p*d3*d1*d1p*d1*d1p*d3p - d1*d1p*d3p - d1*d1p*d3p*d3*d3p,
                d3p*d3 + d3p*d3*d1*d1p - 1 - d1*d1p*d3p*d3*d3p*d3,
                zer,
                zer,
                1 + d3p*d3*d1*d1p*d1*d1p - d1*d1p - d1*d1p*d3*d3p,
                d3p*d3*d1 + d3p*d3*d1*d1p*d1 - d1 - d1*d1p*d3p*d3*d3p*d3*d1],
                [zer,
                d1p + d1p*d1*d2*d2p*d2*d2p*d1p - d2*d2p*d1p - d2*d2p*d1p*d1*d1p,
                d1p*d1 + d1p*d1*d2*d2p - 1 - d2*d2p*d1p*d1*d1p*d1,
                d1p*d1*d2 + d1p*d1*d2*d2p*d2 - d2 - d2*d2p*d1p*d1*d1p*d1*d2,
                zer,
                1 + d1p*d1*d2*d2p*d2*d2p - d2*d2p - d2*d2p*d1*d1p]])
    else:
        raise ValueError("Unknown TDI generation.")

    # Reshape the matrix to nf x nt x 3 x 6
    tdi_mat_eval = np.swapaxes(tdi_mat.T, tdi_mat.ndim-2, tdi_mat.ndim-1)

    if use_lisagwresponse_convention:
        # If requested, re-order the matrix columns to match the LISA GW Response convention
        tdi_mat_eval = tdi_mat_eval[..., convert]

    return tdi_mat_eval


def compute_aet_tf(fr, tt, t_vect, gen='2.0'):
    """Compute the AET transfer function matrix from eta variables to 
    TDI AET. It's valid for readout (OMS) noises.

    Parameters
    ----------
    fr : ndarray
        frequency array [Hz], size nf
    tt : dict
        dictionary of arm light travel times [s], size nt
    t_vect : ndarray
        time vector where to cumpute the light travel time.
    gen : str, optional
        TDI generation, by default '2.0'.

    Returns
    -------
    tdi_mat_eval
        TDI transfer function matrix for AET, array of size nf x nt x 3 x 6

    """

    tdi_mat_eval = compute_tdi_tf(fr, tt, t_vect, gen=gen)

    if tdi_mat_eval.ndim == 3:
        return utils.multiple_dot(aet_mat[np.newaxis, :, :], tdi_mat_eval)

    return utils.multiple_dot(aet_mat[np.newaxis, np.newaxis, :, :], tdi_mat_eval)


def compute_tdi_tf_tm(fr, tt, t_vect, gen='2.0'):
    """Compute the TDI transfer function matrix from tm noise to TDI.

    Parameters
    ----------
    fr : ndarray
        frequency array [Hz]
    tt : dict
        dictionary of arm light travel times [s]
    t_vect : ndarray
        time vector over which to cumpute the light travel time average.
    gen : str, optional
        TDI generation, by default '2.0'

    Returns
    -------
    tdi_tf_tm : ndarray
        TDI transfer function matrix for XYZ, array of size nf x 3 x 6
    """

    # TDI transfer fonction from eta
    tdi_tf = compute_tdi_tf(fr, tt, t_vect, gen=gen)
    # TDI Transfer function for TM noise
    eta_tm = eta_matrix(fr, tt, t_vect, "TM")
    tdi_tf_tm = 2 * utils.multiple_dot(tdi_tf, eta_tm)

    return tdi_tf_tm


def compute_aet_tf_tm(fr, tt, t_vect, gen='2.0'):
    """Compute the TDI transfer function matrix from tm noise to TDI AET.

    Parameters
    ----------
    fr : ndarray
        frequency array [Hz]
    tt : dict
        dictionary of arm light travel times [s]
    t_vect : ndarray
        time vector over which to cumpute the light travel time average.
    gen : str, optional
        TDI generation, by default '2.0'

    Returns
    -------
    tdi_tf_tm : ndarray
        TDI transfer function matrix for AET, array of size nf x 3 x 6
    """
    tdi_mat_eval = compute_tdi_tf_tm(fr, tt, t_vect, gen=gen)

    if tdi_mat_eval.ndim == 3:
        return utils.multiple_dot(aet_mat[np.newaxis, :, :], tdi_mat_eval)

    return utils.multiple_dot(aet_mat[np.newaxis, np.newaxis, :, :], tdi_mat_eval)


class TDITransferFunction:
    """Class to compute the TDI transfer function in the frequency domain
    """
    def __init__(self, tt, gen='2.0'):
        """
        Initialize class

        Parameters
        ----------
        tt : dict
            dictionary of arm light travel times [s]
        t_vect : ndarray
            time vector over which to cumpute the light travel time average.
        gen : str, optional
            TDI generation, by default '2.0'

        Raises
        ------
        ValueError
            TDI generation can only be 1.5 or 2.0.

        """

        if gen not in ['1.5', '2.0']:
            raise ValueError("Unknown TDI generation.")

        self.tt = tt
        self.gen = gen

    @classmethod
    def from_gw(cls, pt_src, gen='2.0'):
        """Load TDITransferFunction arguments from Strain object

        Parameters
        ----------
        pt_src : lisagwresponse.Strai instance
             source instance from LISA GW Response

        Returns
        -------
        class
            StochasticPointSourceResponse object
        """

        tditf = cls(pt_src.ltt, gen=gen)

        return tditf

    def compute_tf(self, freq, t_0):
        """Compute the TDI transfer function matrix

        Parameters
        ----------
        fr : ndarray
            frequency array [Hz] of size nf
        t_0 : dict
           time at which the light travel time will be computed

        Returns
        -------
        tdi_mat
            TDI transfer function matrix for XYZ, array of size nf x 3 x 6

        """

        return compute_tdi_tf(freq, self.tt, t_0, gen=self.gen)


def eta_matrix(fr, tt, t_vect, noise_type):
    """

    Build matrix that convert single-link measurements to the eta variables,
    to cancel spacraft motion and primed lasers.
    Delay symbols should be ordered as 1, 2, 3, 1p, 2p, 2p


    Parameters
    ----------
    Parameters
    ----------
    fr : ndarray
        frequency array [Hz]
    tt : dict
        dictionary of arm light travel times [s]
    t_vect : ndarray
        time vector over which to cumpute the light travel time average.
    noise_type : string
        Noise source among {"SCI", "TM", "REF"}

    Returns
    -------
    a_eta : ndarray
        transform matrix to eta variables. Size nf x nt x 6 x 6

    """

    if isinstance(t_vect, Iterable):
        fr_arr = np.asarray(fr)[:, np.newaxis]
    else:
        fr_arr = fr

    d23 = delay_operator(fr_arr, tt[23](t_vect)).T
    d31 = delay_operator(fr_arr, tt[31](t_vect)).T
    d12 = delay_operator(fr_arr, tt[12](t_vect)).T
    d32 = delay_operator(fr_arr, tt[32](t_vect)).T
    d13 = delay_operator(fr_arr, tt[13](t_vect)).T
    d21 = delay_operator(fr_arr, tt[21](t_vect)).T

    zer = np.zeros(d23.shape)
    one = np.ones(d23.shape)

    if (noise_type == 'TM') | (noise_type == 'REF'):
        # Transformation to xi variables
        a_xi_eps = 0.5 * np.array([[one, zer, zer, zer, d12, zer],
                                   [zer, one, zer, zer, zer, d23],
                                   [zer, zer, one, d31, zer, zer],
                                   [zer, zer, d13, one, zer, zer],
                                   [d21, zer, zer, zer, one, zer],
                                   [zer, d32, zer, zer, zer, one]], dtype=complex)
    if noise_type == 'REF':
        # TM interferometer contribution to eta
        a_eta_tau = 0.5 * np.array([[zer, -d12, zer, zer, d12, zer],
                                    [zer, zer, -d23, zer, zer, d23],
                                    [-d31, zer, zer, d31, zer, zer],
                                    [one, zer, zer, -one, zer, zer],
                                    [zer, one, zer, zer, -one, zer],
                                    [zer, zer, one, zer, zer, -one]], dtype=complex)

    if noise_type == 'SCI':
        mat = np.array([[one, zer, zer, zer, zer, zer],
                        [zer, one, zer, zer, zer, zer],
                        [zer, zer, one, zer, zer, zer],
                        [zer, zer, zer, one, zer, zer],
                        [zer, zer, zer, zer, one, zer],
                        [zer, zer, zer, zer, zer, one]], dtype=complex)
    elif noise_type == 'TM':
        mat = - a_xi_eps
    elif noise_type == 'REF':
        mat = a_eta_tau + a_xi_eps

    if mat.ndim == 3:
        # Transform matrices from size 6 x 6 x nf to nf x 6 x 6
        return np.swapaxes(mat.T, 1, 2)
    else:
        # Transform matrices from size 6 x 6 x nt x nf to nf x nt x 6 x 6
        return np.swapaxes(mat.T, 2, 3)
