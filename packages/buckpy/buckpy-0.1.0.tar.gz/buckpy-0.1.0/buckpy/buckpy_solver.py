"""
This module contains the solver functions of BuckPy.
"""

import time
from multiprocess import Process, Queue, cpu_count
import numpy as np
import pandas as pd
from numba import jit
from .buckpy_variables import *

def exec_buckpy(fric_sampling, np_distr, np_scen, np_ends, n_sim, bl_verbose = False):

    """
    Execute buckpy methodology

    Parameters
    ----------
    fric_sampling : int
        Switch to select the sampling method of the lateral friction: 0 for 'per Element'
        or 1 'per OOS Reference Length'
    np_distr : numpy.ndarray
        3-D array describing the stochastic distributions:
        - dim 1: properties
        - dim 2: elements
        - dim 3: values
    np_scen : numpy.ndarray
        Array containing the pipeline desing data on assessed mesh.
    np_ends : numpy.ndarray
        Array containing information about the boundary conditions at the ends of the pipeline.
    n_sim : int
        Number of Monte-Carlo simulations to be run.

    Returns
    -------
    df_pp_plot : DataFrame
        Definition on assessed mesh of CBF and EAF in different conditions
        for case to plot. 
    df_VAP_plot : DataFrame
        Definition of virtual anchor points for case to plot.
    df_pp_buckle_prop : DataFrame
        Results for all buckles triggered.

    Other Parameters
    ----------------
    bl_verbose : boolean, optional
        True if intermediate printouts are required (False by default).
    """

    # Starting time of the solver module
    start_time = time.time()

    # Run deterministic case
    if bl_verbose:
        print("2. Run the deterministic case")
    np_prob_var_det = np.empty(0)
    np_case_det = preprocess_case(np_prob_var_det, np_scen, np_ends, bl_det = True)
    np_pp_buckle_det, np_case_det_updated, vap_list_det = solve_case(np_scen, np_case_det)

    # To be discussed: This block has been replaced to enable a like to like comparison with
    # Buckfast.

    # # Print-out force profiles for graphical display
    # # (Deterministic case if it buckles, or otherwise first random case that buckles)
    # np_pp_plot = np.empty((9, np_scen[KP].size))
    # vap_list = []
    # df_VAP_plot = pd.DataFrame(vap_list, columns = ['ielt VAP', 'KP VAP', 'ESF VAP'])
    # n_buckle = np_pp_buckle_det.shape[0]
    # if n_buckle > 0: # Deterministic case buckled
    #     for i_buckle in range(n_buckle):
    #         np_pp_buckle_det[i_buckle, SIM_PP] = 1
    #     np_pp_plot[P_KP] = np_scen[KP]
    #     np_pp_plot[P_CBF_HT] = np_case_det[CBF_HT]
    #     np_pp_plot[P_CBF_OP] = np_case_det[CBF_OP]
    #     np_pp_plot[P_EAF_INST] = np_case_det[EAF_INST]
    #     np_pp_plot[P_EAF_HT] = np_case_det_updated[EAF_HT]
    #     np_pp_plot[P_EAF_P_OP] = np_case_det_updated[EAF_P_OP]
    #     np_pp_plot[P_EAF_OP] = np_case_det_updated[EAF_OP]
    #     np_pp_plot[P_EAF_OP_UNBUCK] = np_case_det[EAF_OP_UNBUCK]
    #     df_VAP_plot = pd.DataFrame(vap_list_det, columns = ['ielt VAP', 'KP VAP', 'ESF VAP'])
    #     print('   The deterministic case has buckled')
    #     if bl_verbose:
    #         print(f'   Time taken to run the deterministic case: {time.time()-start_time:.1f}s')

    # # If there is no buckling on deterministic case then for result display
    # # generate a random case until buckling is triggered (max iteration<n_sim)
    # else:
    #     for i_sim in range(n_sim):
    #         np_prob_var = sample_randomness_case(fric_sampling, np_distr, np_scen)
    #         np_case = preprocess_case(np_prob_var, np_scen, np_ends, bl_det = False)
    #         np_pp_buckle, np_case_updated, vap_list = solve_case(np_scen, np_case)
    #         n_buckle = np_pp_buckle.shape[0]
    #         if n_buckle > 0: # Found random case buckling
    #             for i_buckle in range(n_buckle):
    #                 np_pp_buckle[i_buckle, SIM_PP] = i_sim
    #             np_pp_plot[P_KP] = np_scen[KP]
    #             np_pp_plot[P_CBF_HT] = np_case[CBF_HT]
    #             np_pp_plot[P_CBF_OP] = np_case[CBF_OP]
    #             np_pp_plot[P_EAF_INST] = np_case[EAF_INST]
    #             np_pp_plot[P_EAF_HT] = np_case_updated[EAF_HT]
    #             np_pp_plot[P_EAF_P_OP] = np_case_updated[EAF_P_OP]
    #             np_pp_plot[P_EAF_OP] = np_case_updated[EAF_OP]
    #             np_pp_plot[P_EAF_OP_UNBUCK] = np_case[EAF_OP_UNBUCK]
    #             #
    #             df_VAP_plot = pd.DataFrame(vap_list, columns = ['ielt VAP', 'KP VAP', 'ESF VAP'])
    #             print(f'   The random case {i_sim} has buckled')
    #             break

    # Print-out force profiles for graphical display (deterministic simulation only)
    np_pp_plot = np.empty((9, np_scen[KP].size))
    vap_list = []
    df_VAP_plot = pd.DataFrame(vap_list, columns = ['ielt VAP', 'KP VAP', 'ESF VAP'])
    n_buckle = np_pp_buckle_det.shape[0]
    for i_buckle in range(n_buckle):
        np_pp_buckle_det[i_buckle, SIM_PP] = 1
    np_pp_plot[P_KP] = np_scen[KP]
    np_pp_plot[P_CBF_HT] = np_case_det[CBF_HT]
    np_pp_plot[P_CBF_OP] = np_case_det[CBF_OP]
    np_pp_plot[P_EAF_INST] = np_case_det[EAF_INST]
    np_pp_plot[P_EAF_HT] = np_case_det_updated[EAF_HT]
    np_pp_plot[P_EAF_P_OP] = np_case_det_updated[EAF_P_OP]
    np_pp_plot[P_EAF_OP] = np_case_det_updated[EAF_OP]
    np_pp_plot[P_EAF_OP_UNBUCK] = np_case_det[EAF_OP_UNBUCK]
    df_VAP_plot = pd.DataFrame(vap_list_det, columns = ['ielt VAP', 'KP VAP', 'ESF VAP'])
    print('   The deterministic case has buckled')
    if bl_verbose:
        print(f'   Time taken to run the deterministic case: {time.time()-start_time:.1f}s')

    # Run Monte-Carlo loop
    if bl_verbose:
        print("3. Run the Monte-Carlo loop")
        start_time = time.time()
    if n_sim <= 10000:
        N_WORKER = 1
    else:
        N_WORKER = cpu_count()
    list_buckle_prop = run_monte_carlo(N_WORKER, n_sim, np_distr, np_scen,
                                       np_ends, fric_sampling, bl_verbose = bl_verbose)
    if bl_verbose:
        print(f'   Time taken to extract {len(list_buckle_prop)}'
              f' simulations: {time.time()-start_time:.1f}s')

    # Post-process 'df_pp_buckle_prop' and 'df_pp_buckle_prop'
    column_list = ['isim', 'KP', 'route_type', 'muax', 'mulat_op', 'HOOS', 'CBF_op', 'VAS_op']
    df_pp_buckle_prop = pd.DataFrame(np.concatenate(list_buckle_prop), columns = column_list)
    column_list = ['KP', 'CBF_ht', 'CBF_op', 'EAF_inst', 'EAF_ht',
                   'EAF_p_op','EAF_op', 'beta2', 'EAF_op_unbuck']
    df_pp_plot = pd.DataFrame(np.transpose(np_pp_plot), columns = column_list)

    return df_pp_plot, df_VAP_plot, df_pp_buckle_prop

