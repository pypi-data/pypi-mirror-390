"""
This module contains the post-processing functions of BuckPy.
"""

import time
import numpy as np
import pandas as pd
import pandas.io.formats.excel
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

def pp_comb_prob(df_in, df_buckle, col_no, n_sim):

    """
    Count the number of set combinations based on given set number

    Parameters
    ----------
    df_in : pandas DataFrame
        DataFrame containing the set number of combination with buckles along the pipeline.
    df_buckle : pandas DataFrame
        DataFrame containing the count and probability of set number of combination with buckles.
    col_no : String
        Column name of the set number
    n_sim : int
        Number of simulations.

    Returns
    -------
    df_out : pandas DataFrame
        DataFrame containing post-processed statistics about the number of set combination
        with buckles along the pipeline.
    """

    def pp_count_comb(row, df, col):
        # Add 1 to the value each time there is a buckle at the current set
        df.iloc[int(row.loc['isim']), int(row.loc[col])] += 1.0

    # Row number is the total simulation number and column number is the total set number
    n_col = df_in.unique().size
    df_out = pd.DataFrame(0, index = np.arange(int(n_sim)),
                                columns = np.arange(int(n_col + 1.0)))

    # Add 1 to the value in df_out each time there is a buckle
    df_buckle.apply(lambda row: pp_count_comb(row, df_out, col_no), axis = 1)

    # Delete the all 0 rows and the first column, and add prefix to column names
    df_out = df_out[(df_out.T != 0).any()].iloc[:, 1:].add_prefix('Set_')

    # Count the number of unique set combinations
    col_list = df_out.columns.values.tolist()
    df_out = df_out.groupby(col_list).size().reset_index().rename(
        columns = {0: 'Number of Simulations'})

    # Calculate probability and sort values in descending order based on count and reset index
    df_out['Probability of Combination'] = df_out['Number of Simulations'] / n_sim
    df_out = df_out.sort_values(
        by = 'Number of Simulations', ascending = False).reset_index(drop = True)

    return df_out

def pp_rename_columns(df_in, df_out):

    """
    Rename columns in the post-processing DataFrame.

    Parameters
    ----------
    df_in : pandas DataFrame
        DataFrame containing the set number of combination with buckles along the pipeline.
    df_out : pandas DataFrame
        DataFrame containing post-processed statistics about the number of set combination
        with buckles along the pipeline.

    Returns
    -------
    df_out : pandas DataFrame
        DataFrame containing post-processed statistics about the number of set combination
        with buckles along the pipeline.

    Notes
    -----
    Use the Python built-in ``set`` for unique labels, e.g., ``set(labels)``.
    """

    # Change column names from 'Set_1' to predefined names
    new_col_list = np.array(df_in['col_name'].values).tolist()
    df_out.columns = np.concatenate(
        np.array([new_col_list, ['Number of Simulations', 'Probability of Combination']],
                 dtype = object)).tolist()

    # Create new column name list sorted by KP values and reorder columns
    df_out['Combination Id'] = df_out.index + 1
    col_list = np.array(df_in.sort_values(by = 'index').loc[:, 'col_name'].values).tolist()
    cols = np.concatenate(
        np.array([['Combination Id', 'Number of Simulations', 'Probability of Combination'],
                  col_list], dtype = object)).tolist()
    df_out = df_out[cols]

    # Create a double header
    header_first_line = [''] * 3 + ['Number of Buckles'] * (len(cols) - 3)
    header_turples = list(zip(header_first_line, cols))
    double_header = pd.MultiIndex.from_tuples(header_turples)
    df_out.columns = double_header

    return df_out

def pp_comb_buckles_per_set(df_pp, df_pp_set, n_sim):

    """
    Count the number of set combinations and sort based on the most frequent set combinations 
    based on post-processing set.

    Parameters
    ----------
    df_pp : pandas DataFrame
        DataFrame containing pipeline element analysis results.
    df_pp_set : pandas DataFrame
        DataFrame containing the definition of the post-processed sets.
    n_sim : int
        Number of simulations.

    Returns
    -------
    df_set_comb : pandas DataFrame
        DataFrame containing post-processed statistics about the number of set combination
        with buckles along the pipeline.
    """

    # Create index columns for the original index and the sorted pp set value index
    df_pp_set = df_pp_set[['pp_set', 'KP_from', 'KP_to']].sort_values(
        by = ['pp_set', 'KP_from']).reset_index()
    df_pp_set = df_pp_set.reset_index().rename(columns = {'level_0': 'index_sorted'})

    # Select the number of simulation and post-precessing set number with a buckle
    df_set_buckle_no = df_pp[['isim', 'pp_set']].sort_values(by = ['isim', 'pp_set'])

    # Count the number of set combinations based on given set number
    df_set_comb = pp_comb_prob(df_pp_set['pp_set'], df_set_buckle_no, 'pp_set', n_sim)

    # Insert the extra column of duplicated set number into df_set_comb
    df_duplicated = df_pp_set[df_pp_set.duplicated(subset = ['pp_set'])].reset_index(drop = True)
    df_duplicated.apply(lambda row: df_set_comb.insert(
        int(row['index_sorted']), f"Duplicate_{int(row['pp_set'])}",
        df_set_comb.iloc[:, int(row['index_sorted'] - 1)]), axis = 1)

    # Create new column name using KP from and KP to
    df_pp_set[['KP_from', 'KP_to']] = df_pp_set[['KP_from', 'KP_to']].astype(int).astype(str)
    df_pp_set['col_name'] = 'KP ' + df_pp_set['KP_from'] + ' to ' + df_pp_set['KP_to']

    # Rename column names from 'Set_' to certain column names
    df_set_comb = pp_rename_columns(df_pp_set, df_set_comb)

    return df_set_comb

