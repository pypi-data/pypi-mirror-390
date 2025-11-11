# -*- coding: utf-8 -*-
# Author: Quentin Baghi 2021 <quentin.baghi@protonmail.com>
import numpy as np
from scipy import special, stats
import jax
import jax.numpy as jnp
import warnings


@jax.jit
def log_uniform_pdf(x, a, b):
    """Compute the log-pdf of a log-uniform distribution

    Parameters
    ----------
    x : ndarray
        points where to evaluate the log-pdf
    a : float
        lower bound of the distribution
    b : float
        upper bound of the distribution

    Returns
    -------
    log_pdf : ndarray
        log-pdf evaluated at x

    """

    x = jnp.asarray(x)

    lower = jnp.all(x > a)
    upper = jnp.all(x < b)

    valid = lower & upper

    return jnp.where(valid, 0.0, -jnp.inf)


class LogUniformPrior:
    """Log-uniform prior distribution
    """

    def __init__(self, a, b):
        """
        Instantiate a log-uniform prior distribution.

        Parameters
        ----------
        a : float
            lower bound of the distribution
        b : float
            upper bound of the distribution

        """
        self.a = a
        self.b = b
        if isinstance(a, np.ndarray):
            self.ndim = self.a.size
        elif isinstance(a, list):
            self.ndim = len(a)
        else:
            self.ndim = 1

    def evaluate(self, x):
        """evaluate value of the log-pdf at x

        Parameters
        ----------
        x : ndarray
            points where to evaluate the log-pdf

        Returns
        -------
        log_pdf : ndarray
            log-pdf evaluated at x

        """
        return log_uniform_pdf(x, self.a, self.b)

    def initialize_single_param(self):
        """Initialize one parameter state

        Parameters
        ----------

        Returns
        -------
        p_0 : ndarray
            parameter vector, size ndim
        """

        p_0 = np.random.uniform(low=self.a, high=self.b)

        return np.atleast_1d(p_0)


@jax.jit
def conditional_beta_logpdf(x, alphas, betas, x_min, x_max, delta_min=0):
    """
    Compute the log-pdf of a Beta distribution on [x_min, x_max]

    Parameters
    ----------
    x : ndarray
        points where to evaluate the log-pdf
    a : float
        alpha parameter of the Beta distribution
    b : float
        beta parameter of the Beta distribution
    x_min : float
        minimum of the support
    x_max : float
        maximum of the support
    delta_min : float, optional
        minimum spacing between two knots, by default 0

    Returns
    -------
    log_pdf : ndarray
        log-pdf evaluated at x

    """
    # Convert to jax array if needed
    x_knots = jnp.asarray(x)

    # Check bounds using jax conditionals
    in_bounds = jnp.all(x_min <= x_knots) & jnp.all(x_max >= x_knots)

    # Compute the log-prior value
    x0 = jnp.concatenate([x_min, x_knots[0:-1]])
    x1 = x_knots[:]

    logps = (alphas - 1) * jnp.log(x1 - x0)
    logps -= (alphas + betas - 1) * jnp.log(x_max - x0)
    logps += (betas - 1) * jnp.log(x_max - x1)
    log_prior_value = jnp.sum(logps)

    # Check spacing constraint
    x_knots_full = jnp.concatenate([x_min, jnp.sort(x_knots), x_max])
    spacing_ok = jnp.all(jnp.diff(x_knots_full) >= delta_min)

    # Combine all conditions
    valid = in_bounds & spacing_ok & jnp.isfinite(log_prior_value)

    # Return -inf if invalid, otherwise return log_prior
    return jnp.where(valid, log_prior_value, -jnp.inf)


class KnotLocationPrior:
    """
    Impements only the Beta conditional distribution on
    spline knots locations (without accounting for
    the coefficient values).

    """

    def __init__(self, x_min, x_max, n_knots,
                 delta_min=0, alphas_dirichlet=None):

        self.x_min = jnp.atleast_1d(jnp.asarray(x_min))
        self.x_max = jnp.atleast_1d(jnp.asarray(x_max))
        self.n_knots = n_knots
        self.ndim = n_knots

        if alphas_dirichlet is None:
            self.alphas_dirichlet = 2*jnp.ones(self.n_knots+1)
        else:
            self.alphas_dirichlet = jnp.asarray(alphas_dirichlet)

        # Minimum knot interval
        self.delta_min = delta_min
        # Parameters of the conditional beta distributions
        self.alphas = jnp.ones(self.n_knots) * 2
        self.betas = self.n_knots - jnp.arange(1, self.n_knots+1) + 2

    def evaluate(self, x_knots):
        """evaluate value of the log-prior distribution at x

        Parameters
        ----------
        x_knots : ndarray
            knot locations

        Returns
        -------
        log_prior : float
            value of the log-prior at parameter value x

        """

        return conditional_beta_logpdf(x_knots, self.alphas, self.betas,
                                       self.x_min, self.x_max, self.delta_min)

    def initialize_single_param(self, n_draws=10000):
        """Initialize one parameter state

        Parameters
        ----------

        Returns
        -------
        p_0 : ndarray
            parameter vector, size ndim
        """

        ok = False
        i = 0

        while (not ok) & (i < n_draws):
            # Intialize the knot locations
            deltas = np.random.dirichlet(self.alphas_dirichlet)
            p_0_knot_x_ordered = self.x_min + \
                (self.x_max - self.x_min) * \
                np.cumsum(deltas)[0:self.n_knots]
            # Full vector including exterior knots
            knots_x = np.concatenate(
                [self.x_min, p_0_knot_x_ordered, self.x_max])
            # Knots intervals
            dknots = np.diff(knots_x)
            if np.all(dknots >= self.delta_min):
                ok = True
            else:
                i += 1
        if not ok:
            warnings.warn("Could not find a good starting point.")

        return p_0_knot_x_ordered