@jit(nopython=True)
def sample_randomness_case(fric_sampling, np_distr, np_scen):

    """
    Samples the stochastic variables (HOOS and friction factors).

    Parameters
    ----------
    fric_sampling : int
        Switch to select the sampling method of the lateral friction: 0 for 'per Element'
        or 1 'per OOS Reference Length'
    np_distr : numpy.ndarray
        3-D array describing the stochastic distributions: Dim 1 = Properties, Dim 2 = Elements and
        Dim 3 = values
    np_scen : numpy.ndarray
        Array containing the pipeline desing data on assessed mesh.

    Returns
    -------
    np_prob_var : numpy.ndarray
        Definition of probabilistic variables on assessed mesh.
        Rows correspond to properties: MUAX = 0, MULAT_HT = 1, MULAT_OP = 2, HOOS = 3

    Notes
    -----
    The returned `np_prob_var` has values by columns corresponding to mesh elements
    over 4 rows corresponding to properties defined above.
    
        | MUAX: Axial friction coefficient
        | MULAT_HT: Lateral friction coefficient for Hydrotest condition
        | MULAT_OP: Lateral friction coefficient for Operation condition
        | HOOS: Soil property indicator

    """

    # Number of elements in the assessed mesh
    n_elts = np_scen[KP].size
    # Initialize the array to store probabilistic variables
    np_prob_var = np.empty((4, n_elts))

    # Sample axial friction coefficient
    muax_rand = np.random.rand()

    # Sample lateral friction coefficient
    if fric_sampling == 0: # Sample per element
        mul_rand = np.random.rand(n_elts)  
    elif fric_sampling == 1: # Sample per OOS Reference Length
        mul_rand = np.full(n_elts, np.random.rand())
        for i in range(2, int(np.amax(np_scen[SECTION_ID])) + 1):
            mul_rand[np_scen[SECTION_ID] == i] = np.random.rand()

    # Sample HOOS factor
    hoos_rand = np.random.rand(n_elts)

    # Interpolate sampled values based on CDF arrays to get probabilistic variables
    for i in range(n_elts):
        np_prob_var[MUAX, i] = np.interp(
            muax_rand, np_distr[MUAX_CDF_ARRAY][i], np_distr[MUAX_ARRAY][i])
        np_prob_var[MULAT_HT, i] = np.interp(
            mul_rand[i], np_distr[MULAT_CDF_ARRAY_HT][i], np_distr[MULAT_ARRAY_HT][i])
        np_prob_var[MULAT_OP, i] = np.interp(
            mul_rand[i], np_distr[MULAT_CDF_ARRAY_OP][i], np_distr[MULAT_ARRAY_OP][i])
        np_prob_var[HOOS, i] = np.interp(
            hoos_rand[i], np_distr[HOOS_CDF_ARRAY][i], np_distr[HOOS_ARRAY][i])

    return np_prob_var

