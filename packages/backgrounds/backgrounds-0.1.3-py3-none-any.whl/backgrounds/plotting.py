# -*- coding: utf-8 -*-
# Author: Quentin Baghi 2021 <quentin.baghi@protonmail.com>
import matplotlib as mpl
import numpy as np
import jax
import jax.numpy as jnp
from matplotlib import pyplot as plt
#from pyfftw.interfaces.numpy_fft import fft, ifft
from numpy.fft import fft, ifft
import matplotlib.colors as mc
import colorsys
from . import utils


def plotconfig(lbsize=17, lgsize=14, autolayout=True, figsize=[8, 6],
               ticklabelsize=16, fsize=15, fontfamily='STIXGeneral',
               tdir='in', major=10, minor=7, lwidth=2, lhandle=2.0,
               usetex=False, rcfonts=False, ticks_font_family='serif'):

 
    ticks_font = mpl.font_manager.FontProperties(family=ticks_font_family,
                                                 style='normal',
                                                 weight='normal',
                                                 stretch='normal',
                                                 size=lbsize)

    if fontfamily == 'STIXGeneral':
        mpl.rcParams['mathtext.fontset'] = 'stix'


    mpl.rcParams['text.usetex'] = usetex
    mpl.rcParams['pgf.rcfonts'] = usetex

    mpl.rcParams['font.family'] = fontfamily
    mpl.rcParams['figure.figsize'] = figsize[0], figsize[1]
    mpl.rcParams['figure.autolayout'] = autolayout
    mpl.rcParams['xtick.labelsize'] = ticklabelsize
    mpl.rcParams['ytick.labelsize'] = ticklabelsize
    plt.rcParams['font.size'] = fsize
    plt.rcParams['axes.linewidth'] = lwidth

    mpl.rcParams['axes.titlesize'] = lbsize
    mpl.rcParams['axes.labelsize'] = lbsize

    plt.rcParams['xtick.major.size'] = major
    plt.rcParams['xtick.minor.size'] = minor

    plt.rcParams['ytick.major.size'] = major
    plt.rcParams['ytick.minor.size'] = minor

    plt.rcParams['xtick.direction'] = tdir
    plt.rcParams['ytick.direction'] = tdir

    plt.rcParams['xtick.major.width'] = lwidth
    plt.rcParams['ytick.major.width'] = lwidth

    plt.rcParams['xtick.major.top'] = True
    plt.rcParams['xtick.minor.top'] = True
    plt.rcParams['ytick.major.right'] = True
    plt.rcParams['ytick.minor.right'] = True
    plt.rcParams['xtick.major.bottom'] = True
    plt.rcParams['xtick.minor.bottom'] = True
    plt.rcParams['ytick.major.left'] = True
    plt.rcParams['ytick.minor.left'] = True
    plt.rcParams['xtick.top'] = True    # draw ticks on the left side
    plt.rcParams['ytick.right'] = True   # draw ticks on the right side


