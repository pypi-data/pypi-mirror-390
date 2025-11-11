# -*- coding: utf-8 -*-
# Author: Quentin Baghi 2021 <quentin.baghi@protonmail.com>
import warnings
import jax
import jax.numpy as jnp
import numpy as np
from scipy import special, sparse, interpolate, integrate
from interpax import Interpolator1D, Interpolator2D
# FTT modules
try:
    from pyfftw.interfaces.numpy_fft import fft, ifft
except ImportError:
    from numpy.fft import fft, ifft


def order2kind(interp_order):
    """
    Convert interpolation order to interpolation kind.
    """

    # Create interpolating function
    if interp_order == 1:
        kind = 'linear'
    elif interp_order == 2:
        kind = 'quadratic'
    elif interp_order == 3:
        kind = 'cubic'
    else:
        raise TypeError(
            f"invalid interpolation order '{interp_order}', must be 1, 2 or 3")

    return kind


def generate_noise(psd_func, n_data, fs, n_psd=None, f_zero=None):
    """
    Noise generator from arbitrary power spectral density.
    Uses a Gaussian random generation in the frequency domain.

    Parameters
    ----------
    psd_func: callable
        one-sided PSD function in A^2 / Hz, where A is the unit of the desired
        output time series. Can also return a p x p spectrum matrix
    n_data: int
        size of output time series
    fs: float
        sampling frequency in Hz
    n_psd : int
        number of random points to generate in the frequency domain
        if None, the default is 2 x n_data.
    f_zero: float or None
        the value to use for the zero frequency. If None (default), the zero frequency is chosen
        equal to the frequency resolution fs / n_data.

    Returns
    -------
    tseries: ndarray
        generated time series

    """

    # Number of points to generate in the frequency domain (circulant embedding)
    if n_psd is None:
        n_psd = 2 * n_data
    # Number of positive frequencies
    n_fft = int((n_psd-1)/2)
    # Frequency array
    f = np.fft.fftfreq(n_psd)*fs
    # Avoid zero frequency as it sometimes makes the PSD infinite
    if f_zero is None:
        f[0] = f[1]
    else:
        f[0] = f_zero
    # Compute the PSD (or the spectrum matrix)
    psd_f = psd_func(np.abs(f))

    if psd_f.ndim == 1:
        psd_sqrt = np.sqrt(psd_f)
        # Real part of the Noise fft : it is a gaussian random variable
        noise_tf_real = np.sqrt(0.5) * psd_sqrt[0:n_fft + 1] * np.random.normal(
            loc=0.0, scale=1.0, size=n_fft + 1)
        # Imaginary part of the Noise fft :
        noise_tf_im = np.sqrt(0.5) * psd_sqrt[0:n_fft + 1] * np.random.normal(
            loc=0.0,  scale=1.0, size=n_fft + 1)
        # The Fourier transform must be real in f = 0
        noise_tf_im[0] = 0.
        noise_tf_real[0] = noise_tf_real[0]*np.sqrt(2.)
        # Create the NoiseTF complex numbers for positive frequencies
        noise_tf = noise_tf_real + 1j*noise_tf_im
    elif psd_f.ndim == 3:
        # Number of variables
        p = psd_f.shape[1]
        # Form the covariance matrices in the Fourier domain
        cov = psd_f[0:n_fft + 1]
        # Perform Cholesky factorization of the correlation matrices C_m
        psd_sqrt = np.linalg.cholesky(cov)
        # Real part of the Noise fft : it is a gaussian random variable
        w_real = np.sqrt(0.5) * np.random.multivariate_normal(
            np.zeros(p), np.eye(p), size=n_fft + 1)
        w_imag = np.sqrt(0.5) * np.random.multivariate_normal(
            np.zeros(p), np.eye(p), size=n_fft + 1)
        # Generate the Z_m in the Fourier domain
        noise_tf = multiple_dot_vect(psd_sqrt, w_real + 1j*w_imag)
        # The Fourier transform must be real in f = 0
        noise_tf[0].imag = 0
        noise_tf[0].real = noise_tf[0].real*np.sqrt(2.)

    # To get a real valued signal we must have NoiseTF(-f) = NoiseTF*
    if (n_psd % 2 == 0) & (psd_f.ndim == 1):
        # The TF at Nyquist frequency must be real in the case of an even
        # number of data
        noise_sym0 = np.array([psd_sqrt[n_fft + 1] * np.random.normal(0, 1)])
        # Add the symmetric part corresponding to negative frequencies
        noise_tf = np.hstack((noise_tf, noise_sym0,
                              np.conj(noise_tf[1:n_fft+1])[::-1]))
    elif (n_psd % 2 != 0) & (psd_f.ndim == 1):
        noise_tf = np.hstack((noise_tf, np.conj(noise_tf[1:n_fft+1])[::-1]))

    elif (n_psd % 2 == 0) & (psd_f.ndim == 3):
        noise_sym0 = np.random.multivariate_normal(np.zeros(p), psd_f[n_fft + 1].real)
        noise_tf = np.concatenate((noise_tf, noise_sym0[np.newaxis, :],
                                   np.conj(noise_tf[1:n_fft+1])[::-1]))

    elif (n_psd % 2 != 0) & (psd_f.ndim == 3):
        noise_tf = np.concatenate((noise_tf, np.conj(noise_tf[1:n_fft+1])[::-1]))
    else:
        warnings.WarningMessage("Invalid spectrum dimension", UserWarning, "invalid_dim", 149)

    tseries = ifft(np.sqrt(n_psd*fs/2.) * noise_tf, axis=0)

    return tseries[0:n_data].real