def preprocess_case(np_prob_var, np_scen, np_ends, bl_det = False):

    """
    Preprocess case based on scenario definition and probabilistic variables.

    Parameters
    ----------
    np_prob_var : numpy.ndarray
        Array containing probabilistic variables for case processing.
    np_scen : numpy.ndarray
        Array containing scenario-specific data.
    np_ends : numpy.ndarray
        Array containing information about the boundary conditions at the ends of the pipeline.
    bl_det : bool, optional
        True if variables are set to their mean values.
        False if variables are sampled randomly (default).

    Returns
    -------
    np_case : numpy.ndarray
        2D array containing processed case-specific data.

    Notes
    -----
    This function preprocesses case-specific data for friction force calculation. It calculates
    various forces based on scenario and boundary condition data, and builds up frictional
    effective forces for different phases and conditions.

    Returned np_case has values by columns corresponding to mesh elements over 21 rowscorresponding
    to properties defined below:
        | MUAX = 0
        | MULAT_HT = 1
        | MULAT_OP = 2
        | HOOS = 3
        | CBF_HT = 4
        | CBF_OP = 5
        | LFF_INST = 6
        | LFF_HT = 7
        | LFF_OP = 8
        | RFF_INST = 9
        | RFF_HT = 10
        | RFF_OP = 11
        | EAF_INST = 12
        | EAF_HT = 13
        | EAF_P_OP = 14
        | EAF_OP = 15
        | EAF_OP_UNBUCK = 16
        | LDELTAF_HT	=	17
        | RDELTAF_HT	=	18
        | LDELTAF_OP	=	19
        | RDELTAF_OP	=	20

    """

    # Extracting the number of elements from the scenario array
    n_elts = np_scen[KP].size

    # Creating an empty array to store processed case-specific data
    np_case = np.empty((21, np_scen.shape[1]))

    if bl_det: # Alocating mean values to probabilistic variables
        np_case[MUAX] = np_scen[MUAX_MEAN]
        np_case[MULAT_HT] = np_scen[MULAT_HT_MEAN]
        np_case[MULAT_OP] = np_scen[MULAT_OP_MEAN]
        np_case[HOOS] = np.where(np_scen[ROUTE_TYPE] < 4, np_scen[HOOS_MEAN], np_scen[CBF_RCM])
            
    else: # Copying probabilistic variables to the case array
        np_case[MUAX] = np_prob_var[MUAX]
        np_case[MULAT_HT] = np_prob_var[MULAT_HT]
        np_case[MULAT_OP] = np_prob_var[MULAT_OP]
        np_case[HOOS] = np_prob_var[HOOS]

    # Calculating buckling forces based on route types
    for i in range(n_elts):
        if np_scen[ROUTE_TYPE, i] == 1: # Straight section
            np_case[CBF_HT, i] = np_case[HOOS, i] * np_scen[SCHAR_HT, i] \
                * np_case[MULAT_HT, i]**0.5
            np_case[CBF_OP, i] = np_case[HOOS, i] * np_scen[SCHAR_OP, i] \
                * np_case[MULAT_OP, i]**0.5
        elif np_scen[ROUTE_TYPE, i] == 2: # Curve section
            np_case[CBF_HT, i] = np_case[HOOS, i] * np_case[MULAT_HT, i] \
                * np_scen[SW_HT, i] * np_scen[BEND_RADIUS, i]
            np_case[CBF_OP, i] = np_case[HOOS, i] * np_case[MULAT_OP, i] \
                * np_scen[SW_OP, i] * np_scen[BEND_RADIUS, i]
        elif np_scen[ROUTE_TYPE, i] == 3: # Sleeper
            np_case[CBF_HT, i] = np_case[HOOS, i] * np_scen[SV_HT, i]
            np_case[CBF_OP, i] = np_case[HOOS, i] * np_scen[SV_OP, i]
        elif np_scen[ROUTE_TYPE, i] == 4: # RCM
            np_case[CBF_HT, i] = np_case[HOOS, i]
            np_case[CBF_OP, i] = np_case[HOOS, i]

    # Calculate friction forces accounting for boundary conditions
    np_case[LFF_INST], np_case[RFF_INST], junk1, junk2 = calc_fric_forces(
        -np_case[MUAX] * np_scen[SW_INST] * np_scen[LENGTH],
        np_ends[REAC_INST, 0], np_ends[REAC_INST, 1])
    np_case[LFF_HT], np_case[RFF_HT], np_case[LDELTAF_HT], np_case[RDELTAF_HT] = calc_fric_forces(
        np_case[MUAX] * np_scen[SW_HT] * np_scen[LENGTH],
        np_ends[REAC_HT, 0], np_ends[REAC_HT, 1])
    np_case[LFF_OP], np_case[RFF_OP], np_case[LDELTAF_OP], np_case[RDELTAF_OP] = calc_fric_forces(
        np_case[MUAX] * np_scen[SW_OP] * np_scen[LENGTH],
        np_ends[REAC_OP, 0], np_ends[REAC_OP, 1])

    # Adjust friction forces based on boundary conditions
    if np_ends[ROUTE_TYPE_BC, 0] == 2:  # Fixed BC at "left" end side
        np_case[LFF_INST] = np.full(n_elts, -9.0E+09)
        np_case[LFF_HT] = np.full(n_elts, 9.0E+09)
        np_case[LFF_OP] = np.full(n_elts, 9.0E+09)    
    if np_ends[ROUTE_TYPE_BC, 1] == 2:  # Fixed BC at "right" end side
        np_case[RFF_INST] = np.full(n_elts, -9.0E+09)
        np_case[RFF_HT] = np.full(n_elts, 9.0E+09)
        np_case[RFF_OP] = np.full(n_elts, 9.0E+09)

    # Build up frictional effective forces
    np_case[EAF_INST] = np.maximum(
        np.maximum(np_case[LFF_INST], np_case[RFF_INST]), np_scen[RLT])
    np_case[EAF_HT] = np.minimum(
        np.minimum(np_case[LFF_HT], np_case[RFF_HT]), np_scen[FRF_HT])
    np_case[EAF_P_OP] = np.minimum(
        np.minimum(np_case[LFF_OP], np_case[RFF_OP]), np_scen[FRF_P_OP])
    np_case[EAF_OP] = np.minimum(
        np.minimum(np_case[LFF_OP], np_case[RFF_OP]), np_scen[FRF_OP])
    np_case[EAF_OP_UNBUCK] = np.minimum(
        np.minimum(np_case[LFF_OP], np_case[RFF_OP]), np_scen[FRF_OP])

    return np_case

