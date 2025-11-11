# -*- coding: utf-8 -*-
# Author: Quentin Baghi 2021 <quentin.baghi@protonmail.com>
"""
Refactoring of ptemcee to allow to save data along progress
"""
import ptemcee
import logging
import pickle
import numpy as np
logger = logging.getLogger(__name__)


class Sampler(ptemcee.Sampler):

    def __init__(self, output_dir, nwalkers, ndim, logl, logp, **kwargs):

        super().__init__(nwalkers, ndim, logl, logp, **kwargs)

        self.output_dir = output_dir
        self.ndim = ndim

    def run_and_save(self, p0, nit, thin, n_save, n_verbose, storechain=False,
                     chain_suffix="chains.p",
                     logl_suffix="logl.p",
                     logp_suffix="logp.p"):

        # Initialize parameter state
        pos = p0[:]
        # Initialize iteration counter
        i = 0
        isave = 0

        # Initialize saving files
        file_chain = open(self.output_dir + "/" + chain_suffix, "wb")
        file_logl = open(self.output_dir + "/" + logl_suffix, "wb")
        file_logp = open(self.output_dir + "/" + logp_suffix, "wb")

        # Block of chain to be saved
        nsize = np.min([n_save, nit])
        chain_save = np.zeros((self.ntemps, self.nwalkers, nsize, self.ndim))
        logl_save = np.zeros((self.ntemps, self.nwalkers, nsize))
        logp_save = np.zeros((self.ntemps, self.nwalkers, nsize))

        for pstate, lnlike0, lnprob0 in self.sample(pos, nit, thin=thin, storechain=storechain):

            # Enter the iteration
            i += 1
            isave += 1
            # Store data
            chain_save[:, :, isave-1, :] = pstate
            logl_save[:, :, isave-1] = lnlike0
            logp_save[:, :, isave-1] = lnprob0

            if ((i % n_save == 0) & (i != 0) & (i != 1)) | (i == nit):
                # If the number of iterations in a multiple of n_save
                logger.info("Save data at iteration " + str(i) + "...")
                # The number of saved iterations at iteration i is
                # saved_it = i // thin
                # ------Samples---------
                pickle.dump(chain_save, file_chain)
                # ------Log likelihood---------
                pickle.dump(logl_save, file_logl)
                # ------Log prior---------
                pickle.dump(logp_save, file_logp)
                logging.info("Data saved.")
                # Update the number of samples saved
                isave += nsize
                # Once data is saved, re-initialize the arrays
                nsize = np.min([n_save, nit-i])
                chain_save = np.zeros((self.ntemps, self.nwalkers, nsize, self.ndim))
                logl_save = np.zeros((self.ntemps, self.nwalkers, nsize))
                logp_save = np.zeros((self.ntemps, self.nwalkers, nsize))
                # Set the saving counter to zero
                isave = 0

            if i % n_verbose == 0:
                logger.info("Iteration " + str(i) + " completed.")

        # Closing the saving filesrr
        file_chain.close()
        file_logl.close()
        file_logp.close()