def pp_comb_buckles_per_section(df_pp, df_scen, n_sim):

    """
    Count the number of set combinations and sort based on the most frequent set combinations
    based on section number in the route data.

    Parameters
    ----------
    df_pp : pandas DataFrame
        DataFrame containing pipeline element analysis results.
    df_scen : DataFrame
        Dataframe containing the design data along the pipeline route (mesh) that remains
        constant among deterministic and Monte-Carlo simulations.
    n_sim : int
        Number of simulations.

    Returns
    -------
    df_set_comb : pandas DataFrame
        DataFrame containing post-processed statistics about the number of set combination
        with buckles along the pipeline.
    """

    def pp_section_no(kp, kp_list):
        # Add the current KP to the kp list and sort it
        kp_list = np.append(kp_list, kp)
        kp_list.sort()

        # Find the index of the current KP
        section_no = np.where(kp_list == kp)[0][0]

        return section_no

    # Select the number of simulation and post-precessing KP number with a buckle
    df_buckle_kp = df_pp[['isim', 'KP']].sort_values(by = ['isim', 'KP'])

    # Use KP range to group KP into sections and rename columns
    df_section = df_scen[['KP From', 'KP To', 'Point ID From', 'Point ID To']].drop_duplicates(
        subset = ['KP From']).reset_index(drop = True)
    df_section.columns = ['KP_from', 'KP_to', 'point_id_from', 'point_id_to']

    # Find the unique KP value and create section number column in df_buckle_kp
    df_kp = pd.DataFrame({'KP': df_buckle_kp['KP'].unique()})
    df_kp['Section No'] = df_kp.apply(lambda row: pp_section_no(
        row['KP'], df_section['KP_from'].unique()), axis = 1)

    # Merge the Section Number column to df_buckle_kp
    df_buckle_kp = pd.merge(df_buckle_kp, df_kp, on = 'KP', how = 'left')

    # Count the number of set combinations based on given set number
    df_set_comb = pp_comb_prob(df_section['KP_from'], df_buckle_kp, 'Section No', n_sim)

    # Create new column name using Point ID
    df_section = df_section.sort_values(by = 'KP_from').reset_index()
    df_section['col_name'] = df_section['point_id_from'] + ' to ' + df_section['point_id_to']

    # Rename column names from 'Set_' to certain column names
    df_set_comb = pp_rename_columns(df_section, df_set_comb)

    return df_set_comb

def pp_char_vas(df_pp, df_buckling, df_set):

    """
    Determine the characteristic VAS.

    Parameters
    ----------
    df_pp : pandas DataFrame
        DataFrame containing pipeline element analysis results.
    df_buckling : pandas DataFrame
        DataFrame containing buckling data.
    df_set : pandas DataFrame
        DataFrame containing sets along the pipeline route.

    Returns
    -------
    df_set : pandas DataFrame
        Updated DataFrame containing characteristic VAS information.
    """

    df_merged = pd.merge(df_pp, df_buckling, on='pp_set')
    df_merged = df_merged.sort_values(by = ['pp_set', 'VAS_op'])
    df_merged['VAS_op'] = df_merged['VAS_op'].round(1)

    # Dataframe grouping the VAS in ascending order at each set along the pipeline route
    df_char_vas = df_merged.groupby(by = ['pp_set', 'VAS_op', 'prob_buckling'], as_index = False) \
        .agg(VAS_occurrence = ('VAS_op', 'count'), no_buckles = ('no_buckles', 'max'))

    # Add the probability associated to the characteristic VAS
    df_set_temp = df_set.copy().drop_duplicates(subset = 'pp_set', keep = 'first')
    df_char_vas = df_char_vas.merge(df_set_temp[['pp_set', 'Characteristic VAS Probability']],
                                    on = 'pp_set', how = 'inner')

    # Cumulative distributions of the VAS (conditional and unconditional)
    df_char_vas['VAS_prob_cond'] = df_char_vas['VAS_occurrence'] / df_char_vas['no_buckles']
    df_char_vas['VAS_cumsum_prob_cond'] = df_char_vas[['pp_set', 'VAS_prob_cond']] \
        .groupby(by = 'pp_set').cumsum()

    # Lines below associate VAS=0 to cases not buckling
    df_char_vas['VAS_cumsum_prob_uncond'] = (1.0 - df_char_vas['prob_buckling']) \
        + df_char_vas['VAS_cumsum_prob_cond'] * df_char_vas['prob_buckling']

    # Complementary distributions of the VAS (conditional and unconditional)
    df_char_vas['prob_exceedance_cond'] = 1.0 - df_char_vas['VAS_cumsum_prob_cond']
    df_char_vas['prob_exceedance_uncond'] = 1.0 - df_char_vas['VAS_cumsum_prob_uncond']

    # Difference bewteen the complementary distributions and target probabilities of excedance
    df_char_vas['delta_prob_exceedance_cond'] = \
        (df_char_vas['prob_exceedance_cond'] - \
         df_char_vas['Characteristic VAS Probability']).abs()
    df_char_vas['delta_prob_exceedance_uncond'] = \
        (df_char_vas['prob_exceedance_uncond'] - \
         df_char_vas['Characteristic VAS Probability']).abs()

    # NumPy array with the rows containing the characteristic VAS of each pp_set
    vas_cond_indices = df_char_vas.groupby(
        by = 'pp_set')['delta_prob_exceedance_cond'].idxmin().to_numpy()
    vas_uncond_indices = df_char_vas.groupby(
        by = 'pp_set')['delta_prob_exceedance_uncond'].idxmin().to_numpy()

    # Find conditional VAS by pp_set
    df_vas_cond = df_char_vas.loc[vas_cond_indices, ['pp_set', 'VAS_op']]
    df_vas_cond.rename(columns = {'VAS_op': 'VAS_charac_conditional'}, inplace = True)

    # Find unconditional VAS by pp_set
    df_vas_uncond = df_char_vas.loc[vas_uncond_indices, ['pp_set', 'VAS_op']]
    df_vas_uncond.rename(columns = {'VAS_op': 'VAS_charac_unconditional'}, inplace = True)

    # Assign conditional and unconditional VAS by pp_set
    df_set = pd.merge(df_set, df_vas_cond, on = 'pp_set', how = 'outer')
    df_set = pd.merge(df_set, df_vas_uncond, on = 'pp_set', how = 'outer')
    df_set.loc[df_set['prob_buckling'] < df_set['Characteristic VAS Probability'],
               'VAS_charac_unconditional'] = 0.0

    return df_set