def plotconfig_latex(fontsize=11.0, figsize=None, labelsize=17, ticklabelsize=16,
                     tickmajorsize=8, tickminorsize=6, tickminorwidth=1, tickmajorwidth=2):
    """Load matplotlib configuration for paper plots in latex.

    Parameters
    ----------
    fontsize : float, optional
        _description_, by default 11.0
    figsize : list, optional
        _description_, by default None
    labelsize : int, optional
        _description_, by default 17
    ticklabelsize : int, optional
        _description_, by default 16
    tickmajorsize : int, optional
        _description_, by default 10
    tickminorsize : int, optional
        _description_, by default 7
    """

    if figsize is None:
        figsize = [4.9, 3.5]

    mpl.rcParams["figure.figsize"] = figsize[0], figsize[1]
    mpl.rcParams["font.size"] = fontsize
    mpl.rcParams["font.family"] = "serif"
    # mpl.rcParams["font.serif"] = "Palatino"
    mpl.rcParams["axes.titlesize"] = "medium"
    mpl.rcParams["figure.titlesize"] = "medium"
    mpl.rcParams["text.usetex"] = True

    # Axes label sizes (x and y)
    mpl.rcParams['axes.labelsize'] = labelsize
    mpl.rcParams['axes.titlesize'] = labelsize
    # Axes ticks label sizes
    mpl.rcParams['xtick.labelsize'] = ticklabelsize
    mpl.rcParams['ytick.labelsize'] = ticklabelsize
    # Axes ticks sizes
    mpl.rcParams['xtick.major.size'] = tickmajorsize
    mpl.rcParams['xtick.minor.size'] = tickminorsize
    mpl.rcParams['ytick.major.size'] = tickmajorsize
    mpl.rcParams['ytick.minor.size'] = tickminorsize
    # Axes ticks widths
    mpl.rcParams['axes.linewidth'] = tickmajorwidth
    mpl.rcParams['xtick.major.width'] = tickmajorwidth
    mpl.rcParams['ytick.major.width'] = tickmajorwidth
    mpl.rcParams['xtick.minor.width'] = tickminorwidth
    mpl.rcParams['ytick.minor.width'] = tickminorwidth

    mpl.rcParams['xtick.major.top'] = True
    mpl.rcParams['xtick.minor.top'] = True
    mpl.rcParams['ytick.major.right'] = True
    mpl.rcParams['ytick.minor.right'] = True
    mpl.rcParams['xtick.major.bottom'] = True
    mpl.rcParams['xtick.minor.bottom'] = True
    mpl.rcParams['ytick.major.left'] = True
    mpl.rcParams['ytick.minor.left'] = True
    mpl.rcParams['xtick.top'] = True    # draw ticks on the left side
    mpl.rcParams['ytick.right'] = True   # draw ticks on the right side

    mpl.rcParams['xtick.direction'] = 'in'
    mpl.rcParams['ytick.direction'] = 'in'


def set_size(width=426.79135, fraction=1):
    """Set figure dimensions to avoid scaling in LaTeX.

    Parameters
    ----------
    width: float
            Document textwidth or columnwidth in pts
    fraction: float, optional
            Fraction of the width which you wish the figure to occupy

    Returns
    -------
    fig_dim: tuple
            Dimensions of figure in inches
    """
    # Width of figure (in pts)
    fig_width_pt = width * fraction

    # Convert from pt to inches
    inches_per_pt = 1 / 72.27

    # Golden ratio to set aesthetic figure height
    # https://disq.us/p/2940ij3
    golden_ratio = (5**.5 - 1) / 2

    # Figure width in inches
    fig_width_in = fig_width_pt * inches_per_pt
    # Figure height in inches
    fig_height_in = fig_width_in * golden_ratio

    fig_dim = (round(fig_width_in), round(fig_height_in))

    return fig_dim


def compute_periodogram(x, wd=None, fs=1.0):

    if wd is None:
        wd = np.hanning(x.shape[0])
    else:
        if type(wd) == str:
            if wd == 'hanning':
                wd = np.hanning(x.shape[0])
            elif wd == 'blackman':
                wd = np.blackman(x.shape[0])
            else:
                raise NotImplementedError("Window not implemented.")
        elif type(wd) == np.ndarray:
            pass
        else:
            TypeError("Window should be a string or an array")

    x_fft = fft(x * wd)
    k2 = np.sum(wd**2)

    return np.abs(x_fft) * np.sqrt(2 / (k2 * fs))


def lighten_color(color, amount=0.5):
    """
    Lightens the given color by multiplying (1-luminosity) by the given amount.
    Input can be matplotlib color string, hex string, or RGB tuple.

    Examples:
    >> lighten_color('g', 0.3)
    >> lighten_color('#F034A3', 0.6)
    >> lighten_color((.3,.55,.1), 0.5)
    """

    try:
        c = mc.cnames[color]
    except:
        c = color
    c = colorsys.rgb_to_hls(*mc.to_rgb(c))
    return colorsys.hls_to_rgb(c[0], 1 - amount * (1 - c[1]), c[2])