def convolution(x, func_1, func_2):

    dx = x[1] - x[0]

    f1_ft = fft(func_1(x), n=2*x.shape[0])
    f2_ft = fft(func_2(x), n=2*x.shape[0])

    conv = ifft(f1_ft * f2_ft) * dx

    return dx


def cross_spectrum(psd_func, kernel_t_1, kernel_t_2, fs, n_fft=None):
    """

    Compute the cross spectrum (i.e., the mean of the cross-periodogram)
    of two time series of the form :

    y1 = n * kernel_1
    y2 = n * kernel_2

    where n is a stationary noise of PSD psd_func and kernel_i is a time-domain
    function. 

    This function computes S_12 = E[ y1.y2^{*} * 2 / (n_data*fs)]

    Parameters
    ----------
    psd_func : callable
        one-sided PSD function
    kernel_t_1 : ndarray
        Time series of the first kernel
    kernel_t_2 : ndarray
        Time series of the second kernel


    """

    n_data = kernel_t_1.shape[0]
    if n_fft is None:
        n_fft = 2 * n_data

    # # Convolution computation
    # kernel_t_fft = fft(kernel_t_1, n_fft)
    # kernel_t_2_fft = fft(kernel_t_2, n_fft)
    # # kernel_t_power = np.abs(kernel_t_fft) ** 2 / n_fft
    # kernel_t_power_12 = kernel_t_fft * np.conj(kernel_t_2_fft)/ n_fft
    # f2 = np.fft.fftfreq(n_fft) * fs
    # s2 = psd_func(np.abs(f2))
    # s12 = ifft(fft(s2) * fft(kernel_t_power_12))[0:n_data] / n_fft

    # Convolution computation
    kernel_t_fft = fft(kernel_t_1)
    kernel_t_2_fft = fft(kernel_t_2)
    # kernel_t_power = np.abs(kernel_t_fft) ** 2 / n_fft
    kernel_t_power_12 = kernel_t_fft * np.conj(kernel_t_2_fft) / n_data
    f = np.fft.fftfreq(n_data) * fs
    s2 = psd_func(np.abs(f))
    s12 = ifft(fft(s2, n_fft) * fft(kernel_t_power_12, n_fft)
               )[0:n_data] / n_data

    return s12


def compute_power_law_convolution(f, p, q, f_max):
    """

    Compute the convolution of two functions s(f) = f^p and k(f) = f^q

    """

    conv = f**(p+q+1)
    x2 = f_max / f
    integrant = x2**(p+1)/(p+1) * special.hyp2f1(p+1, -q, p+2, x2)
    # integrant -= x1**(p+1)/(p+1) * special.hyp2f1(p+1, -q, p+2, x1)

    return 2 * conv * integrant


def cross_spectrum_approx(f0, f, psd, kernel_f_1, kernel_f_2, fh):
    """
    Compute the cross spectrum of two links based on a convolution
    of the PSD of the stochastic source with the links' kernels, using 
    a short-bandwidth approximation of the kernels.

    Parameters
    ----------
    f0 : float
        frequency at which to compute the convolution
    f : ndarray
        frequency where the PSD is given
    psd : ndarray
        PSD computed at Fourier frequency array f
    kernel_f_1 : ndarray
        First kernel computed at the same frequencies as the PSD
    kernel_f_2 : ndarray
        Second kernel computed at the same frequencies as the PSD
    fs : float
        sampling frequency


    """

    df = f[1] - f[0]
    inds = np.where(np.abs(f-f0) <= fh)[0]

    return np.sum(psd[inds] * kernel_f_1 * np.conj(kernel_f_2)) * df