class LogPrior:
    """
    Class to agregate several priors.
    """

    def __init__(self, prior_list):
        """Class constructor.

        Parameters
        ----------
        prior_list : list of classes
            list of priors
        """
        # List of priors
        self.prior_list = prior_list
        # Indices of parameter blocks
        self.i1 = [0]
        self.i2 = [self.prior_list[0].ndim]
        for i in range(1, len(prior_list)):
            self.i1.append(self.i2[i-1])
            self.i2.append(self.i2[i-1] + self.prior_list[i].ndim)

    def evaluate(self, x):
        """Evaluate the full log-prior by summing over
        all individual log-priors

        Parameters
        ----------
        x : ndarray
            full parameter vector

        Returns
        -------
        lp : float
            log-prior value at x
        """

        lp = sum([self.prior_list[i].evaluate(x[self.i1[i]:self.i2[i]])
                  for i in range(len(self.prior_list))])
        return lp

    def initialize_single_param(self):

        params = np.concatenate([p.initialize_single_param()
                                 for p in self.prior_list])

        return params


class Uniform:

    def __init__(self, x_min, x_max):
        """
        Instantiate a Uniform distribution.

        Parameters
        ----------
        x_min : ndarray
            lower bound
        x_max : ndarray
            upper bound
        """

        self.x_min = np.atleast_1d(x_min)
        self.x_max = np.atleast_1d(x_max)
        self.ndim = x_max.size
        self.constant = - np.sum(np.log(self.x_max - self.x_min))

    def evaluate(self, x):
        """evaluate value of the log-pdf at x

        Parameters
        ----------
        x : ndarray
            paramaters vector

        Returns
        -------
        log_prior : float
            value of the log-pdf at parameter value x

        """
        if np.any(x < self.x_min) | np.any(x > self.x_max):
            return -np.inf

        return self.constant

    def initialize_single_param(self):
        """Initialize one parameter state

        Parameters
        ----------

        Returns
        -------
        p_0 : ndarray
            parameter vector, size ndim
        """

        return np.random.uniform(self.x_min, self.x_max)


class Gaussian:

    def __init__(self, mean, covariance):
        """
        Instantiate a Gaussian prior distribution.

        Parameters
        ----------
        mean : ndarray
            parameters means
        covariance : ndarray
            parameters covariance

        """

        self.mean = mean
        self.covariance = covariance
        self.cov_inv = np.linalg.inv(covariance)
        self.l_mat = np.linalg.cholesky(covariance)
        self.ndim = mean.size

    def evaluate(self, x):
        """evaluate value of the log-prior distribution at x

        Parameters
        ----------
        x : ndarray
            paramaters vector

        Returns
        -------
        log_prior : float
            value of the log-prior at parameter value x

        """
        epsilon = x - self.mean
        cov_inv_eps = self.cov_inv.dot(epsilon)

        return -0.5 * np.sum(epsilon.conj() * cov_inv_eps)

    def initialize_single_param(self):
        """Initialize one parameter state

        Parameters
        ----------

        Returns
        -------
        p_0 : ndarray
            parameter vector, size ndim
        """

        u_vect = np.random.normal(0, 1, size=self.mean.size)

        return self.mean + self.l_mat.dot(u_vect)


class AsymmetricGaussian:

    def __init__(self, loc=0.0, scale=1.0, shape=1.0):
        """
        Instantiate an asymetric Generalized Gaussian 
        distribution

        Parameters
        ----------
        loc : ndarray or float
            parameters means, size q
        scale : ndarray or float
            parameters standard deviations
        shape : ndarray or float
            parameter distribution shape coefficients

        """

        self.loc = loc
        self.scale = scale
        self.a = shape
        if type(loc) == np.ndarray:
            self.ndim = loc.size
        else:
            self.ndim = 1

        # self.rv = stats.skewnorm(shape, loc, scale)
        self.phi = stats.norm()

        # Determine the support of the distribution
        if self.a > 0:
            self.x_min = - np.inf
            self.x_max = self.loc + self.scale / self.a
        elif self.a == 0:
            self.x_min = - np.inf
            self.x_max = np.inf
        else:
            self.x_min = self.loc + self.scale / self.a
            self.x_max = np.inf

    def log_phi(self, x):

        return - 0.5 * (np.log(2 * np.pi) + x**2)

    def variable_transform(self, x):

        u = (x - self.loc)/self.scale

        if self.a == 0:
            y = u
        else:
            y = - np.log(1 - self.a * u) / self.a

        return y, u

    def inverse_variable_transform(self, y):

        u = (1 - np.exp(-self.a * y)) / self.a
        x = self.loc + self.scale * u

        return x

    def logpdf(self, x):
        """evaluate value of the individual log-pdf of 
        the elements of x

        Parameters
        ----------
        x : ndarray
            paramaters vector

        Returns
        -------
        log_prior : ndarray
            value of the log-prior at each elements of x

        """
        y, u = self.variable_transform(x)
        # Compute the individual log-pdf for each parameter
        log_pdfs = self.log_phi(y) - np.log(self.scale*(1 - self.a * u))

        return log_pdfs

    def evaluate(self, x):
        """evaluate value of the log-prior distribution at x

        Parameters
        ----------
        x : ndarray
            paramaters vector

        Returns
        -------
        log_prior : float
            value of the log-prior at parameter value x

        """
        # Check if x belongs to the support
        if np.any(x < self.x_min) | np.any(x > self.x_max):
            return -np.inf
        # Compute the individual log-pdf for each parameter
        log_pdfs = self.logpdf(x)
        # Sum over all PDFs to get the joint prior
        # Convert NaNs to -infinity
        if np.any(np.isnan(log_pdfs)):
            return -np.inf
        return np.sum(log_pdfs)

    def pdf(self, x):
        """evaluate value of the prior distribution at x

        Parameters
        ----------
        x : ndarray
            paramaters vector

        Returns
        -------
        prior : float
            value of the prior at parameter value x
        """

        y, u = self.variable_transform(x)

        return self.phi.pdf(y) / (self.scale*(1 - self.a * u))

    def cdf(self, x):

        y, _ = self.variable_transform(x)

        return self.phi.cdf(y)

    def ppf(self, p):

        y = self.phi.ppf(p)
        x = self.inverse_variable_transform(y)

        return x

    def initialize_single_param(self, n_draws=1000):
        """Initialize one parameter state

        Parameters
        ----------

        Returns
        -------
        p_0 : ndarray
            parameter vector, size ndim
        """

        u_vect = np.random.uniform(0, 1, size=self.ndim)

        return self.ppf(u_vect)


