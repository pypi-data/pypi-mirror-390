# -*- coding: utf-8 -*-
# Author: Quentin Baghi 2021 <quentin.baghi@protonmail.com>
import jax
import jax.numpy as jnp
import numpy as np
from scipy import interpolate
from . import utils

@jax.jit
def wishart_loglikelihood(cov_model, cov_sample, dof):
    """
    Pure function to compute the log-wishart likelihood

    Parameters
    ----------
    cov_model : ndarray
        covariance model (scale matrix divided by the number of DOF), size nf x p x p
    cov_sample : ndarray
        sample covariance matrix (or periodogram matrix), size nf x p x p
    dof : int
        number of degrees of freedom

    Returns
    -------
    loglike: float
        likelihood value

    """

    # Compute the inverse and determinant of the covariance
    # cov_xyz_inv, det = utils.sym_matrix_inv(cov_model)
    cov_xyz_inv = jnp.linalg.inv(cov_model)
    det = jnp.linalg.det(cov_model)
    # Compute C^{-1} P for all frequencies (and times)
    epsilon = utils.multiple_dot(cov_xyz_inv, cov_sample)
    # Compute parameter-dependent parts of log-likelihood for all frequencies
    loglike = - jnp.sum(dof * (jnp.trace(epsilon, axis1=1, axis2=2) + jnp.log(det)))

    return jnp.real(loglike)


class TDICovarianceLikelihood:
    """
    Class implementing the Wishart likelihood in the frequency domain
    """

    def __init__(self, freqs, wper, components, k_seg, times=None):
        """
        Gaussian likelihood model the full XYZ Welch spectrum matrix.

        Parameters
        ----------
        freqs : ndarray
            Vector of frequencies
        wper : ndarray
            Periodogram matrix at frequencies `freqs`, size nf x 3 x 3 or nf x nt x 3 x 3
        components : list of signal or noise class instance
            list of classes to compute the TDI PSD components
        k_seg : int
            effective number of degrees of freedom. It can be the number of segments used for the
            Welch averaging if we assume the complex Wishart distribution.
        times : ndarray or None
            vector of time samples for time-frequency analysis. By default, None.

        """

        self.freqs = freqs
        self.times = times
        # If we have a time dimension, let's merge it with frequency.
        if wper.ndim == 4:
            self.nt, self.nf, self.p, _ = np.shape(wper)
            self.wper = np.reshape(wper, (self.nt*self.nf, self.p, self.p))
        else:
            self.nt = 1
            self.nf, self.p, _ = np.shape(wper)
            self.wper = wper
        self.components = components
        # Number of dimensions
        self.p = self.wper.shape[-1]
        # Number of frequency bins
        self.nf = len(freqs)
        # Number of time bins
        if wper.ndim == 4:
            self.nt = wper.shape[1]
            # Flatten the time and frequency dimensions
            self.wper_flat = np.reshape(self.wper, (self.nf*self.nt, self.p, self.p))
            # Number of DoF (repeat for each time bin)
            # self.k_seg = np.tile(k_seg, self.nt)
            self.k_seg = np.asarray([k_seg for i in range(self.nt)])
            self.k_seg = np.reshape(self.k_seg, (self.nf*self.nt))
        elif wper.ndim == 3:
            self.nt = 1
            self.wper_flat = wper
            # Number of DoF
            self.k_seg = k_seg
        else:
            print("Wrong number of spectrum dimensions !")
        # Inverse of periodogram matrix
        _, self.wper_det = utils.sym_matrix_inv(self.wper_flat)
        self.wper_logdet = np.log(self.wper_det)
        # # Compute the inverse and determinant of the periodogram
        # _, ws, _ = np.linalg.svd(self.wper_flat)
        # self.wper_logdet = np.sum(np.log(ws), axis=1)

        # Number of noise parameters to fit
        if not isinstance(self.components, list):
            raise ValueError("components should be a list of noise/signal model instances.")

        # Full dimension of the noise parameter space
        self.ndim = sum([comp.ndim for comp in self.components])
        # Number of covariance components
        self.ncomp = len(self.components)
        # Localise the individual noise parameters in the full noise parameter vector
        self.ib = [0]
        self.ie = [self.components[0].ndim]
        if self.ncomp > 1:
            for i in range(1, self.ncomp):
                self.ib.append(self.ie[i-1])
                self.ie.append(self.ie[i-1] + self.components[i].ndim)

        self.ie_split = self.ie[:-1]
        # Data-dependent constant
        self.const = 0.0
        # self.const = np.sum((self.k_seg - self.p) * self.wper_logdet.real)
        # self.const += np.sum((self.k_seg - self.p) * self.p * np.log(self.k_seg))
        # self.const -= p * (p-1) / 2 * np.log(np.pi)
        # self.const -= np.sum(sum([special.gamma(self.k_seg-j+1) for j in range(1, p+1)]))

    def compute_covariance(self, theta, comp_indices=None, flatten=False):
        """
        Calculate the covariance of TDI XYZ

        Parameters
        ----------
        theta : ndarray
            vector of noise parameters + SGWB parameters.
        comp_indices : list or None
            list of component indices to include in the covariance computation.
            If None, all components are included. Default is None.
        flatten : ndarray
            if True, merges the frequency and time dimensions.
            Default is False.

        Returns
        -------
        cov_xyz : ndarray
            frequency (and time) dependent covariance of size nf x 3 x 3
            or nf x nt x 3 x 3
        """

        if comp_indices is None:
            comp_indices = range(self.ncomp)

        if self.ncomp == 1:
            cov = self.components[0].compute_covariances(theta)
        else:
            # Split parameters into components
            theta_comps = jnp.split(theta, self.ie_split)

            # Stack all covariances and sum
            cov_list = [self.components[i].compute_covariances(theta_comps[i])
                        for i in comp_indices]
            cov = jnp.sum(jnp.stack(cov_list), axis=0)

        if flatten & (self.nt > 1):
            # Concatenate frequency and time dimension in one row
            return jnp.reshape(cov, (self.nf*self.nt, self.p, self.p))

        return cov

    def evaluate(self, theta):
        """
        Calculate the log-likelihood.

        Parameters
        ----------
        theta : ndarray
            vector of noise parameters + SGWB parameters.

        Returns
        -------
        ll : float
            log-likelihood value at x, computed from finds frequencies and possibly times.
        """

        # Compute TDI covariance
        cov_xyz = self.compute_covariance(theta)
        # Evaluate the Wishart log-likelihood
        log_likelihood = wishart_loglikelihood(cov_xyz, self.wper, self.k_seg)

        return log_likelihood + self.const


