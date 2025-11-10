import json
import pandas as pd
import os
import logging
from typing import List, Dict, Optional, Union
from scipy.stats import kendalltau
import time
import numpy as np
import sys 
from sklearn.metrics import mean_absolute_error
import pysaebm.utils as utils
from .mh import metropolis_hastings
from pyjpm.utils import convert_np_types
from .viz import save_heatmap, save_traceplot


def run_mpebm(
    data_file: str,
    output_dir: Optional[str]=None,
    partial_rankings:Optional[np.ndarray] = np.array([]),
    bm2int: Optional[Dict[str, int]] = dict(), 
    mp_method:Optional[str] = None,
    output_folder: Optional[str] = None,
    n_iter: int = 2000,
    n_shuffle: int = 2,
    burn_in: int = 500,
    thinning: int = 1,
    true_order_dict: Optional[Dict[str, int]] = None,
    true_stages: Optional[List[int]] = None,
    fname_prefix: Optional[str] = "",
    # Strength of the prior belief in prior estimate of the mean (μ), set to 1 as default
    prior_n: float = 1.0,
    # Prior degrees of freedom, influencing the certainty of prior estimate of the variance (σ²), set to 1 as default
    prior_v: float = 1.0,
    seed: int = 123,
    save_results:bool=True,
    save_plots:bool=False,
    mallows_temperature:float=1.0,
):
    """
    Run the metropolis hastings algorithm and save results 

    Args:
        algorithm (str): Choose from 'hard_kmeans', 'mle', 'em', 'kde', and 'conjugate_priors' (default).
        data_file (str): Path to the input CSV file with biomarker data.
        output_dir (str): Path to the directory to store all the results.
        output_folder (str): Optional. If not provided, all results will be saved to output_dir/algorithm. 
            If provided, results will be saved to output_dir/output_folder
        n_iter (int): Number of iterations for the Metropolis-Hastings algorithm.
        n_shuffle (int): Number of shuffles per iteration.
        burn_in (int): Burn-in period for the MCMC chain.
        thinning (int): Thinning interval for the MCMC chain.
        true_order_dict (Optional[Dict[str, int]]): biomarker name: the correct order of it (if known)
        true_stages (Optional[List[int]]): true stages for all participants (if known)
        plot_title_detail (Optional[str]): optional string to add to plot title, as suffix.
        fname_prefix (Optional[str]): the prefix of heatmap, traceplot, results.json, and logs file, e.g., 5_50_0_heatmap_conjugate_priors.png
            In the example, there are no prefix strings. 
        skip_heatmap (Optional[bool]): whether to save heatmaps. True you want to skip saving heatmaps and save space.
        skip_traceplot (Optional[bool]): whether to save traceplots. True if you want to skip saving traceplots and save space.
        prior_n (strength of belief in prior of mean): default to be 1.0
        prior_v (prior degree of freedom) are the weakly informative priors, default to be 1.0
        bw_method (str): bandwidth selection method in kde
        seed (int): for reproducibility

    Returns:
        Dict[str, Union[str, int, float, Dict, List]]: Results including everything, e.g., Kendall's tau and p-value.
    """
    start_time = time.time()

    # Initialize random number generator
    rng = np.random.default_rng(seed)

    if save_results:
        # Folder to save all outputs
        if output_folder:
            output_dir = os.path.join(output_dir, output_folder)
        else:
            output_dir = os.path.join(output_dir)
    fname = utils.extract_fname(data_file)

    # First do cleanup
    logging.info(f"Starting cleanup ...")
    utils.cleanup_old_files(output_dir, fname)

    if save_results:

        # Then create directories
        os.makedirs(output_dir, exist_ok=True)
        results_folder = os.path.join(output_dir, "results")
        os.makedirs(results_folder, exist_ok=True)
     
        # Finally set up logging (console only, no file)
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[logging.StreamHandler(sys.stdout)],
            force=True
        )

    # Log the start of the run
    logging.info(f"Running {fname}")
    logging.getLogger().handlers[0].flush()  # Flush logs immediately

    # Load data
    try:
        data = pd.read_csv(data_file)
    except Exception as e:
        logging.error(f"Error reading data file: {e}")
        raise

    # sort biomarkeres by name, ascending
    # This is the order appearing in data_matrix
    biomarker_names = np.array(sorted(data.biomarker.unique()))
    # biomarkers_int will be corresponding IDs, in the order of data_matrix below. 
    # This is very important 
    biomarkers_int = np.array([])
    if len(partial_rankings)>0:
        # convert biomarker names in string to intergers, according to the str2int mapper
        biomarkers_int = np.array([bm2int[x] for x in biomarker_names])
    n_biomarkers = len(biomarker_names)
    logging.info(f"Number of biomarkers: {n_biomarkers}")

    n_participants = len(data.participant.unique())

    df = data.copy()
    diseased_dict = dict(zip(df.participant, df.diseased))
    dff = df.pivot(
        index='participant', columns='biomarker', values='measurement')
    # make sure the data_matrix is in this order
    dff = dff.reindex(columns=biomarker_names, level=1) 
    # remove column name (biomarker) to clean display
    dff.columns.name = None      
    # bring 'participant' back as a column and then delete it
    dff.reset_index(inplace=True, drop=True)  
    data_matrix = dff.to_numpy()
    diseased_arr = np.array([int(diseased_dict[x]) for x in range(n_participants)])

    # Run the Metropolis-Hastings algorithm
    try:
        all_orders, all_loglikes, best_order, best_log_likelihood, best_theta_phi = metropolis_hastings(
            partial_rankings=partial_rankings, mp_method=mp_method, 
            data_matrix=data_matrix, diseased_arr=diseased_arr, biomarkers_int=biomarkers_int,
            iterations = n_iter, n_shuffle = n_shuffle, prior_n=prior_n, prior_v=prior_v, rng=rng, 
            mallows_temperature = mallows_temperature, burn_in=burn_in,
        )
    except Exception as e:
        logging.error(f"Error in Metropolis-Hastings algorithm: {e}")
        raise

    if save_plots:
        heatmap_folder = os.path.join(output_dir, "heatmaps")
        os.makedirs(heatmap_folder, exist_ok=True)
        traceplot_folder = os.path.join(output_dir, "traceplots")
        os.makedirs(traceplot_folder, exist_ok=True)


        try:
            save_traceplot(
                all_loglikes,
                folder_name=traceplot_folder,
                file_name=f"{fname_prefix}{fname}_traceplot",
                title=f"Traceplot of Log Likelihoods"
            )
        except Exception as e:
            logging.error(f"Error generating trace plot: {e}")
            raise

        try:
            save_heatmap(
                all_orders,
                burn_in,
                thinning,
                folder_name=heatmap_folder,
                file_name=f"{fname_prefix}{fname}_heatmap",
                title=f"Ordering Result",
                biomarker_names=biomarker_names,
                best_order=best_order
            )
        except Exception as e:
            logging.error(f"Error generating heatmap: {e}")
            raise

    # Get the order associated with the highet log likelihoods
    tau = None 
    mae = None
    if true_order_dict:
        # Sort both dicts by the key to make sure they are comparable
        # because the best order is the indices of the biomarkers in the order of sorted(true_order_dict.items())
        true_order_dict = dict(sorted(true_order_dict.items()))
        true_order_indices = np.array(list(true_order_dict.values())) 
        tau, _ = kendalltau(best_order, true_order_indices)
        tau = (1-tau)/2

    if save_results:
        _, ml_stages, _ = utils.stage_with_plugin_pi_em(
            data_matrix=data_matrix,
            order_with_highest_ll=best_order, # no need to + 1 because in pympebm, the order starts from 1 already. 
            # this in fact is more okay, because current_order, the ordering index always starts from 1. 
            # in inference with label, the disease stages, or stage_post, has n_biomarker diseases starting from 1
            # but in blind inference, we have n_stages, starting from 0. 
            final_theta_phi=best_theta_phi,
            rng=rng,
            max_iter=200,
            tol=1e-6
        )
        if true_stages:
            # mae_sampling = mean_absolute_error(true_stages, ml_stages_sampling)
            mae = mean_absolute_error(true_stages, ml_stages)

        end_time = time.time()

        results = {
            "runtime": end_time - start_time,
            "max_log_likelihood": best_log_likelihood,
            "kendalls_tau": tau,
            "mean_absolute_error": mae,
            "order_with_highest_ll": {k: int(v) for k, v in zip(biomarker_names, best_order)}
        }
        # Save results
        try:
            with open(f"{results_folder}/{fname_prefix}{fname}_results.json", "w") as f:
                json.dump(convert_np_types(results), f, indent=4)
        except Exception as e:
            logging.error(f"Error writing results to file: {e}")
            raise
        logging.info(f"Results saved to {results_folder}/{fname_prefix}{fname}_results.json")

        return best_order, results 
    else:     
        order_dict = {k: int(v) for k, v in zip(biomarker_names, best_order)}

        return best_order, order_dict