def pp_char_fric(df_pp, df_buckling, df_set, prob_exceed_char_fric):

    """
    Determine the characteristic lateral breakout friction.

    Parameters
    ----------
    df_pp : pandas DataFrame
        DataFrame containing pipeline element analysis results.
    df_buckling : pandas DataFrame
        DataFrame containing buckling data.
    df_set : pandas DataFrame
        DataFrame containing sets along the pipeline route.
    prob_exceed_char_fric : float
        Probability of exceeding characteristic lateral breakout friction.

    Returns
    -------
    df_set : pandas DataFrame
        Updated DataFrame containing characteristic lateral breakout friction information.
    """

    # Dataframe containing the list of frictions in ascending order at each set
    df_merged = pd.merge(df_pp, df_buckling, on='pp_set')
    df_merged = df_merged.sort_values(by = ['pp_set', 'mulat_op'])

    # Dataframe grouping the frictions in ascending ordet at each set along the pipeline route
    df_char_fric = df_merged.groupby(
        by = ['pp_set', 'mulat_op', 'prob_buckling'], as_index = False) \
        .agg(mulat_occurrence = ('mulat_op', 'count'), no_buckles = ('no_buckles', 'max'))

    # Cumulative distributions of the friction (conditional and unconditional)
    df_char_fric['mulat_prob_cond'] = df_char_fric['mulat_occurrence'] / df_char_fric['no_buckles']
    df_char_fric['mulat_cumsum_prob_cond'] = df_char_fric[['pp_set', 'mulat_prob_cond']] \
        .groupby(by = 'pp_set').cumsum()

    # Lines below associate friction=0 to cases not buckling
    df_char_fric['mulat_cumsum_prob_uncond'] = (1.0 - df_char_fric['prob_buckling']) \
        + df_char_fric['mulat_cumsum_prob_cond'] * df_char_fric['prob_buckling']

    # Complementary distributions of the friction (conditional and unconditional)
    df_char_fric['prob_exceedance_cond'] = 1.0 - df_char_fric['mulat_cumsum_prob_cond']
    df_char_fric['prob_exceedance_uncond'] = 1.0 - df_char_fric['mulat_cumsum_prob_uncond']

    # Difference between the complementary distributions and target probabilities of excedance
    df_char_fric['delta_prob_exceedance_cond'] = (df_char_fric['prob_exceedance_cond']
                                                 - prob_exceed_char_fric).abs()
    df_char_fric['delta_prob_exceedance_uncond'] = (df_char_fric['prob_exceedance_uncond']
                                                   - prob_exceed_char_fric).abs()

    # NumPy array with the rows containing the characteristic friction of each pp_set
    indices_mulat_cond = df_char_fric.groupby(by = 'pp_set')['delta_prob_exceedance_cond'] \
        .idxmin().to_numpy()
    indices_mulat_uncond = df_char_fric.groupby(by = 'pp_set')['delta_prob_exceedance_uncond'] \
        .idxmin().to_numpy()

    # Find conditional friction by pp_set
    df_fric_cond = df_char_fric.loc[indices_mulat_cond, ['pp_set', 'prob_buckling', 'mulat_op']]
    df_fric_cond.rename(columns = {'mulat_op': 'mulat_charac_conditional'}, inplace = True)

    # Find unconditional friction by pp_set
    df_fric_uncond = df_char_fric.loc[indices_mulat_uncond, ['pp_set', 'prob_buckling', 'mulat_op']]
    df_fric_uncond.rename(columns = {'mulat_op': 'mulat_charac_unconditional'}, inplace = True)

    # Assign conditional and unconditional friction by pp_set
    df_set = pd.merge(df_set, df_fric_cond, on = 'pp_set', how = 'outer')
    df_set = pd.merge(df_set, df_fric_uncond, on = 'pp_set', how = 'outer')
    df_set.loc[df_set['prob_buckling'] < prob_exceed_char_fric,
               'mulat_charac_unconditional'] = 0.0

    return df_set

def pp_elem(df_pp, n_sim):

    """
    Perform post-processing of the probability of buckling, VAS and lateral breakout
    friction at each element along the pipeline route.

    Parameters
    ----------
    df_pp : pandas DataFrame
        DataFrame containing the results of the analyses.
    n_sim : int
        Total number of simulations.

    Returns
    -------
    df_elem : pandas DataFrame
        DataFrame containing post-processed probabilities, VAS and lateral breakout friction
        for each pipeline element.
    """

    # Probability of buckling at each element along the pipeline route
    df_buckling = df_pp[['KP', 'isim']].groupby('KP', as_index = False).agg(
        no_buckles = ('isim', 'nunique'))
    df_buckling['prob_buckling'] = df_buckling['no_buckles'] / n_sim
    df_buckling['prob_not_buckling'] = 1.0 - df_buckling['prob_buckling']

    # VAS at each element along the pipeline route
    df_vas = df_pp[['KP', 'VAS_op']].groupby('KP', as_index = False).agg(
        VAS_mean = ('VAS_op', 'mean'), VAS_std = ('VAS_op', 'std'),
        VAS_min = ('VAS_op', 'min'), VAS_max = ('VAS_op', 'max'))

    # Lateral breakout friction at each element along the pipeline route
    df_friction = df_pp[['KP', 'mulat_op']].groupby('KP', as_index = False).agg(
        mulat_mean = ('mulat_op', 'mean'), mulat_std = ('mulat_op', 'std'),
        mulat_min = ('mulat_op', 'min'), mulat_max = ('mulat_op', 'max'))

    # Merge df_buckling and df_vas on 'KP'
    df_elem = pd.merge(df_buckling, df_vas, on = 'KP')

    # Merge merged_df and df_friction on 'KP'
    df_elem = pd.merge(df_elem, df_friction, on = 'KP')

    # Change labels for print-out
    df_elem = df_elem.rename(columns = {
        'KP': 'Centroid of the Element (m)',
        'no_buckles': 'Number of Simulations with a Buckle',
        'prob_buckling': 'Probability of Buckling',
        'prob_not_buckling': 'Probability of not Buckling',
        'VAS_mean': 'Mean of the VAS (m)',
        'VAS_std': 'Standard Deviation of the VAS (m)',
        'VAS_min': 'Minimum VAS (m)',
        'VAS_max': 'Maximum VAS (m)',
        'mulat_mean': 'Mean of the Lateral Breakout Friction',
        'mulat_std': 'Standard Deviation of the Lateral Breakout Friction',
        'mulat_min': 'Minimum Lateral Breakout Friction',
        'mulat_max': 'Maximum Lateral Breakout Friction'})

    df_elem = df_elem.fillna(0.0)

    return df_elem