class LagrangeInterpolator(object):

    def __init__(self, t, y, nint, dtype=np.float64):

        self.t = t
        self.y = y
        self.nint = nint
        # Matrix of differences Mat[k, j] = x[k] - x[j] (except for j = k)
        self.mat = self.prod_matrix()
        # Vector of products prod_{j=0, j!=k}^{nint-1} (x[k] - x[j]) for all j
        self.prods = np.prod(self.mat, axis=1)
        # Sampling time
        self.ts = t[1] - t[0]
        self.nc = np.int((nint - 1) / 2)

    def prod_matrix(self):
        """

        Produce a matrix where each row k contains the terms
        x[k]-x[0], x[k]-x[1], ..., x[k]-x[k-1], x[k]-x[k+1], ...,x[k]-x[nint-1]

        Parameters
        ----------
        t : array_like
            time vector
        nint : scalar integer
            order of the lagrange polynomial

        Returns
        -------
        mat : 2d numpy array
            nint x nint-1 matrix containing the where each row k is given by 
            the differences x[k] - x[j] (except for j = k)

        """

        xn = self.t[0:self.nint]

        mat = np.array([xn[k]-xn[xn != xn[k]] for k in range(self.nint)],
                       dtype=self.y.dtype)

        return mat

    def compute_lagrange_poly(self, xmeas, x):
        """

        Compute the Lagrange polynomials L_j(x) calculated at x
        for all j in [0, nint]

        L_j(x) = Prod_{k=0, k!=j}^{nint} (x - xmeas[k]) / (xmeas[j] - xmeas[k]) 

        Parameters
        ----------
        xmeas : ndarray
            Abscissa (or times) at each the data is measured, size nint.
        x : float
            Interpolation time (at which to calculate new data)

        Returns
        -------
        lj : ndarray
            Array containing the L_j(x) for j=0..nint.
        """

        # The product (x - x_meas[0]) (x - x_meas[1]) ... (x - x_meas[nint])
        full_prod = np.prod(x - xmeas)
        # A vector nums containing all the numerators of the Lagrange
        # polynomial expression, obtained by removing x - x[n] to the full
        # product: nums[j] = Prod_i i!j (x - x_meas[i]) for j=0...nint-1
        nums = full_prod / (x - xmeas)
        # Devide by the vector v of products
        # v[j] = prod_{i=0, i!=j}^{nint-1} (x[j] - x[o])
        if xmeas.shape[0] == 2 * self.nc + 1:
            # If it has size 2nc+1 we already have it computed:
            return nums / self.prods
        else:
            mat = np.array([xmeas[j]-xmeas[xmeas != xmeas[j]]
                            for j in range(xmeas.shape[0])],
                           dtype=self.y.dtype)
            prods = np.prod(mat, axis=1)
            return nums/prods

    def single_interp(self, xmeas, ymeas, x):
        """

        Perform a single interpolation at x, given the dara ymeas measured at 
        xmeas.

        Parameters
        ----------
        xmeas : ndarray
            Abscissa (or times) at each the data is measured, size nint.
        ymeas : ndarray
            Measured data corresponding to xmeas, size nint.
        x : float
            Interpolation time (at which to calculate new data)

        Returns
        -------
        yint : float
            Interpolated point at x.
        """

        lj = self.compute_lagrange_poly(xmeas, x)
        # The interpolated data
        return np.sum(lj * ymeas)

    def ind_start(self, t_int):
        """
        Time index corresponding to the lower bound of the measured interval

        Parameters
        ----------
        t_int : float
            interpolation time

        Returns
        -------
        i_start : int
            initial index of measured interval

        """

        return np.max([np.int(t_int/self.ts) - self.nc, 0])

    def ind_end(self, t_int):
        """
        Time index corresponding to the upper bound of the measured interval

        Parameters
        ----------
        t_int : float
            interpolation time

        Returns
        -------
        i_end : int
            ending index of measured interval
        """

        return np.min([np.int(t_int/self.ts) + self.nc + 1,
                       self.t.shape[0]])

    def interp(self, t_interp):
        """

        Parameters
        ----------
        t_interp : float
            time where to interpolate the data. It is assumed that all times in
            t_interp are included in the
            time vector self.t

        Returns
        -------
        x : ndarray
            vector of interpolated data (same size as t_interp).

        """

        # Interpolation is only valid between time t = (nint-1)/2 and times
        # t = N - 1 - (nint-1)/2
        print("value of nc " + str(self.nc))
        print("Length of t_interp " + str(t_interp.shape[0]))
        print("Length of t " + str(self.t.shape[0]))
        print("Length of y " + str(self.y.shape[0]))

        # x = np.array([self.single_interp(
        #     self.t[np.int(t_interp[n]/self.ts)
        #            - self.nc:np.int(t_interp[n]/self.ts) + self.nc + 1],
        #     self.y[np.int(t_interp[n]/self.ts)
        #            - self.nc:np.int(t_interp[n]/self.ts) + self.nc + 1],
        #     t_interp[n]) for n in range(t_interp.shape[0])],
        #              dtype=self.y.dtype)
        x = np.array([self.single_interp(
            self.t[self.ind_start(t_interp[n]):self.ind_end(t_interp[n])],
            self.y[self.ind_start(t_interp[n]):self.ind_end(t_interp[n])],
            t_interp[n]) for n in range(t_interp.shape[0])],
            dtype=self.y.dtype)

        return x

    def build_matrix(self, t_interp):
        """
        build the sparse matrix L to be applied to the input measurement vector 
        to obtain delayed data, such that:

        x = L y

        Parameters
        ----------
        t_interp : float
            time where to interpolate the data. It is assumed that all times in
            t_interp are included in the
            time vector self.t

        Returns
        -------
        l_mat : scipy.sparse.csc_matrix
            linear operator equilavent to Lagrange interpolation
        """

        tmeas_list = [self.t[np.int(ti/self.ts)
                             - self.nc:np.int(ti/self.ts)+self.nc+1]
                      for ti in t_interp]

        data_list = [self.compute_lagrange_poly(tmeas_list[n], t_interp[n])
                     for n in range(t_interp.shape[0])]

        # Create rows indice array
        row_ind = np.concatenate([i*np.ones(data_list[i].shape[0])
                                  for i in range(t_interp.shape[0])])
        col_ind = np.concatenate([np.arange(np.int(ti/self.ts) - self.nc,
                                            np.int(ti/self.ts)+self.nc+1)
                                  for ti in t_interp])

        return sparse.csc_matrix((np.concatenate(data_list),
                                  (row_ind, col_ind)),
                                 shape=(t_interp.shape[0], self.t.shape[0]))