def calc_fric_forces(np_array, restr_left, restr_right):

    """
    Accumulate friction forces from each end of the array. The calculated values are at the center
    of each element, accounting for the average increase between the element and its surrounding
    elements.

    Parameters
    ----------
    np_array : numpy.ndarray
        Array containing the local friction force for each element without accounting for
        surrounding values.
    restr_left : float
        Constant force to be added at the left of the force profile.
    restr_right : float
        Constant force to be added at the right of the force profile.

    Returns
    -------
    np_cumsum_left: numpy.ndarray
        Cumulated friction force from the left.
    np_cumsum_right: numpy.ndarray
        Cumulated friction force from the right.
    np_rolling_mean_left: numpy.ndarray
        Average friction force increment from the left.
    np_rolling_mean_right: numpy.ndarray
        Average friction force increment from the right.
    """

    # Cumulate the effective axial friction forces
    ret = np.cumsum(np_array, dtype=float)

    # Calculate the average increase between each element and its surrounding elements
    ret[2:] = ret[2:] - ret[:-2]

    # Compute the rolling mean for the left and right ends
    np_rolling_mean_left = np.append(restr_left + np_array[0] / 2.0, ret[1:] / 2.0)
    np_rolling_mean_right = np.append(ret[1:] / 2.0, restr_right + np_array[-1] / 2.0)

    # Compute the cumulative effective axial forces from the left and right
    np_cumsum_left = np.cumsum(np_rolling_mean_left)
    np_cumsum_right = np.cumsum(np_rolling_mean_right[::-1])[::-1]

    return np_cumsum_left, np_cumsum_right, np_rolling_mean_left, np_rolling_mean_right