def pp_no_buckles(df_pp, n_sim):

    """
    Perform post-processing of the number of buckles along the pipeline.

    Parameters
    ----------
    df_pp : pandas DataFrame
        DataFrame containing pipeline element analysis results.
    n_sim : int
        Total number of simulations.

    Returns
    -------
    df_no_buckles : pandas DataFrame
        DataFrame containing post-processed statistics about the number of buckles
        along the pipeline.
    """

    # Number of buckles per simulation
    df_grouped = df_pp[['isim', 'KP']].groupby('isim', as_index = False).agg(
        no_buckles = ('KP', 'count'))

    # Number of simulations as a function of the number of buckles along the pipeline
    df_no_buckles = df_grouped.pivot_table(columns = ['no_buckles'], aggfunc = 'size')
    df_no_buckles = df_no_buckles.reset_index()
    df_no_buckles = df_no_buckles.rename(columns={
        'n_buckle': 'Total Number of Buckles', 0: 'Occurrence'})

    # Accounting for cases without buckle in cumsum
    new_row = {'no_buckles': 0, 'Occurrence': n_sim - df_no_buckles['Occurrence'].sum()}
    df_no_buckles = pd.concat([df_no_buckles, pd.DataFrame(new_row, index=[0])], ignore_index=True)
    df_no_buckles = df_no_buckles.sort_values(by = ['no_buckles']).reset_index(drop=True)

    # Distribution of the expected number of buckles along the pipeline
    df_no_buckles['Probability'] = df_no_buckles['Occurrence'] / n_sim
    df_no_buckles['Cumulative Probability'] = df_no_buckles['Probability'].cumsum()

    # Change labels for print-out
    df_no_buckles = df_no_buckles.rename(columns = {
        'no_buckles': 'Number of Buckles',
        'Occurrence': 'Number of Simulations',
        'Probability': 'Probability of Buckling',
        'Cumulative Probability': 'Cumulative Probability of Buckling'})

    return df_no_buckles

def pp_sets(df_pp, n_sim, prob_exceed_char_fric, df_pp_set, df_scen):

    """
    Perform post-processing of the probability of buckling, VAS and lateral breakout
    friction at each post-processing set along the pipeline route.

    Parameters
    ----------
    df_pp : pandas DataFrame
        DataFrame containing pipeline element analysis results.
    n_sim : int
        Total number of simulations.
    prob_exceed_char_fric : float
        Probability of exceedance of the characteristic lateral breakout friction.
    df_pp_set : DataFrame
        Definition of element sets for post-processing outputs.
    df_scen : DataFrame
        Dataframe containing the design data along the pipeline
        route (mesh) that remains constant among deterministic and
        Monte-Carlo simulations.

    Returns
    -------
    df_set : pandas DataFrame
        DataFrame containing post-processed statistics about pipeline sets.
    """

    # Probability of buckling at each set along the pipeline route
    df_pp_set = df_pp_set[['pp_set', 'KP_from', 'KP_to', 'Characteristic VAS Probability']]

    # Probability of buckling at each set along the pipeline route
    df_buckling = df_pp[['pp_set', 'KP_from', 'KP_to', 'isim', 'VAS_op']].groupby(
        'pp_set', as_index = False).agg(
            no_simulations_with_buckles = ('isim', 'nunique'), no_buckles = ('VAS_op', 'count'))
    df_buckling['prob_buckling'] = df_buckling['no_simulations_with_buckles'] / n_sim
    df_buckling['prob_not_buckling'] = 1.0 - df_buckling['prob_buckling']

    # VAS at each set along the pipeline route
    df_vas = df_pp[['pp_set', 'VAS_op']].groupby('pp_set', as_index = False).agg(
        VAS_mean = ('VAS_op', 'mean'), VAS_std = ('VAS_op', 'std'),
        VAS_min = ('VAS_op', 'min'), VAS_max = ('VAS_op', 'max'))

    # Lateral breakout friction at each set along the pipeline route
    df_friction = df_pp[['pp_set', 'mulat_op']].groupby('pp_set', as_index = False).agg(
        mulat_mean = ('mulat_op', 'mean'), mulat_std = ('mulat_op', 'std'),
        mulat_min = ('mulat_op', 'min'), mulat_max = ('mulat_op', 'max'))

    # Merge df_buckling and df_vas on 'pp_set'
    df_set = pd.merge(df_pp_set, df_buckling, on = 'pp_set', how = 'outer')

    # Merge df_buckling and df_vas on 'pp_set'
    df_set = pd.merge(df_set, df_vas, on = 'pp_set', how = 'outer')
    df_set['VAS_mean'] = df_set['VAS_mean'].fillna(0.0)
    df_set['VAS_std'] = df_set['VAS_std'].fillna(0.0)
    df_set['VAS_min'] = df_set['VAS_min'].fillna(0.0)
    df_set['VAS_max'] = df_set['VAS_max'].fillna(0.0)

    # Determine characteristic VAS
    df_set = pp_char_vas(df_pp, df_buckling, df_set)

    # Merge merged_df and df_friction on 'pp_set' and determine characteristic friction
    df_set = pd.merge(df_set, df_friction, on = 'pp_set', how = 'outer')

    # Determine characteristic lateral breakout friction
    df_set = pp_char_fric(df_pp, df_buckling, df_set, prob_exceed_char_fric)

    # Change labels for print-out
    df_set = df_set.rename(columns = {
        'pp_set': 'Set Label',
        'KP_from': 'KP From (m)',
        'KP_to': 'KP To (m)',
        'no_simulations_with_buckles': 'Number of Simulations with Buckles per Set',
        'no_buckles': 'Number of Buckles per Set',
        'prob_buckling': 'Probability of Buckling',
        'prob_not_buckling': 'Probability of not Buckling',
        'VAS_mean': 'Mean of the VAS (m)',
        'VAS_std': 'Standard Deviation of the VAS (m)',
        'VAS_min': 'Minimum VAS (m)',
        'VAS_max': 'Maximum VAS (m)',
        'VAS_charac_conditional': 'Characteristic VAS, Conditional (m)',
        'VAS_charac_unconditional': 'Characteristic VAS, Unconditional (m)',
        'mulat_mean': 'Mean of the Lateral Breakout Friction',
        'mulat_std': 'Standard Deviation of the Lateral Breakout Friction',
        'mulat_min': 'Minimum Lateral Breakout Friction',
        'mulat_max': 'Maximum Lateral Breakout Friction',
        'mulat_charac_unconditional': 'Characteristic Lateral Breakout Friction, Buckles'})

    # Drop column for print-out
    df_set = df_set.drop(columns = 'mulat_charac_conditional')

    # Sort by KP From
    df_set = df_set.sort_values(by = 'KP From (m)')

    # Fill characteristic frictions at planned buckles with zero
    df_set['Characteristic Lateral Breakout Friction Probability'] = \
        prob_exceed_char_fric
    df_set.loc[df_set['Characteristic Lateral Breakout Friction, Buckles'] == 0.0,
               'Characteristic Lateral Breakout Friction Probability'] = 0.0

    # Define HE of the geotechnical friction
    df_scen['Lateral Breakout Friction, HE, Geotech'] = \
        df_scen.apply(lambda x: np.interp(1.0 - prob_exceed_char_fric,
                                          x['mul OP CDF Array'],
                                          x['mul OP Array']), axis = 1)
    df_set['Lateral Breakout Friction, HE, Geotech'] = \
        df_set.apply(lambda x: np.interp(x['KP From (m)'],
                                         df_scen['KP'],
                                         df_scen['Lateral Breakout Friction, HE, Geotech']),
                                         axis = 1)

    # Convert route type strings to descriptive representation
    df_scen_temp = df_scen.copy()

    df_scen_temp.loc[df_scen_temp['Route Type'] == 1, 'Route'] = 'Straight'
    df_scen_temp.loc[df_scen_temp['Route Type'] == 2, 'Route'] = 'Bend'
    df_scen_temp.loc[df_scen_temp['Route Type'] == 3, 'Route'] = 'Sleeper'
    df_scen_temp.loc[df_scen_temp['Route Type'] == 4, 'Route'] = 'RCM'

    # Assign route type to df_set
    for index, row in df_set.iterrows():
        df_set.loc[index, 'Route'] = df_scen_temp.loc[
            (df_scen_temp['KP'] > row['KP From (m)']) &
            (df_scen_temp['KP'] < row['KP To (m)']),
            'Route'].values[0]

    df_set.loc[(df_set['Route'] == 'Sleeper') | (df_set['Route'] == 'RCM'),
               'Characteristic Lateral Breakout Friction, Buckles'] = 0.0

    # Re-arrange columns
    df_set = df_set[['Set Label', 'KP From (m)', 'KP To (m)',
                     'Number of Simulations with Buckles per Set',
                     'Number of Buckles per Set',
                     'Probability of Buckling',
                     'Probability of not Buckling',
                     'Mean of the VAS (m)', 'Standard Deviation of the VAS (m)',
                     'Minimum VAS (m)', 'Maximum VAS (m)',
                     'Characteristic VAS Probability',
                     'Characteristic VAS, Conditional (m)',
                     'Characteristic VAS, Unconditional (m)',
                     'Mean of the Lateral Breakout Friction',
                     'Standard Deviation of the Lateral Breakout Friction',
                     'Minimum Lateral Breakout Friction',
                     'Maximum Lateral Breakout Friction',
                     'Characteristic Lateral Breakout Friction Probability',
                     'Characteristic Lateral Breakout Friction, Buckles',
                     'Lateral Breakout Friction, HE, Geotech']]

    df_set = df_set.fillna(0.0)
    df_set['Probability of not Buckling'] = 1.0 - df_set['Probability of Buckling']

    return df_set