def compute_fourier_series(t_samples, s_samples, tobs):
    """
    Compute Fourier series coeffcicients of the signal

    Parameters
    ----------
    t_samples : ndarray
        time samples
    s_samples : ndarray
        signal samples to interpolate
    tobs : float
        observation time
    """

    # Compute Fourier series coefficients
    c = fft(np.array(s_samples)) / t_samples.size

    # Compute corresponding frequency vector
    f_vect = np.fft.fftfreq(c.shape[0],
                            d=tobs / c.shape[0])

    # Compute the Fourier series approximation
    s_approx = np.sum([c[n] * np.exp(1j * np.pi * f_vect[n] * t_samples)
                       for n in range(c.shape[0])])

    return c, s_approx
    # # t2 = time.time()
    # #print("FFT: " + str(t2 - t1))
    # # print("Shape of c_list" + str(c_list.shape))
    # # t1 = time.time()
    # # Form the grid of frequency differences, size nf x nc
    # f_grid = np.array([f]) - np.array([f_vect]).T
    # # t2 = time.time()
    # # print("Frequency grid: " + str(t2 - t1))
    # # Assume that v_func includes f_dot dependence
    # # v_list = self.v_func(f_grid, f_0, f_dot, self.tobs, self.del_t)
    # # Assume that v_func is monochromatic
    # # t1 = time.time()
    # v_list = self.v_func(f_grid, f_0, self.tobs, self.del_t)
    # # t2 = time.time()
    # # print("Waveform grid: " + str(t2 - t1))
    # # print("Shape of v_list" + str(v_list.shape))
    # # v_list = [self.v_func(f - f_vect[k], f_0, f_dot, self.tobs, self.del_t)
    # #           for k in range(c_list[0].shape[0])]
    # # t1 = time.time()
    # a_mat_list = [self.compute_series(v_list, c_list[i]) / 2
    #               for i in range(len(c_list))]
    # # np.sum(c * np.array([v_list]).T, axis=1)


@jax.jit
def multiple_dot(a_mat, b_mat):
    """
    Perform the matrix multiplication of two list of matrices.

    Parameters
    ----------
    a : ndarray
        series of m x n matrices (array of size p x m x n)
    b : ndarray
        series of n x k matrices (array of size p x n x k)

    Returns
    -------
    c : ndarray
        array of size p x m x k containg the dot products of all matrices
        contained in a and b.


    """
    return jnp.einsum("...jk, ...kl", a_mat, b_mat)


@jax.jit
def multiple_dot_vect(a_mat, b_vect):
    """
    Performs matrix-to-vector multiplication on a array of matrices and vectors

    Parameters
    ----------
    a : ndarray
        series of m x n matrices (array of size p x m x n)
    b : ndarray
        series of n x k vectors (array of size p x n)

    Returns
    -------
    c : ndarray
        array of size p x m containg the dot products of all vectors
        contained in a and b.


    """
    return jnp.einsum("...jk, ...k", a_mat, b_vect)

@jax.jit
def transform_covariance(tf, cov):
    """
    Compute the product tf cov tf^H for an array of matrices and a covariances.

    Parameters
    ----------
    tf : ndarray
        transfer function matrix, size nf x p x q
    cov : covariance matrix
        covariance matrix, size nf x q x q

    Returns
    -------
    tfcovtft : ndarray
        matrix product tf cov tf^H, size nf x p x p
    """

    return multiple_dot(tf, multiple_dot(cov, jnp.conj(jnp.swapaxes(tf, cov.ndim-2, cov.ndim-1))))