class BetaAGGLogPrior(AsymmetricGaussian):
    """
    Class implementing the prior distribution on the beta parameter 
    so that y = f(beta) follows an asymmetric generalized Gaussian distribution.
    The function f is some linear (or nonlinear) function of beta.
    """

    def __init__(self, noise_comps, y_ref, scale=1.0, shape=1.0, 
                 delta_min=0, alphas_dirichlet=None):
        """
        Instantitiate an instance of BetaAGGLogPrior.

        Parameters
        ----------
        noise_comps : list
            List of noise.SplineNoiseModel objects describing the
            noise components.
        y_ref : int
            Baseline PSD that will determine the mode of the distribution.
        scale : float, optional
            scale parameter of the AGG distribution, by default 1.0
        shape : float, optional
            shape parameter of the AGG distribution, by default 1.0
        """

        # Noise classes
        self.noise_comps = noise_comps
        self.n_noises = len(noise_comps)
        self.nbins = self.noise_comps[0].tdi_corr.shape[0]
        self.transforms = [nc.tdi_corr for nc in self.noise_comps]

        # For knot locations
        # ------------------
        self.log_f_min = np.min(self.noise_comps[0].logfreq)
        self.log_f_max = np.max(self.noise_comps[0].logfreq)
        self.n_knots = self.noise_comps[0].n_coeffs - 2
        self.delta_min = delta_min
        # Parameters of the conditional beta distributions
        self.alphas = np.ones(self.n_knots) * 2
        self.betas = self.n_knots - np.arange(1, self.n_knots+1) + 2

        if alphas_dirichlet is None:
            self.alphas_dirichlet = 2*np.ones(self.n_knots+1)
        else:
            self.alphas_dirichlet = alphas_dirichlet

        # Form the linear system to solve
        mat_vect = np.zeros((self.nbins, 2, 2), dtype=complex)
        mat_vect[:, 0, 0] = self.transforms[0][:, 0, 0]
        mat_vect[:, 0, 1] = self.transforms[1][:, 0, 0]
        mat_vect[:, 1, 0] = self.transforms[0][:, 0, 1]
        mat_vect[:, 1, 1] = self.transforms[1][:, 0, 1]
        self.mat_vect = mat_vect

        # Design matrix
        self.x_mat = []
         # LS estimator for S_OMS and S_TM
        self.projectors = []
        self.compute_projectors()

        # Reference PSD
        self.y_ref = y_ref
        # Size of the PSD space
        self.ndim_y = self.y_ref.size
        # Number of frequency bins
        self.n_c = int(self.ndim_y / 2)
        y_mode_xx = np.log(self.y_ref[0:self.n_c].real)
        y_mode_xy = np.log(np.abs(self.y_ref[self.n_c:]))
        # Corresponding location parameter for the AGG distribution
        loc_xx = y_mode_xx - scale / shape * (1 - np.exp(-shape**2))
        loc_xy = y_mode_xy - scale / shape * (1 - np.exp(-shape**2))
        loc = np.concatenate([loc_xx, loc_xy])

        AsymmetricGaussian.__init__(self, loc=loc, scale=scale, shape=shape)

        # Total number of dimensions
        self.ndim = sum([comp.ndim for comp in self.noise_comps])

    def compute_projectors(self, intknots=None):

        if intknots is None:
            intknots = [self.noise_comps[i].logf_knots[1:-1]
                        for i in range(self.n_noises)]
        # Design matrix
        self.x_mat = [self.noise_comps[0].compute_design_matrix(intknots[i])
                      for i in range(self.n_noises)]
        # LS estimator
        self.projectors = [np.linalg.pinv(
            np.dot(self.x_mat[i].T, self.x_mat[i])).dot(self.x_mat[i].T)
                           for i in range(self.n_noises)]

    def forward_map(self, x):
        """
        Map function
        y = f(x)

        Parameters
        ----------
        theta_noise : ndarray
            vector of spline coefficients

        Returns
        -------
        y : ndarray
            vector of corresponding [S_xx, S_xy]

        """
        # Number of spline parameters per noise component
        ndim_1 = int(x.size / len(self.noise_comps))
        # Compute log(S_OMS) and log(S_TM)
        log_psds = [self.noise_comps[i].compute_link_logpsd(x[i*ndim_1:(i+1)*ndim_1])
                    for i in range(len(self.noise_comps))]
        # Compute the corresponding TDI noise responses
        tdi_out = [self.transforms[i] * np.exp(log_psds[i][:, np.newaxis, np.newaxis])
                   for i in range(len(self.noise_comps))]
        # Compute the total TDI response
        cov_xyz = sum(tdi_out)
        # Return the covariance log S_xx, |log S_xy|
        return np.concatenate([cov_xyz[:, 0, 0], cov_xyz[:, 0, 1]])

    def inverse_map(self, y, output_link_psds=False, intknots=None):
        """
        Pseudo-inverse function x = f^{-1}(y)

        Parameters
        ----------
        y : ndarray
            vector [S_xx, S_xy]
        intknots : list of arrays, default is None
            list of interior knots for each noise spline

        Returns
        -------
        theta_noise : ndarray
            vector of corresponding spline coefficients

        """

        # Form the vector b = [Sxx, Sxy]
        b_vect = np.asarray([y[:self.nbins], y[self.nbins:]]).T
        # Solve for S_OMS and S_TM
        s_vect = np.linalg.solve(self.mat_vect, b_vect)
        # Compute the log(S_OMS) and log(S_TM)
        log_s_vect = np.log(s_vect)
        # Construct LS estimator
        if intknots is None:
            self.compute_projectors(intknots=intknots)
        # Estimate parameters using least squares
        spline_coeffs = [self.projectors[i].dot(log_s_vect[:, i])
                         for i in range(self.n_noises)]
        # theta_n = projector_c.dot(log_s_vect)
        if not output_link_psds:
            return np.concatenate(spline_coeffs)

        return s_vect, np.concatenate(spline_coeffs)

    def logp_x_knots(self, x_knots):
        """evaluate value of the log-prior distribution
        at the knot locations x_knots

        Parameters
        ----------
        x_knots : ndarray
            knot locations

        Returns
        -------
        log_prior : float
            value of the log-prior probability at knot locations x

        """

        # First of all, verify that all parameters are within bounds
        if (np.all(self.log_f_min <= x_knots)) & (np.all(self.log_f_max >= x_knots)):
            # Select control point locations, and sort them (should we?)
            # x_knots = x[self.n_coeffs:self.n_coeffs+self.n_knots]
            # Compute the log-prior value
            x0 = np.concatenate([[self.log_f_min], x_knots[0:-1]])
            x1 = x_knots[:]
            # For a given knot, the next one is more likely to be rather close than
            # very far away in frequency
            logps = - np.log(special.beta(self.alphas, self.betas))
            logps = (self.alphas-1) * np.log(x1 - x0)
            logps -= (self.alphas + self.betas - 1) * \
                np.log(self.log_f_max - x0)
            logps += (self.betas - 1) * np.log(self.log_f_max - x1)
            log_prior = np.sum(logps)
        else:
            print("not in the allowed range")
            return -np.inf
        # Apply constraint on the distance between knots
        x_knots_full = np.concatenate(
            [[self.log_f_min], np.sort(x_knots), [self.log_f_max]])
        if np.any(np.diff(x_knots_full) < self.delta_min):
            # print("Knots not sufficiently spaced")
            return -np.inf
        # Check that log-prior is not NaN
        if np.isnan(log_prior):
            return -np.inf
        return log_prior

    def evaluate(self, x):
        """
        Evaluate the value of the full log-prior at 
        parameter x.
        
        Parameters
        ----------
        x : ndarray
            spline parameters

        Returns
        -------
        log_prior : float
            value of the log-prior probability at spline parameters x
        
        """

        logp_x_knots = 0
        # Compute the log-prior probability of having
        # such knot locations (if they are free)
        if not self.noise_comps[0].fixed_knots:
            # List of knot location parameters or each noise component
            x_list = [x[i*self.noise_comps[i].ndim+self.noise_comps[i].n_coeffs:
                        (i+1)*self.noise_comps[i].ndim] for i in range(self.n_noises)]
            logp_x_knots = sum([self.logp_x_knots(x_) for x_ in x_list])
                    
        # If the log prior for the knot location is -inf, then
        # no need to compute the prior for knot amplitudes
        if not np.isfinite(logp_x_knots):
            return -np.inf
        # Compute the equivalent spectrum s_xx, s_xy
        y = self.forward_map(x)
        log_y = np.log(np.abs(y))        
        # Compute the log-prior probability of having 
        # such a value for spline coefficients
        log_pdfs = self.logpdf(log_y)
        # If there are NaNs or infinite values, return -infinity
        if (np.any(np.isnan(log_pdfs))) | (not np.isfinite(log_pdfs)):
            return -np.inf
        # Else return a real value
        return np.sum(log_pdfs) + logp_x_knots

    def draw_knot_locations(self, n_tries=1000):
        """
        Draw knot locations in log-frequency space.
        It is not a proper draw from the prior, but
        rather a way to initialize the knot paramters
        in a way compatible with the prior.
        
        Parameters
        ----------

        Returns
        -------
        p_0_knot_x_ordered : ndarray
            knots location parameter
        """

        ok = False
        i = 0

        while (not ok) & (i < n_tries):
            # Intialize the knot locations
            deltas = np.random.dirichlet(self.alphas_dirichlet)
            p_0_knot_x_ordered = self.log_f_min + \
                (self.log_f_max - self.log_f_min) * \
                np.cumsum(deltas)[0:self.n_knots]
            # Full vector including exterior knots
            knots_x = np.concatenate(
                [[self.log_f_min], p_0_knot_x_ordered, [self.log_f_max]])
            # Knots intervals
            dknots = np.diff(knots_x)
            if np.all(dknots >= self.delta_min):
                ok = True
            else:
                i += 1
        if not ok:
            warnings.warn("Could not find a good starting point.")

        return p_0_knot_x_ordered

    def knot_coeffs_and_locations_to_params(self, beta, intknots=None):
        # Re-ortder the output if necessary
        if intknots is not None:
            n_coeffs = [nc for nc in self.noise_comps.n_coeffs]
            params = np.concatenate([beta[0:n_coeffs[0]], intknots[0],
                                     beta[n_coeffs[0]:], intknots[1]]).real
        else:
            params = beta.real

        return params

    def initialize_single_param(self, n_draws=1000):
        """
        Generate random number that approximately follow
        the required distirbution.
        """
        ok_flag = False
        i = 0

        while (not ok_flag) & (i < n_draws):
            # Draw number between 0 and 1
            u_vect = np.random.uniform(0, 1) * np.ones(self.ndim_y)
            # Compute inverse CDF for log [S_xx, |S_xy|]
            log_y = self.ppf(u_vect)
            # Remove the mean and perturb the baseline
            y = self.y_ref * np.exp(log_y - self.loc)
            # If necessary, draw knot locations
            if not self.noise_comps[0].fixed_knots:
                intknots = [self.draw_knot_locations(n_tries=n_draws)
                            for i in range(self.n_noises)]
            else:
                intknots = None
            # Compute the equivalent regression parameter
            beta = self.inverse_map(y, intknots=intknots)
            params = self.knot_coeffs_and_locations_to_params(
                beta, intknots=intknots)

            # Evaluate the logprior at this point
            logp = self.evaluate(params)
            if np.isfinite(logp):
                ok_flag = True
            i += 1

        if not ok_flag:
            warnings.warn("Could not find a good starting point.")

        return params


