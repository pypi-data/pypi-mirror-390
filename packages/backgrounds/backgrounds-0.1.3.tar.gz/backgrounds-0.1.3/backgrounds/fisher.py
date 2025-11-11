# -*- coding: utf-8 -*-
# Author: Quentin Baghi 2025 <quentin.baghi@protonmail.com>
"""Module to compute Fisher information matrices and bias estimates"""
import numpy as np
from . import utils


class FisherMatrix:
    """Class to compute Fisher matrix for Gaussian model covariances and bias esimtates.
    """

    def __init__(self, compute_psd, compute_psd_derivatives):
        """Class constructor.

        Parameters
        ----------
        compute_psd : callable
            covariance function
        compute_psd_derivatives : callable
            derivative of covariance function with respect to parameters
        """


        self.compute_psd = compute_psd
        self.compute_psd_derivatives = compute_psd_derivatives

    def compute_fisher_matrix(self, s_list, nu, params):
        """
        Compute the Fisher information matrix for a Gaussian covariance model

        Parameters
        ----------
        s_list : list
            list of component covariances
        nu : ndarray
            effective number of degrees of freedom
        params : ndarray
            model parameter vector


        Returns
        -------
        ndarray
            fisher_mat
        """

        s_tot = self.compute_psd(s_list, params)
        s_tot_inv = np.linalg.pinv(s_tot)
        ndim = len(s_list)
        dsdtheta = self.compute_psd_derivatives(s_list, params)

        fisher_mat = np.zeros((ndim, ndim), dtype=float)

        for i in range(ndim):
            for j in range(ndim):
                term1 = utils.multiple_dot(s_tot_inv, dsdtheta[i])
                term2 = utils.multiple_dot(s_tot_inv, dsdtheta[j])
                fisher_mat[i, j] = np.sum(nu / 2 * np.trace(
                    utils.multiple_dot(term1, term2), axis1=1, axis2=2)).real
                fisher_mat[j, i] = fisher_mat[i, j]

        return fisher_mat


    def compute_parameter_bias_and_variance(self, s_list, nu, s_bias, params):
        """
        Compute the bias of the parameters based on the spectrum bias.
        """

        # Full PSD
        s_tot = self.compute_psd(s_list, params)
        s_tot_inv = np.linalg.pinv(s_tot)
        normalized_bias = utils.multiple_dot(s_tot_inv, s_bias)
        ndim = len(s_list)
        dsdtheta = self.compute_psd_derivatives(s_list, params)

        fisher_mat = np.zeros((ndim, ndim), dtype=float)
        bias = np.zeros((ndim))

        for i in range(ndim):
            term1 = utils.multiple_dot(s_tot_inv, dsdtheta[i])
            # Fisher matrix
            for j in range(ndim):
                term2 = utils.multiple_dot(s_tot_inv, dsdtheta[j])
                fisher_mat[i, j] = np.sum(nu / 2 * np.trace(
                    utils.multiple_dot(term1, term2), axis1=s_tot.ndim-2, axis2=s_tot.ndim-1)).real
                fisher_mat[j, i] = fisher_mat[i, j]
            # Bias
            bias[i] = np.sum(nu / 2 * np.trace(utils.multiple_dot(term1, normalized_bias),
                                               axis1=s_tot.ndim-2,
                                               axis2=s_tot.ndim-1)).real
        # Invert the Fisher matrix to get the covariance matrix
        cov_mat = np.linalg.inv(fisher_mat)
        # delta theta = I^(-1) * bias
        theta_bias = cov_mat @ bias

        return theta_bias, np.diag(cov_mat)