@jit(nopython=True)
def solve_case(np_scen, np_case):

    """
    Calculate effective force profiles during hydrotest and operation and identify
    buckle properties.

    Parameters
    ----------
    np_scen : NumPy arrays
        Definition of scenario on assessed mesh
    np_case : NumPy array
        Definition of case on assessed mesh

    Returns
    -------
    NumPy array
        Properties of triggered buckle(s)
    NumPy array
        Updated definition of case on assessed mesh
    list
        [element index, KP, ESF_op] of centroid for elements containing virtual anchor points
        (by increasing order of KP, not associated with order of np_buckle_id)

    Notes
    -----
    Returned np_pp_buckle has values by rows corresponding to buckles over 8 columns
    corresponding to properties defined below:
        | SIM_PP = 0
        | KP_PP = 1
        | ROUTE_TYPE_PP= 2
        | MUAX_PP = 3
        | MULAT_OP_PP = 4
        | HOOS_PP = 5
        | CBF_OP_PP = 6
        | VAS_PP = 7

    Returned np_case has values by columns corresponding to mesh elements over 21 rows
    corresponding to properties defined below:
        | MUAX = 0
        | MULAT_HT = 1
        | MULAT_OP = 2
        | HOOS = 3
        | CBF_HT = 4
        | CBF_OP = 5
        | LFF_INST = 6
        | LFF_HT = 7
        | LFF_OP = 8
        | RFF_INST = 9
        | RFF_HT = 10
        | RFF_OP = 11
        | EAF_INST = 12
        | EAF_HT = 13
        | EAF_P_OP = 14
        | EAF_OP = 15
        | EAF_OP_UNBUCK = 16
        | LDELTAF_HT = 17
        | RDELTAF_HT = 18
        | LDELTAF_OP = 19
        | RDELTAF_OP = 20

    """

    # Step 1: Get order and location of potential buckles from HT step
    np_beta = (np_case[CBF_HT] - np_case[EAF_INST]) / (np_scen[FRF_HT] - np_scen[RLT])
    np_beta = np.around(np_beta, decimals = 6)
    sorted_beta_array = np.argsort(np_beta, kind = "mergesort")

    # Step 2: Compare local driving force during HT with CBF to identify actual buckles,
    # in the order of the potential buckles
    np_buckle_id = np.empty(0)
    for i in sorted_beta_array:
        if np_case[EAF_HT, i] >= np_case[CBF_HT, i]:
            np_buckle_id = np.append(np_buckle_id, i)
            np_ff_buckle = calc_friction_force_from_buckle(np_scen, np_case, i, "HT")
            np_case[EAF_HT] = np.minimum(np_ff_buckle, np_case[EAF_HT])

            # Step 3a: Set up the EAF OP Pressure profile with the buckle locations from HT
            np_ff_buckle = calc_friction_force_from_buckle(np_scen, np_case, i, "OP")
            np_case[EAF_P_OP] = np.minimum(np_ff_buckle, np_case[EAF_P_OP])

            # Step 5a: Set up the EAF OP profile with the buckle locations from HT
            np_case[EAF_OP] = np.minimum(np_ff_buckle, np_case[EAF_OP])

    # Step 3b: Identify the location and order of additional potential buckles
    # during OP (Pressure only)
    np_beta = (np_case[CBF_OP] - np_case[EAF_INST]) / (np_scen[FRF_P_OP] - np_scen[RLT])
    np_beta = np.around(np_beta, decimals = 6)
    sorted_beta_array = np.argsort(np_beta, kind = "mergesort")

    # Step 4: Compare the local driving force with the CBF during OP (pressure only) to identify
    # actual buckles, taking into account the actual buckles from HT
    for i in sorted_beta_array:
        if np_case[EAF_P_OP, i] >= np_case[CBF_OP, i]:
            np_buckle_id = np.append(np_buckle_id, i)
            np_ff_buckle = calc_friction_force_from_buckle(np_scen, np_case, i, "OP")
            np_case[EAF_P_OP] = np.minimum(np_ff_buckle, np_case[EAF_P_OP])

            # Step 5a: Set up the EAF OP profile with the buckle locations from OP pressure only
            np_case[EAF_OP]=np.minimum(np_ff_buckle, np_case[EAF_OP])

    # Step 5b: Calculate Beta2 to identify the order and location of the potential buckles from the
    # temperature in operation
    # TODO: Explain in the manual that this calculation assumes linear temperature variations.
    np_beta = (
        np_case[CBF_OP] - np_case[EAF_INST] - (
            np_scen[FRF_P_OP] - np_scen[RLT])) / np_scen[FRF_T_OP]
    np_beta = np.around(np_beta, decimals = 6)
    sorted_beta_array = np.argsort(np_beta, kind = "mergesort")

    # Step 6: Compare the local driving force with the CBF (pressure + temperature) to find
    # actual buckles
    for i in sorted_beta_array:
        if np_case[EAF_OP, i] >= np_case[CBF_OP, i]:
            np_buckle_id = np.append(np_buckle_id, i)
            np_ff_buckle = calc_friction_force_from_buckle(np_scen, np_case, i, "OP")
            np_case[EAF_OP] = np.minimum(np_ff_buckle, np_case[EAF_OP])

    # Extract the number of elements from the scenario array
    n_elts = np_scen[KP].size

    # Drop buckle elements duplicated between hydrotest and operation steps
    # [can happen if the CBF < Buckle residual force]
    np_buckle_id = np.unique(np_buckle_id)

    # Initiate post-processing outputs array
    np_pp_buckle = np.empty((np_buckle_id.size, 8))
    vap_list = []

    if len(np_buckle_id) > 0: # At least one buckle detected
        for i_buckle in range(len(np_buckle_id)):
            ielt_buckle = np.sort(np_buckle_id.astype(np.int64))[i_buckle]

            # Identify possible VAP (surrounding buckling susceptibility areas)
            np_ff_buckle = calc_friction_force_from_buckle(np_scen, np_case, ielt_buckle, "OP")
            np_possible_vap_id = np.where(
                np.isclose(np_case[EAF_OP], np_ff_buckle.astype(np.float64)) == False)[0]

            # Add first and last elements to possible VAP for fixed end cases
            if not (0 in np_possible_vap_id):
                np_possible_vap_id = np.append(np_possible_vap_id, 0)
            if not (n_elts in np_possible_vap_id):
                np_possible_vap_id = np.append(np_possible_vap_id, n_elts)
            np_possible_vap_id=np.sort(np_possible_vap_id)

            # For each buckle, look for surrounding VAP and calculate KP
            if ielt_buckle <= np.min(np_possible_vap_id):
                ivap_left = ielt_buckle
            else:
                np_distance_left = np.absolute(
                    np_possible_vap_id[np_possible_vap_id < ielt_buckle]-ielt_buckle)
                ivap_left = min(
                    ielt_buckle, np_possible_vap_id[
                        np_possible_vap_id < ielt_buckle][np_distance_left.argmin()] + 1)

            if ielt_buckle >= np.max(np_possible_vap_id):
                ivap_right = ielt_buckle
            else:
                np_distance_right = np.absolute(
                    np_possible_vap_id[np_possible_vap_id > ielt_buckle]-ielt_buckle)
                ivap_right = max(
                    ielt_buckle, np_possible_vap_id[
                        np_possible_vap_id > ielt_buckle][np_distance_right.argmin()] - 1)

            if ivap_left < ivap_right: # Buckle detected
                # TODO: add switch to calculate KP of actual VAP instead of centroid of elements
                # TODO: ivap_left and ivap_right where VAP are located
                if ivap_left == 0:
                    kp_vap_left = np_scen[KP][ivap_left] - np_scen[LENGTH][ivap_left]
                else:
                    kp_vap_left = np_scen[KP][ivap_left] - np_scen[LENGTH][ivap_left]
                if ivap_right == (n_elts - 1):
                    kp_vap_right = np_scen[KP][ivap_right] + np_scen[LENGTH][ivap_right]
                else:
                    kp_vap_right = np_scen[KP][ivap_right] + np_scen[LENGTH][ivap_right]

                # Add new VAP to list if not already identified
                temp_list = [ivap_left, kp_vap_left, np_case[EAF_OP][ivap_left]]
                if temp_list not in vap_list:
                    vap_list.append(temp_list)
                temp_list = [ivap_right, kp_vap_right, np_case[EAF_OP][ivap_right]]
                if temp_list not in vap_list:
                    vap_list.append(temp_list)
            else: # not really triggered buckle
                kp_vap_right = np_scen[KP, ielt_buckle]
                kp_vap_left = kp_vap_right

            # Fill up the array of outputs for post-processing
            np_pp_buckle[i_buckle, KP_PP] = np_scen[KP, ielt_buckle]
            np_pp_buckle[i_buckle, ROUTE_TYPE_PP] = np_scen[ROUTE_TYPE, ielt_buckle]
            np_pp_buckle[i_buckle, MUAX_PP] = np_case[MUAX, ielt_buckle]
            np_pp_buckle[i_buckle, MULAT_OP_PP] = np_case[MULAT_OP, ielt_buckle]
            np_pp_buckle[i_buckle, HOOS_PP] = np_case[HOOS, ielt_buckle]
            np_pp_buckle[i_buckle, CBF_OP_PP] = np_case[CBF_OP, ielt_buckle]
            np_pp_buckle[i_buckle, VAS_PP] = kp_vap_right - kp_vap_left

    # End of condition on presence of buckle
    vap_list = sorted(vap_list, key = lambda x: x[1])

    return np_pp_buckle, np_case, vap_list