class SpectralAnalysis:

    def __init__(self, fs=1.0, freqs=None, units='',
                 xlabel=r"Frequency [Hz]",
                 ylabel=None):

        # Sampling frequency
        self.fs = fs
        # Vector of frequencies
        self.freqs = freqs
        # Dictionary of time series
        self.series = {}
        self.series_colors = {}
        self.series_linestyles = {}
        # Dictionary of one-sided PSDs
        self.psds = {}
        self.psds_colors = {}
        self.psds_linestyles = {}

        self.xlabel = xlabel
        if ylabel is None:
            self.ylabel = 'PSD [' + units + r'$\mathrm{Hz^{-1/2}}$]'
        else:
            self.ylabel = ylabel
        self.colors = ['k', 'tab:blue', 'brown', 'gray']

    def add_time_series(self, x, name, color=None, linestyle='solid'):

        self.series[name] = x
        self.series_colors[name] = color
        self.series_linestyles[name] = linestyle

    def add_psd(self, psd, name, color=None, linestyle='solid'):

        self.psds[name] = psd.real
        self.psds_colors[name] = color
        self.psds_linestyles[name] = linestyle

    def plot(self, series_names=None, psd_names=None, title=None,
             left=None, right=None, bottom=None, top=None, wd=None,
             periodogram_lw=1, psd_lw=2, savepath=None, dpi=150,
             show=False):

        fig1, ax1 = plt.subplots(nrows=1)
        key_list = list(self.series.keys())

        for j, key in enumerate(key_list):
            # Plot periodograms
            pj = compute_periodogram(
                self.series[key], wd=wd, fs=self.fs)
            freqs = np.fft.fftfreq(pj.shape[0]) * self.fs
            inds = np.where(freqs > 0)[0]
            ax1.plot(freqs[inds], pj[inds],
                     color=self.colors[j],
                     label=key,
                     linewidth=periodogram_lw,
                     linestyle='solid',
                     rasterized=False)

        if self.freqs is not None:
            freqs = self.freqs
        inds = np.where(freqs > 0)[0]
        key_list = list(self.psds.keys())

        for j, key in enumerate(key_list):
            # Plot theoretical PSD if any
            if key_list[j] in self.psds:
                # PSD color
                if self.psds_colors[key] is not None:
                    color = self.psds_colors[key]
                else:
                    color = lighten_color(self.colors[j], amount=0.5)
                ax1.plot(freqs[inds],
                         np.sqrt(self.psds[key][inds]),
                         color=color,
                         label=key,
                         linewidth=psd_lw,
                         linestyle=self.psds_linestyles[key],
                         rasterized=False)

        ax1.set_xscale('log')
        ax1.set_yscale('log')
        ax1.set_xlabel(self.xlabel, fontsize=16)
        ax1.set_ylabel(self.ylabel, fontsize=16)
        if left is None:
            ax1.set_xlim(left=freqs[1], right=self.fs/2)
        if (bottom is not None) | (top is not None):
            ax1.set_ylim(bottom=bottom, top=top)
        ax1.set_title(title)
        ax1.grid(which='both', axis='both', linestyle='dotted', linewidth=1)
        ax1.minorticks_on()
        ax1.grid(color='gray', linestyle='dotted')
        plt.legend()
        if savepath is not None:
            plt.savefig(savepath, dpi=dpi)
        if show:
            plt.show()
        return fig1, ax1