def pp_eaf(df_pp_plot):

    """
    Converts units and renames columns for pipeline EAF plot DataFrame.

    Parameters
    ----------
    df_pp_plot : pandas DataFrame
        DataFrame containing pipeline plot data.

    Returns
    -------
    df_pp_plot: pandas DataFrame
        DataFrame with converted units and renamed columns.
    """

    # Convert the units of 'df_pp_plot' (N to kN)
    df_pp_plot[['CBF_ht', 'CBF_op', 'EAF_inst', 'EAF_ht',
             'EAF_p_op', 'EAF_op', 'EAF_op_unbuck']] /= 1000.0

    # Change labels for print-out
    df_pp_plot = df_pp_plot.rename(columns = {
        'KP': 'KP (m)',
        'CBF_ht': 'CBF Hydrotest (kN)',
        'CBF_op': 'CBF Operation (kN)',
        'EAF_inst': 'EAF Installation [RLT] (kN)',
        'EAF_ht': 'EAF Hydrotest (kN)',
        'EAF_p_op': 'EAF Operation [Pressure Only] (kN)',
        'EAF_op': 'EAF Operation (kN)',
        'EAF_op_unbuck': 'EAF Operation [without Buckling] (kN)'
        })

    # Drop column for print-out
    df_pp_plot = df_pp_plot.drop(columns = 'beta2')

    return df_pp_plot

def pp_raw(df):

    """
    Converts units and renames columns of the DataFrame containing the raw data
    from the BuckPy simulations.

    Parameters
    ----------
    df : pandas DataFrame
        DataFrame containing raw data from the BuckPy simulations.

    Returns
    -------
    df : pandas DataFrame
        DataFrame with converted units and renamed columns.
    """

    # Change labels for print-out
    df = df.rename(columns = {
        'isim': 'Simulation Number',
        'KP': 'KP (m)',
        'route_type': 'Section Type',
        'muax': 'Axial Residual Friction Factor, Operation',
        'mulat_op': 'Lateral Breakout Friction Factor, Operation',
        'HOOS': 'HOOS Factor',
        'CBF_op': 'CBF Operation (kN)',
        'VAS_op': 'VAS Operation (m)'
        })

    # Convert units of the CBF (N to kN)
    df['CBF Operation (kN)'] /= 1000.0

    # Rename section types
    df['Section Type'] = df['Section Type'].astype(object)
    df.loc[df['Section Type'] == 1, 'Section Type'] = 'Straight'
    df.loc[df['Section Type'] == 2, 'Section Type'] = 'Bend'
    df.loc[df['Section Type'] == 3, 'Section Type'] = 'Sleeper'
    df.loc[df['Section Type'] == 4, 'Section Type'] = 'RCM'

    # Select the first 10000 rows to optimise the size of the Excel file
    #TODO: why? if Excel is limited, let's export it to something else as it could be useful to have all case for separate post-processing
    df = df.iloc[:10000]

    return df