@jax.jit
def compute_covariances(link_psd, tdi_corr):
    """
    Calculate the full covariances at frequencies finds.

    Parameters
    ----------
    link_psd : ndarray
        Link PSD of size nf
    tdi_corr : ndarray
        Correlation matrix of size nf x nt x 3 x 3

    Returns
    -------
    cov : ndarray
        matrix of covariances for all channels, size nf x 3 x 3 
        (if t0 is a float or average is True) or size nf x nt x 3 x 3
    """

    # Apply TDI transfer matrix to the single-link PSDs
    cov_tdi = jnp.multiply(tdi_corr.T, link_psd).T

    return cov_tdi

@jax.jit
def sum_covariances(cov_list):
    """
    Sum a list of covariance matrices.

    Parameters
    ----------
    cov_list : list of ndarray
        List of covariance matrices to sum.

    Returns
    -------
    cov_sum : ndarray
        Sum of the covariance matrices.
    """
    return jnp.sum(jnp.array(cov_list), axis=0)

@jax.jit
def sym_matrix_inv_from_rows(a, b, c, e, f, i):
    """_summary_

    Parameters
    ----------
    a : array_like
        00 element
    b : array_like
        01 element
    c : array_like
        02 element
    e : array_like
        11 element
    f : array_like
        12 element
    i : array_like
        22 element

    Returns
    -------
    mat_inv : ndarray
        array of inverse matrices
    det : ndarray
        array of matrix determinants
    """

    big_a = e*i - jnp.abs(f)**2
    big_b = - (jnp.conj(b)*i-f*jnp.conj(c))
    big_c = jnp.conj(b)*jnp.conj(f) - e*jnp.conj(c)
    big_e = a*i - jnp.abs(c)**2
    big_f = - (a*jnp.conj(f) - b * jnp.conj(c))
    big_i = a*e - jnp.abs(b)**2

    det = a * big_a + b * big_b + c * big_c

    # Create a 3 x 3 x nf matrix
    mat_inv = jnp.array([[big_a, big_b, big_c], [jnp.conj(big_b), big_e, big_f],
                        [jnp.conj(big_c), jnp.conj(big_f), big_i]])
    mat_inv = (1 / det[:, jnp.newaxis, jnp.newaxis]) * jnp.transpose(mat_inv)

    return mat_inv, det


def sym_matrix_inv(mat):
    """

    Efficiently computes the inverse of a 
    series of 3 x 3 symmetric matrices.

    Parameters
    ----------
    mat : ndarray
        series of matrices n_mat x 3 x 3

    Returns
    -------
    mat_inv : ndarray
        series of matrix inverses (size n_mat x 3 x 3)
    det : ndarray, optional
        series of determinants (size n_mat)
    """

    a = mat[:, 0, 0]
    b = mat[:, 0, 1]
    c = mat[:, 0, 2]
    e = mat[:, 1, 1]
    f = mat[:, 1, 2]
    i = mat[:, 2, 2]

    mat_inv, det = sym_matrix_inv_from_rows(a, b, c, e, f, i)

    return mat_inv, det


class CovarianceInterpolator:
    """Interpolate frequency-domain covariance matrices (assumed to be Hermitian)
    """

    def __init__(self, x, mat, kind='cubic', fill_value="extrapolate") -> None:
        """
        Class constructor.

        Parameters
        ----------
        x : array_like
            interpolation points
        mat : array_like
            covariance matrices to interpolate, size n_freq x n x m
        kind : str, optinal
            interpolation kind, default is 'cubic'
        fill_value : str, optional
            value to use for points outside the interpolation range.

        """

        # Number of rows
        self.n = mat.shape[-2]
        # Number of columns
        self.m = mat.shape[-1]

        # Gather the upper triangular part of the matrix, excluding the diagonal
        self.triu_idx = np.triu_indices(self.n, k=1)
        # Gather the diagonal indices
        self.diag_idx = np.diag_indices(self.n)

        if fill_value == "extrapolate":
            extrap = True
        else:
            extrap = False

        # Create an interpolator of the diagonal elements
        self.diag_interpolators = Interpolator1D(x,
                                                 mat[..., self.diag_idx[0], self.diag_idx[1]].real,
                                                 method=kind, extrap=extrap)
        # Create an interpolator of the upper triangular elements, real part
        self.offr_interpolators = Interpolator1D(x,
                                                 mat[..., self.triu_idx[0], self.triu_idx[1]].real,
                                                 method=kind, extrap=extrap)
        # Create an interpolator of the upper triangular elements, imaginary part
        self.offi_dinterpolators = Interpolator1D(x,
                                                 mat[..., self.triu_idx[0], self.triu_idx[1]].imag,
                                                 method=kind, extrap=extrap)

    def __call__(self, x_new):
        """Evaluate the covariance at new points

        Parameters
        ----------
        x_new : array_like
            new inteprolation points
        """
        # Evaluate the upper triangular part of the matrix
        mat_triu = self.offr_interpolators(x_new) + 1j*self.offi_dinterpolators(x_new)
        # Create an empty array
        mat = np.zeros(x_new.shape + (self.n, self.m), dtype=mat_triu.dtype)
        # Fill the diaogonal part
        mat[..., self.diag_idx[0], self.diag_idx[1]] = self.diag_interpolators(x_new)
        # Fill the upper triangular part
        mat[..., self.triu_idx[0], self.triu_idx[1]] = mat_triu
        # Fill the lower triangular part by symmetry
        mat[..., self.triu_idx[1], self.triu_idx[0]] = np.conj(mat_triu)

        return mat