class PriorMap:
    """
    Class that defines a map from the model parameter to some other quantity y_ref on which 
    we apply a prior constraint.
    """

    def __init__(self, noise_comps):
        """
        PriorMap constructor

        Parameters
        ----------
        noise_comps : list
            list of noise classes
        """

        self.noise_comps = noise_comps
        self.n_noises = len(noise_comps)
        self.nbins = self.noise_comps[0].tdi_corr.shape[0]

        # Localise the individual noise parameters in the full parameter vector
        self.ib = [0] # Start from the beginning of the vector
        self.ie = [self.noise_comps[0].ndim] # Until the dimension of the first noise model
        for i in range(1, self.n_noises): # Then for each additional component
            # Start from where we were at the last iteration
            self.ib.append(self.ie[i-1])
            # Add the dimension of the new noise model
            self.ie.append(self.ie[i-1] + self.noise_comps[i].ndim)


    def forward_map(self, x):
        """
        Compute y_ref map from the model parameters x

        Parameters
        ----------
        x : ndarray
            noise model parameters

        Returns
        -------
        y_ref : ndarray
            reference quantity depending on x
        """

        return x

    def inverse_map(self, y):
        """
        Pseudo-inverse function x = f^{-1}(y)

        Parameters
        ----------
        y : ndarray
            reference vector

        Returns
        -------
        x : ndarray
            vector of corresponding noise coefficients

        """

        return y