def pp_save(output_combination, output_file_name, *args):

    """
    Saves DataFrames to an Excel file with specified formatting.

    Parameters
    ----------
    output_combination : Boolean
        Switch to write the most frequent combination set of buckles in the result file.
    output_file_name : str
        Name of the output Excel file.
    df_elem : pandas DataFrame
        DataFrame containing element data.
    df_sets : pandas DataFrame
        DataFrame containing set data.
    df_no_buckles : pandas DataFrame
        DataFrame containing data related to the number of buckles.
    df_pp_plot : pandas DataFrame
        DataFrame containing force profile data.
    df_pp_buckle_prop : pandas DataFrame
        DataFrame containing raw data related to buckling properties.
    df_comb_per_set : pandas DataFrame
        DataFrame containing raw data related to KP set combinations based on post-processing set.
    df_comb_per_section : pandas DataFrame
        DataFrame containing raw data related to KP set combinations based on route point id.

    Returns
    -------
    None
    """

    if output_combination:
        df_elem, df_sets, df_no_buckles, df_pp_plot, df_pp_buckle_prop,\
            df_comb_per_set, df_comb_per_section = args
    else:
        df_elem, df_sets, df_no_buckles, df_pp_plot, df_pp_buckle_prop = args

    writer = pd.ExcelWriter(output_file_name)
    pandas.io.formats.excel.ExcelFormatter.header_style = None

    # Convert DataFrames to Excel objects
    df_elem.to_excel(writer, sheet_name = 'Elements', index = False,
                     startrow = 1, header = False)
    df_sets.to_excel(writer, sheet_name = 'Sets', index = False,
                     startrow = 1, header = False)
    df_no_buckles.to_excel(writer, sheet_name = 'No Buckles', index = False,
                           startrow = 1, header = False)
    df_pp_plot.to_excel(writer, sheet_name = 'Force Profiles', index = False,
                        startrow = 1, header = False)
    df_pp_buckle_prop.to_excel(writer, sheet_name = 'Raw Data', index = False,
                               startrow = 1, header = False)

    if output_combination:
        df_comb_per_set.to_excel(writer, sheet_name = 'Comb Buckles per Set',
                                 startrow = 1, header = False)
        df_comb_per_section.to_excel(writer, sheet_name = 'Comb Buckles per Section',
                                     startrow = 1, header = False)

    # Get the workbook and worksheet objects.
    workbook = writer.book
    worksheet1 = writer.sheets['Elements']
    worksheet2 = writer.sheets['Sets']
    worksheet3 = writer.sheets['No Buckles']
    worksheet4 = writer.sheets['Force Profiles']
    worksheet5 = writer.sheets['Raw Data']

    if output_combination:
        worksheet6 = writer.sheets['Comb Buckles per Set']
        worksheet7 = writer.sheets['Comb Buckles per Section']

    # Add generic cell formats to Excel file
    formatc1 = workbook.add_format({'num_format': '#,##0', 'align': 'center',
                                    'valign': 'vcenter', 'text_wrap': True})
    formatc2 = workbook.add_format({'num_format': '#,##0.0', 'align': 'center',
                                    'valign': 'vcenter', 'text_wrap': True})
    formatc3 = workbook.add_format({'num_format': '0.000', 'align': 'center',
                                    'valign': 'vcenter', 'text_wrap': True})
    formath1 = workbook.add_format({'num_format': '#,###', 'bold': True, 'border': 1,
                                    'bg_color': '#C0C0C0', 'align': 'center',
                                    'valign': 'vcenter', 'text_wrap': True})

    # Set the column width and format of the Excel worksheets
    worksheet1.set_column('A:B', 12.5, formatc1)
    worksheet1.set_column('C:D', 12.5, formatc3)
    worksheet1.set_column('E:H', 12.5, formatc2)
    worksheet1.set_column('I:L', 12.5, formatc3)

    worksheet2.set_column('A:E', 12.5, formatc1)
    worksheet2.set_column('F:G', 12.5, formatc3)
    worksheet2.set_column('H:K', 12.5, formatc2)
    worksheet2.set_column('L:L', 12.5, formatc3)
    worksheet2.set_column('M:N', 12.5, formatc2)
    worksheet2.set_column('O:U', 12.5, formatc3)

    worksheet3.set_column('A:B', 12.5, formatc1)
    worksheet3.set_column('C:D', 12.5, formatc3)

    worksheet4.set_column('A:A', 12.5, formatc1)
    worksheet4.set_column('B:H', 12.5, formatc2)

    worksheet5.set_column('A:C', 12.5, formatc1)
    worksheet5.set_column('D:F', 12.5, formatc3)
    worksheet5.set_column('G:H', 12.5, formatc2)

    if output_combination:
        worksheet6.set_column('A:C', 12.5, formatc1)
        worksheet6.set_column('D:D', 12.5, formatc3)
        worksheet6.set_column('E:AZ', 12.5, formatc1)

        worksheet7.set_column('A:C', 12.5, formatc1)
        worksheet7.set_column('D:D', 12.5, formatc3)
        worksheet7.set_column('E:AZ', 12.5, formatc1)

    # Write the column hearders with the defined format
    for col_num, value in enumerate(df_elem.columns.values):
        worksheet1.write(0, col_num, value, formath1)
    for col_num, value in enumerate(df_sets.columns.values):
        worksheet2.write(0, col_num, value, formath1)
    for col_num, value in enumerate(df_no_buckles.columns.values):
        worksheet3.write(0, col_num, value, formath1)
    for col_num, value in enumerate(df_pp_plot.columns.values):
        worksheet4.write(0, col_num, value, formath1)
    for col_num, value in enumerate(df_pp_buckle_prop.columns.values):
        worksheet5.write(0, col_num, value, formath1)

    if output_combination:
        for col_num, value in enumerate(df_comb_per_set.columns.values):
            worksheet6.write(0, col_num + 1, value[0], formath1)
            worksheet6.write(1, col_num + 1, value[1], formath1)
            # Merge header cells for the 3 columns in the first and second row
            if col_num <= 2:
                worksheet6.merge_range(0, col_num + 1, 1, col_num + 1, value[1], formath1)
        # Merge header cells for the 'Number of Buckles' columns in the first row
        worksheet6.merge_range(0, 4, 0, len(df_comb_per_set.columns.values),
                               df_comb_per_set.columns.levels[0][1], formath1)

        for col_num, value in enumerate(df_comb_per_section.columns.values):
            worksheet7.write(0, col_num + 1, value[0], formath1)
            worksheet7.write(1, col_num + 1, value[1], formath1)
            # Merge header cells for the 3 columns in the first and second row
            if col_num <= 2:
                worksheet7.merge_range(0, col_num + 1, 1, col_num + 1, value[1], formath1)
        # Merge header cells for the 'Number of Buckles' columns in the first row
        worksheet7.merge_range(0, 4, 0, len(df_comb_per_section.columns.values),
                               df_comb_per_section.columns.levels[0][1], formath1)

    # Close the Excel writer and output the Excel file
    writer.close()