def plot_single_link_posteriors(noise_classes, chaint, sn_true, titles=None,
                                ylabels=None, ylabels_errors=None,
                                ndraws = 500, psd_prior_up=None, psd_prior_low=None):
    # Frequencies
    finds = noise_classes[0].freq

    # Localise the individual noise parameters in the full parameter vector
    ib = [0] # Start from the beginning of the vector
    ie = [noise_classes[0].ndim] # Until the dimension of the first noise model
    for i, noise_comp in enumerate(noise_classes): # Then for each additional component
        # Start from where we were at the last iteration
        ib.append(ie[i-1]) 
        # Add the dimension of the new noise model
        ie.append(ie[i-1] + noise_comp.ndim)

    if titles is None:
        titles = ["OMS noise", "TM noise"]
    if ylabels is None:
        ylabels = [r"$\sqrt{S_{\mathrm{OMS}}}$ [$\mathrm{Hz^{-1/2}}$]",
                r"$\sqrt{S_{\mathrm{TM}}}$ [$\mathrm{Hz^{-1/2}}$]"]
    if ylabels_errors is None:
        ylabels_errors = [r"$\delta S_{\mathrm{OMS}} / S_{\mathrm{OMS}}$",
                          r"$\delta S_{\mathrm{TM}} / S_{\mathrm{TM}}$"]
    # Plot the OMS PSD estimate
    for j in range(2):
        fig, ax = plt.subplots(nrows=2, ncols=1, figsize=(8, 6),
                            gridspec_kw={'height_ratios': [2, 1]})
        y_max = np.sqrt(np.max(np.abs(sn_true[:, j]))*10)
        y_min = np.sqrt(np.min(np.abs(sn_true[:, j]))/10)

        for i in range(ndraws):
            theta_n = chaint[i, ib[j]:ie[j]]
            ax[0].plot(finds, np.sqrt(np.abs(noise_classes[j].compute_link_psd(theta_n))),
                    alpha=0.6, color='tab:blue', linewidth=0.5)

            if i == 0:
                ax[0].plot(finds, np.sqrt(np.abs(noise_classes[j].compute_link_psd(theta_n))),
                        alpha=0.6, 
                        color='tab:blue',
                        linewidth=0.5,
                        label='Posterior')
        if (psd_prior_up is not None) & (psd_prior_low is not None):
            ax[0].fill_between(finds, 
                            y1=np.sqrt(psd_prior_up[j]), 
                            y2=np.sqrt(psd_prior_low[j]), 
                            alpha=0.4,
                            label="Prior",
                            color='gray')

        ax[0].plot(finds, np.sqrt(np.abs(sn_true[:, j])),
                label='True PSD', 
                color='tab:orange', linewidth=1, linestyle='dashed')

        ax[0].set_xscale('log')
        ax[0].set_yscale('log')
        ax[0].legend(loc='upper right', frameon=False, ncol=3)
        ax[0].set_ylabel(ylabels[j])
        ax[0].set_title(titles[j])
        ax[0].set_xlim([finds[0], finds[-1]])

        # ---------
        # Residuals
        # ---------
        ax[1].set_xlabel(r"Frequency [Hz]")
        ax[1].set_ylabel(ylabels_errors[j])
        ax[1].set_xlim([1e-4, finds[-1]])

        for i in range(ndraws):
            theta_n = chaint[i, j*noise_classes[j].ndim:(j+1)*noise_classes[j].ndim]
            sn_post = noise_classes[j].compute_link_psd(theta_n)
            err = (sn_post - sn_true[:, j]) / sn_true[:, j]
            ax[1].plot(finds, np.real(err),
                    linestyle='solid',
                    linewidth=0.5,
                    color='tab:blue')

        ax[1].set_xscale('log')
        plt.tight_layout()

    return fig, ax