class SingleLinkPriorMap(PriorMap):
    """
    Prior map on single-link noise power spectral densities
    """

    def __init__(self, noise_comps):
        """
        SingleLinkPriorMap constructor

        Parameters
        ----------
        noise_comps : list
            list of noise classes
        """
        super().__init__(noise_comps)

        self.transforms = [nc.tdi_corr for nc in self.noise_comps]
        # Design matrix
        self.x_mat = []
         # LS estimator for S_OMS and S_TM
        self.projectors = []
        self.compute_projectors()

    def compute_projectors(self, intknots=None):
        """
        Compute least-square projectors to fit the noise parameters from y_ref

        Parameters
        ----------
        intknots : _type_, optional
            interior knots, by default None
        """

        if intknots is None:
            intknots = [self.noise_comps[i].logf_knots[1:-1]
                        for i in range(self.n_noises)]
        # Design matrix
        self.x_mat = [self.noise_comps[i].compute_design_matrix(intknots[i])
                      for i in range(self.n_noises)]
        # LS estimator
        self.projectors = [np.linalg.pinv(
            np.dot(self.x_mat[i].T, self.x_mat[i])).dot(self.x_mat[i].T)
                           for i in range(self.n_noises)]

    def forward_map(self, x):
        """
        Map function
        y = f(x)

        Parameters
        ----------
        theta_noise : ndarray
            vector of spline coefficients

        Returns
        -------
        y : ndarray
            vector of corresponding [S_oms, S_tm]

        """
        # Compute S_OMS and S_TM
        psds = [self.noise_comps[i].compute_link_psd(x[self.ib[i]:self.ie[i]])
                for i in range(len(self.noise_comps))]

        return np.concatenate(psds)

    def inverse_map(self, y, output_link_psds=False, basis_args=None):
        """
        Pseudo-inverse function x = f^{-1}(y)

        Parameters
        ----------
        y : ndarray
            vector [S_oms, S_tm]
        intknots : list of arrays, default is None
            list of interior knots for each noise spline

        Returns
        -------
        theta_noise : ndarray
            vector of corresponding noise coefficients

        """

        # Construct LS estimator
        if basis_args is None:
            self.compute_projectors(basis_args)
        # Form the vector log_y_vect = [log S_oms, log S_tm]
        log_y_vect = np.log(np.asarray([y[:self.nbins], y[self.nbins:]]).T)
        # Estimate parameters using least squares
        spline_coeffs = [self.projectors[i].dot(log_y_vect[:, i])
                         for i in range(self.n_noises)]
        # theta_n = projector_c.dot(log_s_vect)
        if not output_link_psds:
            return np.concatenate(spline_coeffs)

        return y, np.concatenate(spline_coeffs)


class TDIPriorMap(PriorMap):
    """
    Prior map on TDI power spectral densities
    """

    def __init__(self, noise_comps):
        """
        TDIPriorMap constructor

        Parameters
        ----------
        noise_comps : list
            list of noise classes
        """
        super().__init__(noise_comps)

        self.transforms = [nc.tdi_corr for nc in self.noise_comps]

        # Form the linear system to solve
        mat_vect = np.zeros((self.nbins, 2, 2), dtype=complex)
        mat_vect[:, 0, 0] = self.transforms[0][:, 0, 0]
        mat_vect[:, 0, 1] = self.transforms[1][:, 0, 0]
        mat_vect[:, 1, 0] = self.transforms[0][:, 0, 1]
        mat_vect[:, 1, 1] = self.transforms[1][:, 0, 1]
        self.mat_vect = mat_vect

        # Design matrix
        self.x_mat = []
         # LS estimator for S_OMS and S_TM
        self.projectors = []
        self.compute_projectors()

    def compute_projectors(self, basis_args=None):
        """
        Compute least-square projectors to fit the noise parameters from y_ref

        Parameters
        ----------
        basis_args : list, optional
            argument to construct a new noise basis, like interior knots, by default None
        """

        # Design matrix
        if basis_args is None:
            self.x_mat = [self.noise_comps[i].x_mat for i in range(self.n_noises)]
        else:
            self.x_mat = [self.noise_comps[i].compute_design_matrix(basis_args=basis_args[i])
                          for i in range(self.n_noises)]
        # LS estimator
        self.projectors = [np.linalg.pinv(
            np.dot(self.x_mat[i].T, self.x_mat[i])).dot(self.x_mat[i].T)
                           for i in range(self.n_noises)]

    def forward_map(self, x):
        """
        Map function
        y = f(x)

        Parameters
        ----------
        theta_noise : ndarray
            vector of spline coefficients

        Returns
        -------
        y : ndarray
            vector of corresponding [S_xx, S_xy]

        """
        # Compute S_OMS and S_TM
        psds = [self.noise_comps[i].compute_link_psd(x[self.ib[i]:self.ie[i]])
                for i in range(len(self.noise_comps))]
        # Compute the corresponding TDI noise responses
        tdi_out = [self.transforms[i] * psds[i][:, np.newaxis, np.newaxis]
                   for i in range(len(self.noise_comps))]
        # Compute the total TDI response
        cov_xyz = sum(tdi_out)
        # Return the covariance log S_xx, |log S_xy|
        return np.concatenate([cov_xyz[:, 0, 0], cov_xyz[:, 0, 1]])

    def inverse_map(self, y, output_link_psds=False, basis_args=None):
        """
        Pseudo-inverse function x = f^{-1}(y)

        Parameters
        ----------
        y : ndarray
            vector [S_xx, S_xy]
        basis_args : list of arrays, default is None
            Arguments to construct the design matrix, like a list 
            of interior knots for each noise spline. If provided,
            it recomputes the design matrix.

        Returns
        -------
        theta_noise : ndarray
            vector of corresponding noise coefficients

        """

        # Form the vector b = [Sxx, Sxy]
        b_vect = np.asarray([y[:self.nbins], y[self.nbins:]]).T
        # Solve for S_OMS and S_TM
        s_vect = np.linalg.solve(self.mat_vect, b_vect)
        # Compute the log(S_OMS) and log(S_TM)
        log_s_vect = np.log(s_vect)
        # Construct LS estimator if the design matrix changes
        if basis_args is not None:
            self.compute_projectors(basis_args=basis_args)
        # Estimate parameters using least squares
        spline_coeffs = [self.projectors[i].dot(log_s_vect[:, i])
                         for i in range(self.n_noises)]
        if not output_link_psds:
            return np.concatenate(spline_coeffs)

        return s_vect, np.concatenate(spline_coeffs)