class Covariance2DInterpolator:
    """Interpolate time-frequency-domain covariance matrices (assumed to be Hermitian)
    """
    def __init__(self, x, y, mat, kind='cubic', fill_value="extrapolate") -> None:
        """
        Interpolates a time-frequency matrix function.
        """

        # Number of rows
        self.n = mat.shape[-2]
        # Number of columns
        self.m = mat.shape[-1]

        # Gather the upper triangular part of the matrix, excluding the diagonal
        self.triu_idx = np.triu_indices(self.n, k=1)
        # Gather the diagonal indices
        self.diag_idx = np.diag_indices(self.n)

        if fill_value == "extrapolate":
            extrap = True
        else:
            extrap = False

        # Create an interpolator of the diagonal elements
        self.diag_interpolators = Interpolator2D(x, y,
                                                 mat[..., self.diag_idx[0], self.diag_idx[1]].real,
                                                 method=kind, extrap=extrap)
        # Create an interpolator of the upper triangular elements, real part
        self.offr_interpolators = Interpolator2D(x, y,
                                                 mat[..., self.triu_idx[0], self.triu_idx[1]].real,
                                                 method=kind, extrap=extrap)
        # Create an interpolator of the upper triangular elements, imaginary part
        self.offi_dinterpolators = Interpolator2D(x, y,
                                                 mat[..., self.triu_idx[0], self.triu_idx[1]].imag,
                                                 method=kind, extrap=extrap)

    def __call__(self, x_new, y_new):
        """Evaluate the covariance at new points

        Parameters
        ----------
        x_new : array_like
            new inteprolation points on the first axis (size N)
        y_new : array_like
            new inteprolation points on the second axis (size N)

        Returns
        -------
        mat : ndarray
            interpolated covariance matrices at (x_new, y_new). The output shape is (N, n, m)
        """
        # Evaluate the upper triangular part of the matrix
        mat_triu = self.offr_interpolators(x_new, y_new) + 1j*self.offi_dinterpolators(x_new, y_new)
        # Create an empty array
        mat = np.zeros((x_new.size, self.n, self.m), dtype=mat_triu.dtype)
        # Fill the diaogonal part
        mat[:, self.diag_idx[0], self.diag_idx[1]] = self.diag_interpolators(x_new, y_new)
        # Fill the upper triangular part
        mat[:, self.triu_idx[0], self.triu_idx[1]] = mat_triu
        # Fill the lower triangular part by symmetry
        mat[:, self.triu_idx[1], self.triu_idx[0]] = np.conj(mat_triu)

        return mat


class MatrixInterpolator:

    def __init__(self, x, mat, kind='cubic') -> None:

        # Output type
        dtype = type(interpolate.interp1d([0, 1], [0, 1]))

        # If the array is 3D, we assume n_freq x n x m
        if len(mat.shape) == 3:
            # Number of rows
            self.n = mat.shape[1]
            # Number of columns
            self.m = mat.shape[2]
            # Inteprolator matrix
            self.mat_real = np.empty((self.n, self.m), dtype=dtype)
            self.mat_imag = np.empty((self.n, self.m), dtype=dtype)
            # Diagonal elements
            for i in range(self.n):
                for j in range(self.m):
                    self.mat_real[i, j] = interpolate.interp1d(x, mat.real[:, i, j],
                                                               kind=kind,
                                                               fill_value="extrapolate")
                    self.mat_imag[i, j] = interpolate.interp1d(x, mat.imag[:, i, j],
                                                               kind=kind,
                                                               fill_value="extrapolate")

        else:
            raise ValueError("The array provided should have 3 dimensions.")

    def __call__(self, x_new):

        mat = np.zeros((len(x_new), self.n, self.m), dtype=complex)

        for i in range(self.n):
            for j in range(self.m):
                mat[:, i, j] = self.mat_real[i, j](
                    x_new) + 1j * self.mat_imag[i, j](x_new)

        return mat


