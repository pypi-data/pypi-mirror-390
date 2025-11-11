# -*- coding: utf-8 -*-
# Author: Quentin Baghi 2023 <quentin.baghi@protonmail.com>
"""
Code based on Jean-Baptiste Bayle's LISA Instrument to compute
the analytical instrumental response (PSD).
"""
import numpy as np
from lisaconstants import c

MOSAS = ['12', '23', '31', '13', '32', '21']


class InstrumentModel:
    """Class that construct a model for the instrumental noise. 
    Can be interfaced with LISA Instrument package.
    """

    def __init__(self, oms_isi_carrier_asds=7.9e-12,
                 oms_fknees=0.002,
                 testmass_asds=2.4e-15,
                 testmass_fknees=0.0004,
                 central_freq=281600000000000.0,
                 pprs=None, filter_approx=False, fs=4.0):

        self.central_freq = central_freq

        if isinstance(oms_isi_carrier_asds, float):
            self.oms_isi_carrier_asds = {mosa: oms_isi_carrier_asds
                                         for mosa in MOSAS}
        if isinstance(oms_fknees, float):
            self.oms_fknees = {mosa: oms_fknees 
                               for mosa in MOSAS}
        if isinstance(testmass_asds, float):
            self.testmass_asds = {mosa: testmass_asds
                                  for mosa in MOSAS}
        if isinstance(testmass_fknees, float):
            self.testmass_fknees = {mosa: testmass_fknees
                                    for mosa in MOSAS}

        if pprs is None:
            self.pprs = {
                # Default PPRs based on first samples of Keplerian orbits (v2.0.dev)
                '12': 8.33242295, '23': 8.30282196, '31': 8.33242298,
                '13': 8.33159404, '32': 8.30446786, '21': 8.33159402,
            }

        self.pprs = pprs
        self.filter_approx = filter_approx
        self.fs = fs

    @classmethod
    def from_instru(cls, instru):
        """Load InstrumentModel arguments 
        from Instrument object

        Parameters
        ----------
        instru : lisainstrument.Instrument instance
             instance of LISA Instrument

        Returns
        -------
        class
            InstrumentModel object
        """

        resp = cls(oms_isi_carrier_asds=instru.oms_isi_carrier_asds,
                   oms_fknees=instru.oms_fknees,
                   testmass_asds=instru.testmass_asds,
                   testmass_fknees=instru.testmass_fknees,
                   central_freq=instru.central_freq,
                   pprs=instru.pprs)

        return resp

    def oms_in_isi_carrier(self, freq, mosa='12', ffd=True):
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
        psd_hertz : PDD in Hz / Hz or /Hz

        """
        asd = self.oms_isi_carrier_asds[mosa]
        fknee = self.oms_fknees[mosa]
        if not self.filter_approx:
            psd_meters = asd**2 * (1 + (fknee / freq)**4)
            psd_hertz = (2 * np.pi * freq * self.central_freq / c)**2 * psd_meters
        else:
            psd_highfreq = (asd * self.fs * self.central_freq / c) ** 2 * np.sin(2 * np.pi * freq / self.fs) ** 2
            psd_lowfreq = (2 * np.pi * asd * fknee**2 * self.central_freq / c) ** 2 * freq ** (-2)
            psd_hertz = psd_highfreq + psd_lowfreq
        if ffd:
            return psd_hertz/self.central_freq**2
        return psd_hertz

    def testmass_in_tmi_carrier(self, freq, mosa='12', ffd=True):
        """Model for TM noise PSD in TMI carrier beatnote fluctuations.
        
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
        psd_hertz : PDD in Hz / Hz or /Hz

        """
        asd = self.testmass_asds[mosa]
        fknee = self.testmass_fknees[mosa]
        if not self.filter_approx:
            psd_acc = asd**2 * (1 + (fknee / freq)**2)
            psd_hertz = (2 * self.central_freq / (2 * np.pi * c * freq))**2 * psd_acc
        else:
            # Same for now
            psd_acc = asd**2 * (1 + (fknee / freq)**2)
            psd_hertz = (2 * self.central_freq / (2 * np.pi * c * freq))**2 * psd_acc
            # psd_hertz = (asd * 2 * self.central_freq / (2 * np.pi * c))**2 * (
            #     np.pi / np.sin(np.pi*freq))**2
            # psd_hertz += (asd * fknee * self.central_freq / (np.pi*c))**2 * (
            #     np.pi / np.sin(np.pi*freq))**4

        if ffd:
            # The factor of 4 = 2^2 is to be consistent with backgrounds
            # conventions. The test-mass jitter noise vector is projected two times
            # onto the sensitive axis. The vector nij TM->OB:
            # beam = - 2 / c nij delta_ij
            return psd_hertz / (2*self.central_freq)**2
        return psd_hertz

    def tdi_common(self, freq, mosa='12'):
        """
        TDI common factor.

        Args:
            freq (float): frequencies [Hz]
            instru (Instrument): LISA instrument object
        """
        armlength = np.mean(self.pprs[mosa])

        return 16 * np.sin(2 * np.pi * freq * armlength)**2 \
            * np.sin(4 * np.pi * freq * armlength)**2

    def tdi_tf_oms(self, freq, mosa='12'):
        """TDI transfer function for ISI OMS noise.
        
        Args:
            freq (float): frequencies [Hz]
            instru (Instrument): LISA instrument object
        """
        psd = 4 * self.tdi_common(freq, mosa)
        return np.sqrt(psd)

    def tdi_tf_testmass(self, freq, mosa='12'):
        """TDI transfer function for test mass noise.

        Args:
            freq (float): frequencies [Hz]
            instru (Instrument): LISA instrument object
        """
        armlength = np.mean(self.pprs[mosa])
        psd = self.tdi_common(freq, mosa) * (3 + np.cos(4 * np.pi * freq * armlength))
        return np.sqrt(psd)

    def tdi_psd(self, freq, channel='X', ffd=True):
        """
        TDI PSD with a very simple OMS + TM model

        Parameters
        ----------
        freq : ndarray or float
            Frequencies [Hz] where to compute the PSD

        Returns
        -------
        psd_model : ndarray
            TDI PSD

        """
        testmass = self.tdi_tf_testmass(freq) * np.sqrt(self.testmass_in_tmi_carrier(freq, ffd=False))
        oms = self.tdi_tf_oms(freq) * np.sqrt(self.oms_in_isi_carrier(freq, ffd=False))
        psd_model = np.sqrt(testmass**2 + oms**2)
        if ffd:
            return psd_model / self.central_freq
        return psd_model