class SplinePrior:
    """
    Class implementing the prior distribution on the beta parameter 
    so that y = f(beta) follows a uniform distribution.
    The function f is some linear (or nonlinear) function of beta.
    """

    def __init__(self, noise_comps, y_ref,
                 scale_low=0.1,
                 scale_up=10.0,
                 delta_min=0,
                 alphas_dirichlet=None,
                 mapping=None):
        """
        Instantitiate an instance of BetaAGGLogPrior.

        Parameters
        ----------
        noise_comps : list
            List of noise.SplineNoiseModel objects describing the
            noise components.
        y_ref : int
            Baseline PSD that will determine the center of the distribution.
        scale_low : float, optional
            factor multiplying y_ref to get the lower bound, by default 0.1
        scale_up : float, optional
            factor multiplying y_ref to get the upper bound, by default 10.0
        delta_min : float
            minimum separation to impose betweem knots, in log-frequency
        alpha_dirichlet : ndarray
            parameters for the Dirichlet distribution to initialize the knot
            locations
        mapping : PriorMap instance
            map from parameter space to y_ref
        """

        # Parameter mapping
        if mapping is None:
            self.mapping = TDIPriorMap(noise_comps)
        elif isinstance(mapping, str):
            if mapping == "tdi":
                self.mapping = TDIPriorMap(noise_comps)
            elif mapping == "links":
                self.mapping = SingleLinkPriorMap(noise_comps)

        # Noise classes
        self.noise_comps = noise_comps
        self.n_noises = len(noise_comps)

        # For knot locations
        self.log_f_min = np.min(self.noise_comps[0].logfreq)
        self.log_f_max = np.max(self.noise_comps[0].logfreq)
        self.n_knots = self.noise_comps[0].n_coeffs - 2
        self.delta_min = delta_min
        # Parameters of the conditional beta distributions
        self.alphas = np.ones(self.n_knots) * 2
        self.betas = self.n_knots - np.arange(1, self.n_knots+1) + 2

        if alphas_dirichlet is None:
            self.alphas_dirichlet = 2*np.ones(self.n_knots+1)
        else:
            self.alphas_dirichlet = alphas_dirichlet

        # Reference PSD
        self.y_ref = y_ref

        # Bounds
        self.scale_up = scale_up
        self.scale_low = scale_low
        self.log_y_up = np.log(np.abs(y_ref)) + np.log(scale_up)
        self.log_y_low = np.log(np.abs(y_ref)) + np.log(scale_low)
        # Size of the PSD space
        self.ndim_y = self.y_ref.size
        # Number of frequency bins
        self.n_c = int(self.ndim_y / 2)

        # Total number of dimensions
        self.ndim = sum(comp.ndim for comp in self.noise_comps)

        if hasattr(self.noise_comps[0], 'fixed_knots'):
            self.fixed_basis = self.noise_comps[0].fixed_knots
        elif hasattr(self.noise_comps[0], 'fixed_basis'):
            self.fixed_basis = self.noise_comps[0].fixed_basis

    def logp_x_knots(self, x_knots):
        """evaluate value of the log-prior distribution
        at the knot locations x_knots

        Parameters
        ----------
        x_knots : ndarray
            knot locations

        Returns
        -------
        log_prior : float
            value of the log-prior probability at knot locations x

        """

        # First of all, verify that all parameters are within bounds
        if (np.all(self.log_f_min <= x_knots)) & (np.all(self.log_f_max >= x_knots)):
            # Select control point locations, and sort them (should we?)
            # x_knots = x[self.n_coeffs:self.n_coeffs+self.n_knots]
            # Compute the log-prior value
            x0 = np.concatenate([[self.log_f_min], x_knots[0:-1]])
            x1 = x_knots[:]
            # For a given knot, the next one is more likely to be rather close than
            # very far away in frequency
            logps = - np.log(special.beta(self.alphas, self.betas))
            logps = (self.alphas-1) * np.log(x1 - x0)
            logps -= (self.alphas + self.betas - 1) * \
                np.log(self.log_f_max - x0)
            logps += (self.betas - 1) * np.log(self.log_f_max - x1)
            log_prior = np.sum(logps)
        else:
            # print("not in the allowed range")
            return -np.inf
        # Apply constraint on the distance between knots
        x_knots_full = np.concatenate(
            [[self.log_f_min], np.sort(x_knots), [self.log_f_max]])
        if np.any(np.diff(x_knots_full) < self.delta_min):
            # print("Knots not sufficiently spaced")
            return -np.inf
        # Check that log-prior is not NaN
        if np.isnan(log_prior):
            return -np.inf
        return log_prior

    def evaluate(self, x):
        """
        Evaluate the value of the full log-prior at 
        parameter x.
        
        Parameters
        ----------
        x : ndarray
            spline parameters

        Returns
        -------
        log_prior : float
            value of the log-prior probability at spline parameters x
        
        """

        logp_x_knots = 0
        # Compute the log-prior probability of having
        # such knot locations (if they are free)
        if not self.fixed_basis:
            # List of knot location parameters or each noise component
            x_list = [x[i*self.noise_comps[i].ndim+self.noise_comps[i].n_coeffs:
                        (i+1)*self.noise_comps[i].ndim] for i in range(self.n_noises)]
            logp_x_knots = sum(self.logp_x_knots(x_) for x_ in x_list)

        # If the log prior for the knot location is -inf, then
        # no need to compute the prior for knot amplitudes
        if not np.isfinite(logp_x_knots):
            return -np.inf
        # Compute the equivalent spectrum s_xx, s_xy (or s_oms, s_tm)
        y = self.mapping.forward_map(x)
        log_y = np.log(np.abs(y))
        # Verify that the spectra are within bounds
        logp_y_knots = self.log_pdf(log_y)

        if np.isnan(logp_y_knots):
            return -np.inf

        return logp_x_knots + logp_y_knots

    def draw_knot_locations(self, n_tries=1000):
        """
        Draw knot locations in log-frequency space.
        It is not a proper draw from the prior, but
        rather a way to initialize the knot paramters
        in a way compatible with the prior.
        
        Parameters
        ----------

        Returns
        -------
        p_0_knot_x_ordered : ndarray
            knots location parameter
        """

        ok = False
        i = 0

        while (not ok) & (i < n_tries):
            # Intialize the knot locations
            deltas = np.random.dirichlet(self.alphas_dirichlet)
            p_0_knot_x_ordered = self.log_f_min + \
                (self.log_f_max - self.log_f_min) * \
                np.cumsum(deltas)[0:self.n_knots]
            # Full vector including exterior knots
            knots_x = np.concatenate(
                [[self.log_f_min], p_0_knot_x_ordered, [self.log_f_max]])
            # Knots intervals
            dknots = np.diff(knots_x)
            if np.all(dknots >= self.delta_min):
                ok = True
            else:
                i += 1
        if not ok:
            warnings.warn("Could not find a good starting point.")

        return p_0_knot_x_ordered

    @staticmethod
    def arange_parameters(beta, intknots=None):
        """
        For book-keeping: append knot locations parameters to
        coefficients in the right ordering.

        Parameters
        ----------
        beta : ndarray
            vector of knot coefficients
        intknots : list, optional
            list of vectors of knot locations, by default None

        Returns
        -------
        params : ndarray
            full noise parameter
        """
        # Re-ortder the output if necessary
        if intknots is not None:
            n_coeffs = int(beta.size/2)
            params = np.concatenate([beta[0:n_coeffs], intknots[0],
                                     beta[n_coeffs:], intknots[1]]).real
        else:
            params = beta.real

        return params

    def initialize_single_param(self, n_draws=1000):
        """
        Generate random number that approximately follow
        the required distirbution.
        """
        ok_flag = False
        i = 0

        while (not ok_flag) & (i < n_draws):
            # Perturb the baseline
            log_y = self.draw()
            # y = self.y_ref * np.random.uniform(self.scale_low, self.scale_up)
            # If necessary, draw knot locations
            if not self.fixed_basis:
                intknots = [self.draw_knot_locations(n_tries=n_draws)
                            for i in range(self.n_noises)]
            else:
                intknots = None
            # Compute the equivalent regression parameter
            beta = self.mapping.inverse_map(np.exp(log_y), basis_args=intknots)
            params = self.arange_parameters(
                beta, intknots=intknots)

            # Evaluate the logprior at this point
            logp = self.evaluate(params)
            if np.isfinite(logp):
                ok_flag = True
            i += 1

        if not ok_flag:
            warnings.warn("Could not find a good starting point.")

        return params

    def pdf(self, y):
        """Probability density function for the variables
        y = log(S). Assumed to be uniform

        Parameters
        ----------
        y : ndarray
            Mapped variable y = f(x)

        Returns
        -------
        fy : ndarray
            Vector of PDF values associated with each value of y
        """

        fy = np.zeros_like(y)
        ii = np.where((y <= self.log_y_up) & (y >= self.log_y_low))[0]
        fy[ii] = 1 / (self.log_y_up[ii]-self.log_y_low[ii])

        return fy

    def log_pdf(self, y):
        """Log-probability density function for the joint variable
        y = log(S). Assumed to be uniform.

        Parameters
        ----------
        y : ndarray
            Mapped variable y = f(x)

        Returns
        -------
        log_fy : ndarray
            sum of log-PDF values associated with y.
        """
        if np.any(y < self.log_y_low) | np.any(y > self.log_y_up):
            return -np.inf

        return 0.0

    def draw(self):
        """Draw a vector around the reference y_ref using
        a random uniform distribution.

        Returns
        -------
        y_draw : ndarray
            Randomly perturbed reference vector
        """

        return np.log(self.y_ref) + np.random.uniform(
                    np.log(self.scale_low), np.log(self.scale_up))