def hypertriangulate(x, bounds=(0, 1)):
    """
    Transform a vector of numbers from a cube to a hypertriangle.
    The hypercube is the space the samplers work in, and the hypertriangle is
    the physical space where the components of x are ordered such that
    x0 < x1 < ... < xn. The (unit) transformation is defined by:
    .. math::
        X_j = 1 - \\prod_{i=0}^{j} (1 - x_i)^{1/(K-i)}
    Parameters
    ----------
    x: array
        The hypercube parameter values
    bounds: tuple
        Lower and upper bounds of parameter space. Default is to transform
        between the unit hypercube and unit hypertriangle.
    Returns
    -------
    X: array
        The hypertriangle parameter values

    Reference
    ---------
    Riccardo Buscicchio et al, 10.5281/zenodo.3351629


    """

    # transform to the unit hypercube
    unit_x = (np.array(x) - bounds[0]) / (bounds[1] - bounds[0])

    # hypertriangle transformation
    with warnings.catch_warnings():
        # this specific warning is raised when unit_x goes outside [0, 1]
        warnings.filterwarnings('error', 'invalid value encountered in power')
        try:
            K = np.size(unit_x)
            index = np.arange(K)
            inner_term = np.power(1 - unit_x, 1/(K - index))
            unit_X = 1 - np.cumprod(inner_term)
        except RuntimeWarning as exc:
            raise ValueError('Values outside bounds passed to hypertriangulate') from exc

    # re-apply orginal scaling, offset
    X = bounds[0] + unit_X * (bounds[1] - bounds[0])

    return X


def hypertriangulate_reverse(X, bounds=(0, 1)):

    unit_X = (np.array(X) - bounds[0]) / (bounds[1] - bounds[0])

    K = np.size(unit_X)
    index = np.arange(K)

    unit_X_ext = np.concatenate([[0], unit_X])

    unit_x = 1 - np.power(1 - unit_X_ext[0:-1], -(K - index)) * \
        np.power(1 - unit_X_ext[1:], (K - index))

    x = bounds[0] + unit_x * (bounds[1] - bounds[0])

    return x


def compute_log_evidence(logpvals, beta_ladder):
    """

    Parameters
    ----------
    logpvals : numpy array
        ntemps x nsamples matrix containing all the samples at different temperatures.
        from temperature T=1 to temperature T=inf  (beta = 1 to beta=0)
    beta_ladder : numpy array
        inverse temperature ladder


    Returns
    -------
    loge: scalar float
        logarithm of the evidence
    loge_std : scalar float
        estimated standard deviation of the log-evidence


    References
    ----------
    Lartillot, Nicolas and Philippe, Herve, Computing Bayes Factors Using Thermodynamic Integration,
    2006


    """

    # Sample average of log(p|theta)
    eu = np.mean(logpvals, axis=1)
    # Number of samples
    n_samples = logpvals.shape[1]
    # Sample variance of log(p|theta)
    vu = np.var(logpvals, axis=1)/n_samples

    # Integral over beta
    beta_max = np.max(beta_ladder)
    beta_min = np.min(beta_ladder)
    ntemps = len(beta_ladder)
    loge_std = (beta_max - beta_min) / ntemps * np.sqrt(np.sum(vu))
    loge = integrate.simps(eu[::-1], beta_ladder[::-1])

    return loge, loge_std


def sym_matrix_det(mat):
    """
    Compute the determinant of a series of 3 x 3 matrices

    A = [a, b, c
         d, e, f,
         g, h, i]

    D = a(ei − fh) − b(di − fg) + c(dh − eg)

    For
    d = conj(b)
    g = conj(c)
    h = conj(f)

    D = a(ei - |f|^2) - b(conj(b)i - f * conj(c)) + c(conj(b)*conj(f)
    - e * conj(c))



    """

    a = mat[:, 0, 0]
    b = mat[:, 0, 1]
    c = mat[:, 0, 2]
    e = mat[:, 1, 1]
    f = mat[:, 1, 2]
    i = mat[:, 2, 2]

    return a * (e*i - np.abs(f)**2) - b * (np.conj(b)*i-f*np.conj(c)) \
        + c * (np.conj(b)*np.conj(f) - e*np.conj(c))


def eigenvalues_to_eigenvectors(a, b, c, d, e, f, lamb, norm=False):

    m = (np.conj(d) * (c - lamb) - e * np.conj(f)) / (np.conj(f) * (b - lamb)
                                                      - np.conj(d) * np.conj(e))

    v = np.array([(lamb - c - np.conj(e) * m) /
                  np.conj(f), m, np.ones(a.shape[0])])

    if norm:
        normalization = np.sqrt(np.sum(np.abs(v), axis=0))
    else:
        normalization = 1.0

    return v / normalization