def pp_outputs(output_file_name, n_sim, output_combination, df_pp_buckle_prop,
               df_pp_set, df_pp_plot, prob_exceed_char_fric, df_scen):

    """
    Perform post-processing of analysis outputs.

    Parameters
    ----------
    output_file_name : str
        Name of the output Excel file
    n_sim : int
        Number of simulations.
    output_combination : Boolean
        Switch to write the most frequent combination set of buckles in the result file.
    df_pp_buckle_prop : pandas DataFrame
        DataFrame containing post-processed buckling properties.
    df_pp_set : DataFrame
        Definition of element sets for post-processing outputs.
    df_pp_plot : pandas DataFrame
        DataFrame containing post-processed plot data.
    prob_exceed_char_fric : float
        Probability of exceedance associated with the characteristic lateral breakout friction.
    df_pp_set : DataFrame
        Definition of element sets for post-processing outputs.
    df_scen : DataFrame
        Dataframe containing the design data along the pipeline
        route (mesh) that remains constant among deterministic and
        Monte-Carlo simulations.

    Returns
    -------
    df_no_buckles : pandas DataFrame
        DataFrame containing post-processed statistics about the number of buckles
        along the pipeline.
    df_sets : pandas DataFrame
        DataFrame containing post-processed statistics grouped by pipeline sets.
    """

    # Dataframe containing the raw data
    df_pp_buckle_prop = df_pp_buckle_prop.sort_values(by = ['KP', 'isim'])
    df_pp = pd.merge_asof(left = df_pp_buckle_prop, right = df_pp_set,
                          left_on = 'KP', right_on = 'KP_from')

    # Probability of buckling, VAS and lateral breakout friction sorted by element
    df_elem = pp_elem(df_pp, n_sim)

    # Distribution of the expected number of buckles along the pipeline
    df_no_buckles = pp_no_buckles(df_pp, n_sim)

    # Probability of buckling, VAS and lateral breakout friction sorted by post-processing set
    df_sets = pp_sets(df_pp, n_sim, prob_exceed_char_fric, df_pp_set, df_scen)

    # Post-processing of 'df_pp_plot' for print-out
    df_pp_plot = pp_eaf(df_pp_plot)

    # Post-processing of 'df_pp_buckle_prop' for print-out
    df_pp_buckle_prop = pp_raw(df_pp_buckle_prop)

    if output_combination:
        # Calculate the most frequent combination of KP set with buckles
        df_comb_per_set = pp_comb_buckles_per_set(df_pp, df_pp_set, n_sim)
        df_comb_per_section = pp_comb_buckles_per_section(df_pp, df_scen, n_sim)

        # Save key outputs to Excel file
        pp_save(output_combination, output_file_name, df_elem, df_sets, df_no_buckles,
                df_pp_plot, df_pp_buckle_prop, df_comb_per_set, df_comb_per_section)
    else:
        # Save key outputs to Excel file
        pp_save(output_combination, output_file_name, df_elem, df_sets, df_no_buckles,
                df_pp_plot, df_pp_buckle_prop)

    return df_no_buckles, df_sets

def pp_plots(plot_file_name, df_scen, df_plot, df_vap_plot, df_no_buckles, df_sets,
             prob_exceed_char_fric):

    """
    Plot deterministic and probabilistic results
    
    Parameters
    ----------
    plot_file_name : str
        Name of the \*.png file
    df_scen : DataFrame
        Dataframe containing the design data along the pipeline
        route (mesh) that remains constant among deterministic and
        Monte-Carlo simulations.
    df_plot : DataFrame
        Definition on assessed mesh of CBF and EAF in different conditions.
        for case to plot 
    df_vap_plot : DataFrame
        Definition of virtual anchor points for case to plot.
        Columns: ['ielt VAP', 'KP VAP', 'ESF VAP'].
    df_no_buckles : DataFrame
        Probability of number of buckles over pipeline.
    df_sets : DataFrame
        Probability of buckling and characteristic VAS and friction factors by set.
    prob_exceed_char_fric : float
        Probability of exceedance for characteristic friction factors.
    plot_file_name : str
        File name where plots are to be saved.
    """

    # Convert the units of 'df_plot', 'df_vap_plot' & 'df_scen' (m to km and N to kN)
    df_plot[['KP']] /= 1000.0
    df_vap_plot[['KP VAP', 'ESF VAP']] /= 1000.0
    df_scen[['KP', 'FRF OP Pressure', 'FRF OP Temperature']] /= 1000.0

    # Create arrays to plot buckling probability, characteristic VAS and characteristic friction
    np_kp = np.array([df_sets.iloc[0]['KP From (m)'] / 1000.0])
    np_prob = np.array([0.0])
    np_vas_cond = np.array([0.0])
    np_vas_uncond = np.array([0.0])
    np_mul_buckle = np.array([0.0])
    for index, row in df_sets.iterrows():
        np_kp = np.append(np_kp, np.append(
            row['KP From (m)'] / 1000.0,
            row['KP To (m)'] / 1000.0))
        np_prob = np.append(np_prob, np.append(
            100.0 * row['Probability of Buckling'],
            100.0 * row['Probability of Buckling']))
        np_vas_cond = np.append(np_vas_cond, np.append(
            row['Characteristic VAS, Conditional (m)'],
            row['Characteristic VAS, Conditional (m)']))
        np_vas_uncond = np.append(np_vas_uncond, np.append(
            row['Characteristic VAS, Unconditional (m)'],
            row['Characteristic VAS, Unconditional (m)']))
        np_mul_buckle = np.append(np_mul_buckle, np.append(
            row['Characteristic Lateral Breakout Friction, Buckles'],
            row['Characteristic Lateral Breakout Friction, Buckles']))
        if index == df_sets.shape[0] - 1:
            np_kp = np.append(np_kp, row['KP To (m)'] / 1000.0)
            np_prob = np.append(np_prob, 0.0)
            np_vas_cond = np.append(np_vas_cond, 0.0)
            np_vas_uncond = np.append(np_vas_uncond, 0.0)
            np_mul_buckle = np.append(np_mul_buckle, 0.0)

    # Create an array to plot the HE of the geotechnical lateral breakdown friction
    np_mul_kp = np.empty(0)
    np_mul_geotech = np.empty(0)
    for index, row in df_scen.iterrows():
        # df_scen has at least 2 points, no need to double the points in append functions
        np_mul_kp = np.append(np_mul_kp, row['KP'])
        mul_geotech = np.interp(1.0 - prob_exceed_char_fric,
                                row['mul OP CDF Array'], row['mul OP Array'])
        np_mul_geotech = np.append(np_mul_geotech, mul_geotech)

    # Generate matplolib figure
    fig = plt.figure()
    dpi_size = 110
    fig.set_size_inches(19.2 * 100 / dpi_size, 10.8 * 100 / dpi_size)
    gs = GridSpec(nrows = 2, ncols = 3)

    # Plot effective axial force profiles from selected case
    a1=fig.add_subplot(gs[0, :])
    a1.plot(df_plot['KP'], df_plot['EAF_inst'],
            label = 'EAF Installation', color = 'C1')
    a1.plot(df_plot['KP'], df_plot['EAF_ht'],
            label = 'EAF Hydrotest', color = 'C2')
    a1.plot(df_plot['KP'], df_plot['EAF_p_op'],
            label = 'EAF Operation (Pressure Only)', color = 'C3')
    a1.plot(df_plot['KP'], df_plot['EAF_op'],
            label = 'EAF Operation', color = 'C4')
    a1.plot(df_plot['KP'], df_plot['EAF_op_unbuck'],
            label = 'EAF Operation (without Buckling)', color = 'C4', linestyle = ':')

    # Plot intermediate force profile during temperature application
    for i in range(1, 21):
        # Shouldnt overwrite existing df_plot['EAF_inst'], separate dataframe used instead
        eaf_interim = df_scen['FRF OP Pressure'] + (i / 20) * df_scen['FRF OP Temperature']
        eaf_interim=np.where(eaf_interim < df_plot['EAF_op_unbuck'].to_numpy(), eaf_interim, np.nan)
        a1.plot(df_plot['KP'], eaf_interim, color = 'C4', linestyle = '--', alpha = 0.25)

    #TODO: Indeed, however different sections (routes, straight, sleepers...) can have different ones
    # and it's interresting to see if area buckle "earlier" than other
    #? Block commented as all buckling forces per section are constant in the deterministic case
    # Plot buckling susceptibility areas and actual buckle locations
    # a1.scatter(df_plot.loc[
    #    df_plot['CBF_op'] < df_plot['EAF_op_unbuck'], 'KP'],
    #            df_plot.loc[
    #    df_plot['CBF_op'] < df_plot['EAF_op_unbuck'], 'CBF_op'],
    #            label = 'CBF operation', marker = '.', color = 'C4')

    # Plot VAP
    a1.scatter(df_vap_plot['KP VAP'], df_vap_plot['ESF VAP'],
               marker = '8', c = 'none', edgecolors = 'C3', label = 'VAP')
    a1.set_xlabel('KP [km]')
    a1.set_ylabel('Effective Force [kN]')
    a1.legend()
    a1.grid()

    # Plot distribution of number of buckles
    a2 = fig.add_subplot(gs[1, 0])
    a2.plot(df_no_buckles['Number of Buckles'],
            100.0 * df_no_buckles['Probability of Buckling'], color = 'C1')
    a2.set_xlabel('Number of Buckles')
    a2.set_ylabel('Probability [%]')
    a2.grid()

    # Plot lateral friction factor versus location
    a3 = fig.add_subplot(gs[1, 1])
    a3.plot(np_kp, np_mul_buckle,
            label = f'P{int(100 * prob_exceed_char_fric)} Buckle Friction', color = 'C1')
    a3.plot(np_mul_kp, np_mul_geotech,
            label = f'P{int(100 * prob_exceed_char_fric)} Geotech Friction', color = 'C2')
    a3.set_xlabel('KP [km]')
    a3.set_ylabel('Lateral Breakout Friction Factor (Operation)')
    a3.legend()
    a3.grid()

    # Plot probability of buckling and characteristic VAS
    a4 = fig.add_subplot(gs[1, 2])
    a4_twin = a4.twinx()
    # a4.plot(np_kp, np_vas_cond, label = 'Conditional VAS',
    #         color = 'C1')
    a4.plot(np_kp, np_vas_uncond, label = 'Unconditional VAS',
            color = 'C2')
    a4_twin.plot(np_kp, np_prob, label = 'Probability of Buckling', linestyle = ':',
                 color = 'C3')
    a4.set_xlabel('KP [km]')
    a4.set_ylabel('Characteristic VAS [m]')
    a4_twin.set_ylabel('Buckling Probability [%]')
    line4, label4 = a4.get_legend_handles_labels()
    line4_twin, label4_twin = a4_twin.get_legend_handles_labels()
    a4.legend(line4 + line4_twin, label4 + label4_twin)
    a4.grid()

    fig_manager=plt.get_current_fig_manager()
    try:
        fig_manager.window.state('zoomed')
    except AttributeError:
        pass
    try:
        fig_manager.window.showMaximized()
    except AttributeError:
        pass
    plt.subplots_adjust(
        left = 0.1, bottom = 0.1, right = 0.95, top = 0.925, wspace = 0.225, hspace = 0.2)
    plt.savefig(plot_file_name, dpi = dpi_size)
    # plt.show()
    plt.close()