@jit(nopython=True)
def calc_friction_force_from_buckle(np_scen, np_case, ielt_buckle, phase_str):

    """
    Calculate the effective axial frictional forces for each element in a scenario.

    Parameters
    ----------
    np_scen : numpy.ndarray
        2D array containing scenario-specific data, where rows represent different parameters and
        columns represent elements.
    np_case : numpy.ndarray
        2D array containing case-specific data, where rows represent different parameters and
        columns represent elements.
    ielt_buckle : int
        Index of the buckle element.
    phase_str : str
        Phase label indicating whether the calculation is for "HT" (hydrotest) or
        "OP" (operational) phase.

    Returns
    -------
    np_ff_buckle : numpy.ndarray
        1D array containing the computed friction forces for each element in the scenario.

    """

    # Extract the number of elements from the scenario array
    n_elts = np_scen[KP].size

    if phase_str == "HT":
        cbf = np_case[CBF_HT, ielt_buckle]
        residual_buckle_force = np_scen[EAF_BUCKLE_HT, ielt_buckle]
        residual_buckle_length = np_scen[L_BUCKLE_HT, ielt_buckle]
        i_sw = SW_HT
        i_ldeltaf = LDELTAF_HT
        i_rdeltaf = RDELTAF_HT

    elif phase_str == "OP":
        cbf = np_case[CBF_OP, ielt_buckle]
        residual_buckle_force = np_scen[EAF_BUCKLE_OP, ielt_buckle]
        residual_buckle_length = np_scen[L_BUCKLE_OP, ielt_buckle]
        i_sw = SW_OP
        i_ldeltaf = LDELTAF_OP
        i_rdeltaf = RDELTAF_OP

    else:
        print(f'Unrecognised phase label {phase_str}')

    # The residual buckle force should be capped by the minimum CBF
    residual_buckle_force = min(residual_buckle_force, cbf)

    # Find the index of elements closer to "left" side of buckle
    kp_flat_left = np_scen[KP, ielt_buckle] - residual_buckle_length / 2.0
    np_distance_left = np.absolute(np_scen[KP] - kp_flat_left)
    ielt_left = np_distance_left.argmin()
    if np_scen[KP,ielt_left] > kp_flat_left:
        ielt_left = max(0, ielt_left-1)

    # Find the index of elements closer to "right" side of buckle
    kp_flat_right = np_scen[KP, ielt_buckle] + residual_buckle_length / 2.0
    np_distance_right = np.absolute(np_scen[KP] - kp_flat_right)
    ielt_right = np_distance_right.argmin()
    if np_scen[KP, ielt_right] < kp_flat_right:
        ielt_right = min(ielt_right + 1, n_elts - 1)

    # Calculate the incremental effective axial frictional forces
    eaf_left_centroid = residual_buckle_force + np_case[MUAX, ielt_left] \
        * np_scen[i_sw, ielt_left] * (kp_flat_left - np_scen[KP, ielt_left])
    eaf_right_centroid = residual_buckle_force + np_case[MUAX, ielt_right] \
        * np_scen[i_sw, ielt_right] * (np_scen[KP, ielt_right] - kp_flat_right)

    # Compute rolling means for the left and right sections around the buckle
    np_rolling_mean_left = np.append(np.zeros(ielt_right+1-1), eaf_right_centroid)
    np_rolling_mean_left = np.append(np_rolling_mean_left, np_case[i_ldeltaf][(ielt_right+1):])
    np_rolling_mean_right = np.append(np_case[i_rdeltaf][:ielt_left], eaf_left_centroid)
    np_rolling_mean_right = np.append(np_rolling_mean_right, np.zeros(n_elts - (ielt_left+1)))

    # Compute left and right cumulative sums of the effective axial forces for each element
    np_lff_buckle = np.cumsum(np_rolling_mean_left)
    np_rff_buckle = np.cumsum(np_rolling_mean_right[::-1])[::-1]

    # Determine the maximum effective axial frictional force for each element
    np_ff_buckle = np.maximum(np.maximum(np_lff_buckle,residual_buckle_force), np_rff_buckle)

    return np_ff_buckle