class TDICovarianceLikelihoodDynamic:

    def __init__(self, freqs, wper, k_seg, cov_models=None, inf=1e14, ftol=1e-2,
                 hypertriangle=False, expmax=200, interpolation_kind='Akima',
                 use_edges=True, whiten=None):
        """
        Gaussian likelihood model the full XYZ Welch spectrum matrix.

        Parameters
        ----------
        freqs : ndarray
            Vector of frequencies
        wper : ndarray
            Welch periodogram matrix at frequencies`freqs`, size nf x 3 x 3
        k_seg : int
            number of segments used for the Welch averaging
        inf : float or np.inf
            if the likelihood diverge, it will be set equal to - inf
        cov_models : dictionary
            A dictionary with the information about the models contributing to the total covariance. This means
            that both noise and signal contributions enter here. The keys of the dictionary are used as the 
            names of each model.
            
            Each entry can contain ndarrays with transfer functions or instrument instance. Those will be used 
            to assess if each particular entry is a shape-agnostic spline model or an analytic one. Keys can 
            also contain analytic models (instrument or signal objects).
            
            Example: cov_models = {'model1': ndarray (nf x 3 x 6), 
                                   'model2': ndarray (nf x 3 x 6), 
                                   'model3': instr_1, 
                                   'model4': instr_2, 
                                   ...
                                   }
              
        signal_models : ndarray or lsit of ndarray objects
            Same as above, but for the signal
        hypertriangle : bool
            if True, the likelihood will operate a transformation on the knot parameters
            such that the transformed parameters are orderered knot locations.
        interpolation_kind: string
            The kind of interpolation to be passed to the interp1d function.
        expmax : float
            maximum value allowed in the exponential function. If this is reached,
            the log-likelihood will return -infinity.
        whiten : dictionary
            A dictionary containing a numerical spectrum for whitening the data. 
        use_edges : bool
            Flag to use a double model for the spline case. The double model includes 
            a model for the tfree knots at the center of the spectrum, plus the non-dynamical
            model of the fixed "edges" amplitudes at the minimum and maximum frequency respectively. 

        """

        self.freqs = freqs
        self.logfr = np.log(freqs)
        self.wper = wper
        self.inf = inf
        self.ftol = ftol
        self.hypertriangle = hypertriangle
        self.expmax = expmax  # Maximum value allowed in the exponential function
        self.kind = interpolation_kind  # Interpolation kind
        self.use_edges = use_edges
        # handle the interpolation kind
        if self.kind.lower() == "akima":
            self.interp_func = lambda x, y : interpolate.Akima1DInterpolator(x, y, axis=-1)(self.logfr)
            
        elif self.kind.lower() in ['linear', 'zero', 'slinear', 'quadratic', 'cubic', 'previous']:
            self.interp_func = lambda x, y : interpolate.interp1d(x, y,
                                                        kind=self.kind, axis=-1, copy=True,
                                                        bounds_error=False,
                                                        fill_value="extrapolate",
                                                        assume_sorted=self.hypertriangle)(self.logfr)
            
        elif self.kind.lower() in ['pchip', 'pchip_interpolate']:
            self.interp_func = lambda x, y : interpolate.pchip_interpolate(x, y, self.logfr)
            
        else:
            raise TypeError("### Error: The likelihood can use only the Akima or the interp1d functions.")
        
        self.noise_models = [] # initialize the number of noise models (splines plus analytic)
        self.signal_models = []
        self._cov_tot = None # Initialize the total covariance matrix (get it for each eval)
        # Loop over the number of transfer functions (or noise components)
        if cov_models is None: raise TypeError("### Error: The noise_models can not be None. Please provide a set of noise models.")
        self.cov_models = cov_models
        self.whiten = whiten
        self.cov_contr = dict()
        self.num_models = len(cov_models.keys())
        # Mark the index where each model parameters start
        self.minds = dict()
        total_param_groups = 0
        for mdl in self.cov_models:
            if isinstance(self.cov_models[mdl], np.ndarray): 
                self.minds[mdl] = [total_param_groups, total_param_groups+2]
                total_param_groups += 2  if self.use_edges else 1 # Can have two groups of parameters (it's a double model: free knots and edges)
            else:
                self.minds[mdl] = [total_param_groups, total_param_groups+1]
                total_param_groups += 1  # Has one group of parameters (single model)

        # Number of segments
        self.k_seg = k_seg
        # Number of dimensions
        self.p = self.wper.shape[2]

        # Inverse of periodogram matrix
        self.wper_inv, self.wper_det = utils.sym_matrix_inv(self.wper)

        # Data-dependent constant
        p = self.wper.shape[2]
        self.const = np.sum((self.k_seg - p) * np.log(np.linalg.det(self.wper)).real)
        self.const += np.sum((self.k_seg - p) * p * np.log(self.k_seg))        
    
    def compute_spline_psd(self, x, groups):
        """Get the spline model for the a given PSD series, given some knots

        Parameters
        ----------
        x, groups : ndarray
            PSD parameters and groups of the dynamical models

        Returns
        -------
        psd, failed : interpolate.interp1d evaluated, list of indices that failed
        """

        x_knots = x[0][:, 0]
        y_knots = x[0][:, 1]
        group_free_knots = groups[0]
        
        # Consider two models. One handling the internal knots, and one for the edges
        if self.use_edges:
            y_knots_edges = x[1] # Get the edges info
            group_edges = groups[1]                    

        num_groups = int(group_free_knots.max() + 1)
        log_psd_model = np.empty((num_groups, len(self.freqs)))
        log_psd_model[:] = np.nan
        failed = {}
        # Loop over the temperatures vs walkers
        for i in range(num_groups):
            inds1 = np.where(group_free_knots == i)
            x_knots_i = x_knots[inds1]
            y_knots_i = y_knots[inds1]

            if self.use_edges:
                inds2 = np.where(group_edges == i)
                y_knots_edges_i = np.squeeze(y_knots_edges[inds2])

            # Remove zeros ### Think about this again!
            x_knots_i = x_knots_i[x_knots_i != 0.]
            y_knots_i = y_knots_i[y_knots_i != 0.]

            if self.hypertriangle:
                # Re-order the knot location parameters by hypertriangulation
                x_knots_i = utils.hypertriangulate(x_knots_i,
                                                    bounds=(self.logfr[0], self.logfr[-1]))
            
            if self.use_edges: # Add the min and max frequency, as well as their knot amplitude
                x_knots_i = np.array([self.logfr[0]] + list(x_knots_i) + [self.logfr[-1]])
                y_knots_i = np.array([y_knots_edges_i[0]] + list(y_knots_i) + [y_knots_edges_i[-1]])

            # Sort them
            sort_ids = np.argsort(x_knots_i)
            x_knots_i = x_knots_i[sort_ids]
            y_knots_i = y_knots_i[sort_ids]

            # Control for knots very close to each other
            if not np.any(np.absolute(np.diff(np.array(x_knots_i))) < self.ftol):
                
                # Change the data and reset the spline class
                log_psd_model[i] = self.interp_func(x_knots_i, y_knots_i)

                # To prevent overflow
                if np.any(log_psd_model[i] > self.expmax):
                    i_over = np.where((log_psd_model[i] > self.expmax) | (
                        np.isnan(log_psd_model[i])))
                    log_psd_model[i][i_over] = np.nan
                    failed[i] = i_over

        return np.exp(log_psd_model)
    
    def compute_covariance(self, x, groups):
        """
        Calculate the covariance of TDI XYZ

        Parameters
        ----------
        x : ndarray
            vector of noise parameters + SGWB parameters.
        groups: ndarray
            vector of groups for the dynamical models.
        Returns
        -------
        cov_xyz : ndarray
            frequency-dependent covariance of size nf x 3 x 3
        """
        niter = 0
        for mdl in self.cov_models:
            if isinstance(self.cov_models[mdl], np.ndarray): # This entry is assumed to be a tdi noise transfer function
                
                spline_psd = self.compute_spline_psd(x[self.minds[mdl][0]:self.minds[mdl][1]], 
                                                     groups[self.minds[mdl][0]:self.minds[mdl][1]])
                
                # If we have chosen to fit the "whitened" spectrum
                if self.whiten is not None and mdl in self.whiten:
                    spline_psd *= self.whiten[mdl]
                    
                self.cov_contr[mdl] = self.cov_models[mdl] * spline_psd[:, :, np.newaxis, np.newaxis]  # The model here is a "tdi_corr" matrix
            else:
                pvals = np.array(x[self.minds[mdl][0]:self.minds[mdl][1]]).squeeze()
                self.cov_contr[mdl] = self.cov_models[mdl]( pvals )   # The model here is an analytic function

            if niter == 0: # I do this in order to avoid initializing (I might have different walkers and temperatures, or even none)
                self._cov_tot = self.cov_contr[mdl].copy() # Add the contribution to the total cov matrix
            else:
                self._cov_tot += self.cov_contr[mdl] # Add the contribution to the total cov matrix
            niter += 1
            
        return self._cov_tot

    def evaluate(self, x, groups):
        """
        Calculate the log-likelihood.

        Parameters
        ----------
        x : ndarray
            vector of noise parameters + SGWB parameters.
        groups: ndarray
            vector of groups for the dynamical models.

        Returns
        -------
        ll : float
            log-likelihood value at x, computed from finds frequencies.
        """

        # Compute TDI covariance
        cov_xyz = self.compute_covariance(x, groups)
        # Initialize the likelihood (N_temps times N_walkers)
        log_likelihood = np.full(cov_xyz.shape[0], - self.inf)
        # Compute the inverse and determinant of the covariance
        for i in range(cov_xyz.shape[0]):
            # Compute the eigendecomposition of the covariance
            cov_xyz_inv, det = utils.sym_matrix_inv(cov_xyz[i])
            # Compute C^{-1} P
            epsilon = utils.multiple_dot(cov_xyz_inv, self.wper)
            # Compute parameter-dependent parts of log-likelihood for all frequencies
            log_likelihood[i] = - np.sum(self.k_seg * (
                np.trace(epsilon, axis1=1, axis2=2) + np.log(det))).real
            # Prevent NaNs
            if np.isnan(log_likelihood[i]):
                log_likelihood[i] = - self.inf
        return log_likelihood + self.const