def pp_buckpy(work_dir, input_file_name, pipeline_id, scenario_no, prob_exceed_char_fric,
              df_pp_plot, df_vap_plot, df_pp_buckle_prop, df_scen, df_pp_set,
              n_sim, output_combination, bl_verbose = False):

    """
    Post-processing of probabilistic buckling results.

    Parameters
    ----------
    work_dir : str
        The working directory where the analysis files are located.
    input_file_name : str
        The name of the input file.
    pipeline_id : str
        Identifier of the pipeline.
    scenario_no : int
        The scenario number.
    prob_exceed_char_fric : float
        Probability of exceedance for the calculation of the characteristic friction factor.
    df_pp_plot : DataFrame
        Definition on assessed mesh of CBF and EAF in different conditions for case to plot.
    df_vap_plot : DataFrame
        Definition of virtual anchor points for case to plot.
    df_pp_buckle_prop : DataFrame
        Results for all buckles triggered.
    df_scen : DataFrame
        Dataframe containing the design data along the pipeline route (mesh) that remains
        constant among deterministic and Monte-Carlo simulations.
    df_pp_set : DataFrame
        Definition of element sets for post-processing outputs.
    n_sim : int
        Number of Monte-Carlo simulations to be run.
    output_combination : Boolean
        Switch to write the most frequent combination set of buckles in the result file.
    """

    # Starting time of the post-processing module
    start_time = time.time()

    # Print in the terminal that the post-processing of the results has started
    if bl_verbose:
        print("4. Post-process results")

    # Calculate probabilistic outputs and save outputs to Excel file
    output_file_name = f"{work_dir}/{input_file_name.split('.')[0]}_{pipeline_id}_scen{scenario_no}_outputs.xlsx"
    df_prob_n_buckle, df_prob_set = pp_outputs(output_file_name, n_sim, output_combination,
        df_pp_buckle_prop, df_pp_set, df_pp_plot, prob_exceed_char_fric, df_scen)

    # Print in the terminal the time taken to post-process results
    if bl_verbose:
        print(f'   Time taken to post-process results: {time.time() - start_time:.1f}s')

    # Plot post-processed results and save figure to file
    plot_file_name = f"{work_dir}/{input_file_name.split('.')[0]}_{pipeline_id}_scen{scenario_no}_plots-1.png"
    pp_plots(plot_file_name, df_scen, df_pp_plot, df_vap_plot, df_prob_n_buckle, df_prob_set,
             prob_exceed_char_fric)