def run_monte_carlo(n_worker, n_sim, np_distr, np_scen, np_ends, fric_sampling, bl_verbose = False):

    """
    Set to run the Monte-Carlo simulations using multiple workers and gather the properties of
    the buckles that have triggered.

    Parameters
    ----------
    n_worker : int
        Number of worker processes spawned in the multiprocess.
    n_sim : int
        Number of Monte-Carlo simulations to be run.
    np_distr: NumPy array
        3-D numpy array containing the stochastic distributions
        (dim 1: properties, dim 2: elements, dim 3: values).
    np_scen : NumPy array
        Numpy array containing the design data along the pipeline
        route (mesh) that remains constant among deterministic and
        Monte-Carlo simulations (except the stochastic distributions).
    np_ends : NumPy array
        Returns a numpy array with the definition of the tie-ins at
        the pipeline ends.
    fric_sampling : int
        Switch to select the sampling method of the soil lateral friction
        factor (0 for 'per Element' or 1 'per OOS Reference Length').

    Returns
    ----------
    list_buckle_prop : List[np.ndarray]
        Array containing for each simulation the properties of
        the buckle(s) that has(ve) triggered.

    Other Parameters
    ----------------
    bl_verbose : boolean, optional
        True if intermediate printouts are required (False by default).
    """

    mp_output = Queue()
    processes = []
    if bl_verbose:
        start_time = time.time()

    # Distribute simulations across worker processes
    for i_worker in range(n_worker):
        if i_worker < (n_worker - 1):
            processes.append(Process(target=exec_worker_stack,
                                     args=(int(i_worker*int(n_sim/n_worker)),
                                           int((i_worker+1)*int(n_sim/n_worker)),
                                           np_distr, np_scen, np_ends, fric_sampling, mp_output)))
        else:
            processes.append(Process(target=exec_worker_stack,
                                     args=(int(i_worker*int(n_sim/n_worker)),
                                           int(n_sim), np_distr, np_scen, np_ends, fric_sampling, mp_output)))

    # Start worker processes
    for p in processes:
        p.start()

    if bl_verbose:
        print(f'   Time taken to start the queue and {n_worker} worker process: {time.time() - start_time:.1f}s')

    # Wait for output from worker processes
    while mp_output.qsize() == 0:
        time.sleep(1)

    buckle_prop = []

    # Collect buckle properties from the output queue
    if bl_verbose:
        n_sim_display_list = [10**i for i in range(1+round(np.log10(n_sim)))]

    while mp_output:
        try:
            buckle_prop.append(mp_output.get(timeout=10))
        except:
            break

        if bl_verbose:
            for n_sim_display in n_sim_display_list:
                if len(buckle_prop) >= n_sim_display:
                    print(f'   Time taken to solve {n_sim_display:.0f} / {n_sim:.0f} simulations: {time.time() - start_time:.1f}s')
                    n_sim_display_list.remove(n_sim_display)

    return buckle_prop