def closed_form_solution(a, b, c, d, e, f, norm=False):
    """
    Closed-form solution of the eigenvalues and eigenvectors of a series of
    3 x 3 matrix of the form

        a,  d,  f
    C = d*, b,  e
        f*, e*, c

    based on https://hal.archives-ouvertes.fr/hal-01501221


    Parameters
    ----------
    a : ndarray
        vector of 11 elements
    b : ndarray
        vector of 22 elements
    c : ndarray
        vector of 33 elements
    d : ndarray
        vector of 12 elements
    e : ndarray
        vector of 23 elements
    f : ndarray
        vector of 13 elements

    Returns
    -------
    lambs : ndarray
        array of size n x 3 convaining the eigenvalues
    vects : ndarray
        array of size n x 3 x 3 containing all eigenvectors

    """

    # a, b, c are supposed to have null imaginary part
    a = np.real(a)
    b = np.real(b)
    c = np.real(c)

    sabc = a + b + c
    k1 = 2 * a - b - c
    k2 = 2 * b - a - c
    k3 = 2 * c - a - b

    x1 = a**2 + b**2 + c**2 - a * b - a * c - b * c + 3 * (
        np.abs(d)**2 + np.abs(f)**2 + np.abs(e)**2)
    x2 = - k1 * k2 * k3 + 9 * (k3 * np.abs(d)**2 + k2 * np.abs(f)**2
                               + k1 * np.abs(e)**2) - 54 * np.real(
                                   d * e * np.conj(f))

    phi0 = np.arctan(np.sqrt(4 * x1**3 - x2**2) / x2)
    phi = np.zeros(a.shape[0], dtype=a.dtype)
    phi[x2 > 0] = phi0[x2 > 0]
    phi[x2 == 0] = np.pi / 2
    phi[x2 < 0] = phi0[x2 < 0] + np.pi

    l1 = (sabc - 2 * np.sqrt(x1) * np.cos(phi / 3)) / 3
    l2 = (sabc + 2 * np.sqrt(x1) * np.cos((phi - np.pi) / 3)) / 3
    l3 = (sabc + 2 * np.sqrt(x1) * np.cos((phi + np.pi) / 3)) / 3

    lambs = np.array([l1, l2, l3])

    vects = np.array([eigenvalues_to_eigenvectors(a, b, c, d, e, f, lamb, norm=norm)
                      for lamb in lambs])

    # Special case qhere f == 0?
    return lambs.T, vects.T


def initialize_params(config, initialize_single_param, **kwargs):
    """Initialize sampler parameter state

    Parameters
    ----------
    config : _type_
        _description_
    initialize_single_param : callable
        function that initializes one parameter instance


    """

    if config["sampler"].get("Sampler") == 'ptemcee':

        ntemps = config["sampler"].getint("Temperatures")
        nwalkers = config["sampler"].getint("Walkers")
        # Intialize the parameter state
        p0 = np.array([[initialize_single_param(**kwargs)
                        for j in range(nwalkers)]
                       for i in range(ntemps)])

    elif config["sampler"].get("Sampler") == 'ptmcmc':
        # Intialize the parameter state
        p0 = initialize_single_param()

    return p0


def reorganise(freqs, eigenvalues, eigenvectors, sep=6e-2):
    """
    Re-order the frequency-dependent eigenvalues to ensure continuity.
    TODO: needs extension to handle any possible case.

    Parameters
    ----------
    freqs : ndarray
        frequency vector, size nf
    eigenvalues : ndarray
        eigenvalues array, size nf x nv
    eigenvectors : ndarray
        eigenvector matrix series, size nf x nv x nv
    sep : float
        frequency after which re-ordering is needed again.
        the code will try to find two discontinuities: one before sep, 
        and one after sep.

    Returns
    -------
    i_min_1 : int
        Frequency index of first discontinuity
    i_min_2 : int
        Frequency index of second discontinuity
    eigenvalues_new : ndarray
        Re-ordered eigenvalues
    eigenvectors_new : ndarray
        Re-ordered eigenvectors

    """
    # Get the index of the separation frequency
    i_sep = np.argmin(np.abs(freqs - sep))
    eigenvalues_new = np.copy(eigenvalues)
    eigenvectors_new = np.copy(eigenvectors)
    # Compute the difference between eigenvalues
    diff = eigenvalues[:, 0].real - eigenvalues[:, 3].real
    # Locate the turning points (index of the difference before it reaches zero)
    i_min_1 = np.argmin(diff[0:i_sep])
    i_min_2 = i_sep + np.argmin(diff[i_sep:])
    # Now flip the roles in-between
    for i in range(3):
        eigenvalues_new[i_min_1:i_min_2, i] = eigenvalues[i_min_1:i_min_2, i+3]
        eigenvalues_new[i_min_1:i_min_2, i+3] = eigenvalues[i_min_1:i_min_2, i]

        eigenvectors_new[i_min_1:i_min_2, :,
                         i] = eigenvectors[i_min_1:i_min_2, :, i+3]
        eigenvectors_new[i_min_1:i_min_2, :, i +
                         3] = eigenvectors[i_min_1:i_min_2, :, i]

    return i_min_1, i_min_2, eigenvalues_new, eigenvectors_new


def reformat_chains(chains, keep):
    """Flatten MCMC chains from ptemcee.

    Parameters
    ----------
    chains : ndarray
        parameter sample chains, 
        size ntemps x nwalkers x nstep x ndim
    keep : int
        number of steps to keep in the falattened chain

    Returns
    -------
    ndarray
        flattened chain, size nwalkers*keep x ndim
    """

    _, nwalkers, _, ndim = np.shape(chains)

    chains_reshaped = np.reshape(chains[0, :, -keep:, :],
                                 (nwalkers*keep, ndim))

    return chains_reshaped