class PredictivePosteriors:
    """
    Plot predictive posteriors from parameter chains and likelihood model.
    
    """

    def __init__(self, prior_samples, posterior_samples, noise_classes, signal_classes,
                 n_draws=300, cov_tdi_true=None,
                 k_sig=2, keys=None):
        """_summary_

        Parameters
        ----------
        prior_samples : ndarray, optional
            Prior samples from the MCMC chain, by default None
        posterior_samples : ndarray
            Posterior samples from the MCMC chain.
        noise_classes : list
            List of noise class objects.
        signal_classes : list
            List of signal class objects.
        n_draws : int, optional
            Number of draws from the posterior, by default 300
        cov_tdi_true : _type_, optional
            True total covariance, by default None
        k_sig : int, optional
            Number of standard deviations for credible intervals, by default 2
        keys : list, optional
            List of keys to use for the prior and posterior samples, by default None
        """

        if keys is None:
            keys = ["noise", "GW"]
        self.freqs = noise_classes[0].freq
        self.samples = posterior_samples[-n_draws:, :]
        self.noise_classes = noise_classes
        self.signal_classes = signal_classes
        self.n_draws = n_draws

        # For the priors
        # --------------

        # Prior samples
        # Dimension of the noise model parameter space
        ndim_n = sum([nc.ndim for nc in noise_classes])
        ndim_s = sum([sc.ndim for sc in signal_classes])
        ndim = ndim_n + ndim_s

        self.cov_function = {keys[0]: jax.jit(jax.vmap(self.compute_noise_covariance)),
                             keys[1]: jax.jit(jax.vmap(self.compute_signal_covariance))}
        self.theta_indices = {keys[0]: np.arange(ndim_n),
                              keys[1]: np.arange(ndim_n, ndim)}

        self.tdi_prior_psd_mean = {}
        self.tdi_prior_psd_var = {}
        self.tdi_prior_psd_up = {}
        self.tdi_prior_psd_low = {}

        self.tdi_posterior_psd_mean = {}
        self.tdi_posterior_psd_var = {}
        self.tdi_posterior_psd_up = {}
        self.tdi_posterior_psd_low = {}

        for key in keys:

            # For prior samples
            # =================

            # Compute the covariances in batch
            log_cov_tdi_samples = jnp.log(
                self.cov_function[key](prior_samples[:n_draws, self.theta_indices[key]]))
            # Compute prior mean deviation of noise in TDI domain
            log_cov_tdi_mean = jnp.mean(log_cov_tdi_samples, axis=0)
            # Compute prior standard deviation of noise in TDI domain
            log_cov_tdi_var = jnp.var(log_cov_tdi_samples, axis=0)
            # Delete covariance samples to free memory
            del log_cov_tdi_samples

            # Compute the prior mean and variance
            self.tdi_prior_psd_mean[key] = jnp.exp(jnp.asarray([log_cov_tdi_mean[..., i, i]
                                                            for i in range(3)])).T
            self.tdi_prior_psd_var[key] = jnp.asarray([log_cov_tdi_var[..., i, i]
                                                    for i in range(3)]).T
            # Compute prior credible intervals
            self.tdi_prior_psd_up[key] = jnp.exp(jnp.log(self.tdi_prior_psd_mean[key])
                                            + k_sig * jnp.sqrt(self.tdi_prior_psd_var[key]))
            self.tdi_prior_psd_low[key] = jnp.exp(jnp.log(self.tdi_prior_psd_mean[key])
                                                - k_sig * jnp.sqrt(self.tdi_prior_psd_var[key]))

            # For posterior samples
            # ====================

            # Compute the covariances in batch
            log_cov_tdi_samples = jnp.log(
                self.cov_function[key](posterior_samples[:n_draws, self.theta_indices[key]]))
            # Compute prior mean deviation of noise in TDI domain
            log_cov_tdi_mean = jnp.mean(log_cov_tdi_samples, axis=0)
            # Compute prior standard deviation of noise in TDI domain
            log_cov_tdi_var = jnp.var(log_cov_tdi_samples, axis=0)
            # Compute the posterior mean and variance
            self.tdi_posterior_psd_mean[key] = jnp.exp(jnp.asarray([log_cov_tdi_mean[..., i, i]
                                                            for i in range(3)])).T
            self.tdi_posterior_psd_var[key] = jnp.asarray([log_cov_tdi_var[..., i, i]
                                                    for i in range(3)]).T
            # Compute posterior credible intervals
            self.tdi_posterior_psd_up[key] = jnp.exp(jnp.log(self.tdi_posterior_psd_mean[key])
                                            + k_sig * jnp.sqrt(self.tdi_posterior_psd_var[key]))
            self.tdi_posterior_psd_low[key] = jnp.exp(jnp.log(self.tdi_posterior_psd_mean[key])
                                                - k_sig * jnp.sqrt(self.tdi_posterior_psd_var[key]))

        if cov_tdi_true is not None:
            # True TDI PSD
            self.tdi_psd_true = {key: np.asarray([cov_tdi_true[key][..., i, i] for i in range(3)]).T
                                 for key in keys}
        else:
            self.tdi_psd_true = None

    def compute_noise_covariance(self, theta_n):

        noise_dims = [nc.ndim for nc in self.noise_classes]

        theta_split = jnp.split(theta_n, np.cumsum(noise_dims)[:-1])

        cov_list = [nc.compute_covariances(ts) for nc, ts in zip(self.noise_classes, theta_split)]
        return jnp.sum(jnp.stack(cov_list), axis=0)

    def compute_signal_covariance(self, theta_s):

        signal_dims = [sc.ndim for sc in self.signal_classes]

        theta_split = jnp.split(theta_s, np.cumsum(signal_dims)[:-1])

        cov_list = [sc.compute_covariances(ts) for sc, ts in zip(self.signal_classes, theta_split)]

        return jnp.sum(jnp.stack(cov_list), axis=0)

    def plot(self, keys=["noise", "GW"], channels=["X"],
             colors_posterior={"noise": "tab:blue", 
                               "GW": "purple"},
             plot_type={"noise": "intervals", "GW": "draws"},
             colors_prior={"noise": "blue", "GW": "violet"},
             colors_true={"noise": "magenta", "GW": "black"},
             y_min = 1e-24, y_max = 1e-19, prior_on=True):

        figures = []
        axes = []

        for j_channel, channel in enumerate(channels):

            fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(8, 6))

            for key in keys:
                # Plot the prior credible intervals
                if prior_on:
                    ax.fill_between(self.freqs, 
                                    np.sqrt(np.abs(self.tdi_prior_psd_up[key][:, j_channel])),
                                    np.sqrt(np.abs(self.tdi_prior_psd_low[key][:, j_channel])),
                                    color=colors_prior[key],
                                    alpha=0.6,
                                label=key + ' prior')

                # Plot the posteriors
                if plot_type[key] == "intervals":
                    ax.fill_between(self.freqs,
                                    np.sqrt(np.abs(self.tdi_posterior_psd_up[key][:, j_channel])),
                                    np.sqrt(np.abs(self.tdi_posterior_psd_low[key][:, j_channel])),
                                    color=colors_posterior[key],
                                    alpha=0.6,
                                    label=key + ' posterior')
                elif plot_type[key] == "draws":
                    # Evaluate covariance samples in batch
                    cov_samples = self.cov_function[key](self.samples[:self.n_draws,
                                                                      self.theta_indices[key]])
                    for i in range(self.n_draws):
                        cov = cov_samples[i]
                        if i==0:
                            label = key + ' posterior'
                        else:
                            label = None
                        ax.plot(self.freqs, np.sqrt(np.abs(cov[:, j_channel, j_channel])),
                                linestyle='solid',
                                alpha=0.6,
                                color=colors_posterior[key],
                                label=label,
                                linewidth=1)
                        
                # Plot the true PSD if any
                if self.tdi_psd_true is not None:
                    ax.plot(self.freqs, np.sqrt(np.abs(self.tdi_psd_true[key][:, j_channel])),
                            linestyle='dashed',
                            label='True '+key+' PSD',
                            color=colors_true[key],
                            linewidth=2)

                ax.set_xscale('log')
                ax.set_yscale('log')
                ax.legend(loc='upper left', ncol=2, frameon=False, prop={'size': 14})
                ax.set_ylabel(r"$\sqrt{\mathrm{PSD}}$ [$\mathrm{Hz^{-1/2}}$]")
                ax.set_title("TDI " + channel)
                ax.set_xlabel(r"Frequency [Hz]")
                ax.set_xlim([self.freqs[0], self.freqs[-1]])
                ax.set_ylim([y_min, y_max])

            figures.append(fig)
            axes.append(ax)

        return figures, axes