def exec_worker_stack(n_sim_start, n_sim_end, np_distr, np_scen, np_ends, fric_sampling, mp_output):

    """
    Run a stack of random simulations using a single worker and add the results to the
    post-processing queue mp_output.

    Parameters
    ----------
    n_sim_start : int
        Number of the first simulation to be executed by the current worker.
    n_sim_end : int
        Number of the last simulation to be executed by the current worker (i.e., this simulation
        number is not executed in this call to the function).
    np_distr: NumPy array
        3-D numpy array containing the stochastic distributions
        (dim 1: properties, dim 2: elements, dim 3: values).
    np_scen : NumPy array
        Numpy array containing the design data along the pipeline route (mesh) that remains
        constant among deterministic and Monte-Carlo simulations
        (except the stochastic distributions).
    np_ends : NumPy array
        Returns a numpy array with the definition of the tie-ins at the pipeline ends.
    fric_sampling : int
        Switch to select the sampling method of the soil lateral friction factor
        (0 for 'per Element' or 1 'per OOS Reference Length').
    mp_output: Queue
        Results are added to this Queue for subsequent post-processing.
    """

    # Iterate over the range of simulations assigned to the worker
    for i_sim in range(n_sim_start, n_sim_end):

        # Sample randomness for the current simulation
        np_prob_var = sample_randomness_case(fric_sampling, np_distr, np_scen)

        # Preprocess the simulation case
        np_case = preprocess_case(np_prob_var, np_scen, np_ends, bl_det = False)

        # Solve the simulation case to find potential buckle properties
        np_pp_buckle, junk1, junk2 = solve_case(np_scen, np_case)

        # Get the number of buckles triggered in the simulation
        n_buckle = np_pp_buckle.shape[0]

        # If buckles triggered, adjust the simulation number of the buckle and add to the queue
        if n_buckle > 0:
            for i_buckle in range(n_buckle):
                np_pp_buckle[i_buckle, SIM_PP] = i_sim
            mp_output.put(np_pp_buckle)