class GaussianSplinePrior(SplinePrior):
    """Generate response for a stochastic gravitational-wave background.

    The +/x-polarized strains are white Gaussian noise.
    """

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.mean = np.log(np.abs(self.y_ref))
        self.sigma = (np.log(self.scale_up)-np.log(self.scale_low))/3

    def log_pdf(self, x):

        epsilon = x - self.mean

        return -0.5 * np.sum(np.abs(epsilon/self.sigma)**2)

    def draw(self):
        return np.log(self.y_ref) + np.random.normal(
            loc=0.0, scale=self.sigma)


class ComponentPrior:
    """
    Class implementing the prior distribution on the beta parameter 
    so that y = f(beta) follows a uniform distribution.
    The function f is some linear (or nonlinear) function of beta.
    """

    def __init__(self, noise_comps, y_ref,
                 scale_low=0.1,
                 scale_up=10.0,
                 delta_min=0,
                 mapping=None,
                 knee_freq_low=None,
                 knee_freq_up=None):
        """
        Instantitiate an instance of BetaAGGLogPrior.

        Parameters
        ----------
        noise_comps : list
            List of noise.NoiseModel objects describing the
            noise components.
        y_ref : int
            Baseline PSD that will determine the center of the distribution.
        scale_low : float, optional
            factor multiplying y_ref to get the lower bound, by default 0.1
        scale_up : float, optional
            factor multiplying y_ref to get the upper bound, by default 10.0
        mapping : PriorMap instance
            map from parameter space to y_ref
        knee_freq_low : list of ndarrays
            list of lower bound for knee frequencies (one item for each noise component)
        knee_freq_up : list of ndarray
            list of upper bound for knee frequencies (one item for each noise component)
        """

        # Noise classes
        self.noise_comps = noise_comps
        self.n_noises = len(noise_comps)
        # Parameter mapping
        if mapping is None:
            self.mapping = TDIPriorMap(noise_comps)
        elif isinstance(mapping, str):
            if mapping == "tdi":
                self.mapping = TDIPriorMap(noise_comps)
            elif mapping == "links":
                self.mapping = SingleLinkPriorMap(noise_comps)

        # For knot locations
        self.log_f_min = np.min(self.noise_comps[0].logfreq)
        self.log_f_max = np.max(self.noise_comps[0].logfreq)
        self.delta_min = delta_min

        # Reference PSD
        self.y_ref = y_ref

        # Bounds
        self.scale_up = scale_up
        self.scale_low = scale_low
        self.log_y_up = np.log(np.abs(y_ref)) + np.log(scale_up)
        self.log_y_low = np.log(np.abs(y_ref)) + np.log(scale_low)
        # Size of the PSD space
        self.ndim_y = self.y_ref.size
        # Number of frequency bins
        self.n_c = int(self.ndim_y / 2)

        # Total number of dimensions
        self.ndim = sum(comp.ndim for comp in self.noise_comps)

        # Upper and lower bounds for knee frequencies
        self.knee_freq_low = knee_freq_low
        self.knee_freq_up = knee_freq_up

    def logp_x_basis(self, x_basis):
        """evaluate value of the log-prior distribution
        at the basis arguments (knee frequencies)

        Parameters
        ----------
        x_basis : ndarray
            argument of the component basis (knee frequencies)

        Returns
        -------
        log_prior : float
            value of the log-prior probability at knee frequencies x

        """
        
        x_arr = np.concatenate([np.atleast_1d(x) for x in x_basis])
        if np.any(x_arr < np.concatenate(self.knee_freq_low)) | np.any(x_arr > np.concatenate(self.knee_freq_up)):
            return -np.inf

        return 0.0

    def evaluate(self, x):
        """
        Evaluate the value of the full log-prior at 
        parameter x.
        
        Parameters
        ----------
        x : ndarray
            spline parameters

        Returns
        -------
        log_prior : float
            value of the log-prior probability at spline parameters x
        
        """

        # Compute the log-prior probability of having
        # such knee frequencies (if they are free)
        if not self.noise_comps[0].fixed_basis:
            # List of knot location parameters or each noise component
            x_list = [x[nc.n_coeffs+self.mapping.ib[i]:self.mapping.ie[i]]
                      for i, nc in enumerate(self.noise_comps)]
            logp_x = self.logp_x_basis(x_list)

            # If the log prior for the knot location is -inf, then
            # no need to compute the prior for knot amplitudes
            if not np.isfinite(logp_x):
                return -np.inf

        # Compute the equivalent spectrum s_xx, s_xy
        y = self.mapping.forward_map(x)
        log_y = np.log(np.abs(y))
        # Verify that the spectra are within bounds
        logp_y = self.log_pdf(log_y)

        if np.isnan(logp_y):
            return -np.inf

        return logp_y.real

    def draw_knee_frequencies(self):
        """
        Draw the knee frequencies from a uniform prior.
        
        Returns
        -------
        knee_freq : list
            List of knee frequencies. Each item in the list corresponds
            to the knee frequencies for each noise components.
        
        """

        knee_freqs = [np.random.uniform(low=self.knee_freq_low[i],
                                        high=self.knee_freq_up[i]) 
                      for i in range(self.n_noises)]

        return knee_freqs

    def arange_parameters(self, beta, kneefreqs=None):
        """
        For book-keeping: append knot locations parameters to
        coefficients in the right ordering.

        Parameters
        ----------
        beta : ndarray
            vector of knot coefficients
        kneefreqs : list, optional
            list of vectors of knee frequencies, by default None

        Returns
        -------
        params : ndarray
            full noise parameter
        """
        # Re-ortder the output if necessary
        if kneefreqs is not None:
            params = []
            i0 = 0
            for i, nc in enumerate(self.noise_comps):
                params.append(beta[i0:i0+nc.n_coeffs])
                params.append(np.atleast_1d(kneefreqs[i]))
                i0 += nc.n_coeffs
            params = np.concatenate(params).real
        else:
            params = beta.real

        return params

    def initialize_single_param(self, n_draws=1000):
        """
        Generate random number that approximately follow
        the required distirbution.
        """
        ok_flag = False
        i = 0

        while (not ok_flag) & (i < n_draws):
            # Perturb the baseline
            log_y = self.draw()
            # If necessary, draw knee frequencies
            if not self.noise_comps[0].fixed_basis:
                knee_freqs = self.draw_knee_frequencies()
            else:
                knee_freqs = None
            # Compute the equivalent regression parameter
            beta = self.mapping.inverse_map(np.exp(log_y), basis_args=knee_freqs)
            # Include all parameters in a single array
            params = self.arange_parameters(beta, kneefreqs=knee_freqs)
            # Evaluate the logprior at this point
            logp = self.evaluate(params.real)
            if np.isfinite(logp):
                ok_flag = True
            i += 1

        if not ok_flag:
            warnings.warn("Could not find a good starting point.")

        return params

    def pdf(self, y):
        """Probability density function for the variables
        y = log(S). Assumed to be uniform

        Parameters
        ----------
        y : ndarray
            Mapped variable y = f(x)

        Returns
        -------
        fy : ndarray
            Vector of PDF values associated with each value of y
        """
        fy = np.zeros_like(y)
        ii = np.where((y <= self.log_y_up) & (y >= self.log_y_low))[0]
        fy[ii] = 1 / (self.log_y_up[ii]-self.log_y_low[ii])

        return fy

    def log_pdf(self, y):
        """Log-probability density function for the joint variable
        y = log(S). Assumed to be uniform.

        Parameters
        ----------
        y : ndarray
            Mapped variable y = f(x)

        Returns
        -------
        log_fy : ndarray
            sum of log-PDF values associated with y.
        """
        if np.any(y < self.log_y_low) | np.any(y > self.log_y_up):
            return -np.inf

        return 0.0

    def draw(self):
        """Draw a vector around the reference y_ref using
        a random uniform distribution.

        Returns
        -------
        y_draw : ndarray
            Randomly perturbed reference vector
        """
        return np.log(self.y_ref) + np.random.uniform(
                    np.log(self.scale_low), np.log(self.scale_up))
