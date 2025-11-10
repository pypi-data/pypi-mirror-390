import numpy as np
import pyjpm.utils as utils 
from typing import Tuple, List
import logging
import pyjpm.mp_utils as mp_utils

def metropolis_hastings(
        partial_rankings: np.ndarray,
        mp_method: str,
        data_matrix: np.ndarray,
        diseased_arr: np.ndarray,
        biomarkers_int:np.ndarray,
        iterations: int,
        n_shuffle: int,
        prior_n: float,
        prior_v: float,
        mallows_temperature:float,
        burn_in:int,
        rng: np.random.Generator,
) -> Tuple:
    """Implement metroplis hastings MCMC algorithm
    
    """
    if len(partial_rankings) > 0:
        logging.info(
                f"Now using {mp_method}"
            )
        allowed_mp_method = {'PL', 'Mallows_Tau', 'Mallows_RMJ' ,'Pairwise', 'BT'}
        assert mp_method in allowed_mp_method, f'mp_method must be chosen from {allowed_mp_method}!'
        
        # no need to sample, so there is no need to use mcmc_iterations, sample_count, pl_best
        if mp_method == 'PL':
            sampler = mp_utils.PlackettLuce(ordering_array=partial_rankings, rng=rng)
        else:
            sampler = mp_utils.MCMC(
                ordering_array=partial_rankings, 
                rng=rng, method=mp_method, 
                n_shuffle=n_shuffle,
                mallows_temperature=mallows_temperature)
            
    n_participants, n_biomarkers = data_matrix.shape

    # Validate input
    if n_shuffle <= 1:
        raise ValueError("n_shuffle must be >= 2 or =0")
    if n_shuffle > n_biomarkers:
        raise ValueError("n_shuffle cannot exceed n_biomarkers")

    n_stages = n_biomarkers + 1
    disease_stages = np.arange(start=1, stop=n_stages, step=1)
    n_disease_stages = n_stages - 1
    non_diseased_ids = np.where(diseased_arr == 0)[0]
    diseased_ids = np.where(diseased_arr == 1)[0]

    # N * 4 matrix, cols: theta_mean, theta_std, phi_mean, phi_std
    theta_phi_default = utils.get_initial_theta_phi_estimates(
        data_matrix, non_diseased_ids, diseased_ids, prior_n, prior_v, rng=rng)

    current_theta_phi = theta_phi_default.copy()

    # initialize an ordering and likelihood
    # Imagine this: the array of biomarker_int stays intact. 
    # we are randomizing the indices of each of them in the new order
    current_order = rng.permutation(np.arange(1, n_stages))
    current_ln_likelihood = -np.inf
    alpha_prior = [1.0] * (n_disease_stages)
    # current_pi is the prior distribution of N disease stages.
    # Sample from uniform dirichlet dist.
    # Notice that the index starts from zero here. 
    current_pi = rng.dirichlet(alpha_prior)
    # Only for diseased participants
    # current_stage_post = np.zeros((n_participants, n_disease_stages))
    acceptance_count = 0

    best_order = current_order.copy()
    best_theta_phi = current_theta_phi.copy()
    best_log_likelihood = current_ln_likelihood

    all_accepted_orders = np.zeros((iterations, n_biomarkers), dtype=np.int64)
    # This records all log likelihoods
    log_likelihoods = np.zeros(iterations, dtype=np.float64)

    for iteration in range(iterations):
        random_state = rng.integers(0, 2**32 - 1)

        new_order = current_order.copy()
        # utils.shuffle_adjacent(current_order, rng)
        utils.shuffle_order(new_order, n_shuffle, rng)

        """
        When we propose a new ordering, we want to calculate the total ln likelihood, which is 
        dependent on theta_phi_estimates, which are dependent on biomarker_data and stage_likelihoods_posterior,
        both of which are dependent on the ordering. 

        Therefore, we need to update participant_data, biomarker_data, stage_likelihoods_posterior
        and theta_phi_estimates before we can calculate the total ln likelihood associated with the new ordering
        """

        """
        update theta_phi_estimates
        """

        # --- Compute stage posteriors with OLD θ/φ ---
        _, stage_post_old = utils.compute_total_ln_likelihood_and_stage_likelihoods(
            n_participants, data_matrix, new_order, non_diseased_ids, 
            current_theta_phi, current_pi, disease_stages
        )

        # Compute the new theta_phi_estimates based on new_order
        new_theta_phi = utils.update_theta_phi_estimates(
            n_biomarkers,
            data_matrix,
            new_order,
            current_theta_phi,  # Current state’s θ/φ
            stage_post_old,
            disease_stages,
            prior_n,    # Weak prior (not data-dependent)
            prior_v,     # Weak prior (not data-dependent)
        )

        # Recompute new_ln_likelihood using the new theta_phi_estimates
        new_ln_likelihood, stage_post_new = utils.compute_total_ln_likelihood_and_stage_likelihoods(
            n_participants, data_matrix, new_order, non_diseased_ids, new_theta_phi, current_pi, disease_stages
        )
        new_energy = 0.0
        if len(partial_rankings) > 0:
            new_energy = sampler.get_energy(biomarkers_int[np.argsort(new_order)])
            new_ln_likelihood -= new_energy
        # Compute acceptance probability
        delta = new_ln_likelihood - current_ln_likelihood
        prob_accept = 1.0 if delta > 0 else np.exp(delta)

        # Accept or reject the new state
        if rng.random() < prob_accept:
            current_order = new_order
            current_ln_likelihood = new_ln_likelihood
            # stage post exists only to update the stage prior (current_pi), so it's an intermediate variable
            # current_stage_post = stage_post_new
            current_theta_phi = new_theta_phi
            acceptance_count += 1

            # for each column, get the sum of all rows; output is a vector of stage_post_new.shape[1]
            stage_counts = stage_post_new[diseased_ids].sum(axis=0)  # soft counts
            current_pi = rng.dirichlet(alpha_prior + stage_counts)

            # stage_counts = np.zeros(n_disease_stages)
            # # participant, array of stage likelihoods
            # for p in range(n_participants):
            #     stage_probs = stage_post_new[p]
            #     stage_counts += stage_probs  # Soft counts
            # current_pi = rng.dirichlet(alpha_prior + stage_counts)

            if current_ln_likelihood > best_log_likelihood:
                best_log_likelihood = current_ln_likelihood
                best_order = current_order.copy()
                best_theta_phi = current_theta_phi.copy()

        all_accepted_orders[iteration] = current_order.copy()
        log_likelihoods[iteration] = current_ln_likelihood

        # Log progress
        if (iteration + 1) % max(10, iterations // 10) == 0:
            acceptance_ratio = 100 * acceptance_count / (iteration + 1)
            msg = (
                f"Iteration {iteration + 1}/{iterations}, "
                f"Acceptance Ratio: {acceptance_ratio:.2f}%, "
                f"Log Likelihood: {current_ln_likelihood:.4f}"
            )

            if mp_method:
                msg += f", New Energy: {new_energy:.4f}"

            logging.info(msg)


    return all_accepted_orders, log_likelihoods, best_order, best_log_likelihood, best_theta_phi