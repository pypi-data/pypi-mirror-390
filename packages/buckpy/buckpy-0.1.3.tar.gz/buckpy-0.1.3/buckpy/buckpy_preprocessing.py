"""
This module contains the pre-processing functions of BuckPy.
"""

import time
import numpy as np
import pandas as pd
from scipy.stats import norm, lognorm
from .buckpy_variables import KP_TO

'''
This module provides classes and functions for lateral buckling calculations and friction factor
distribution fitting for subsea pipelines.

**Features:**

- The `LBDistributions` class implements lognormal distribution fitting for geotechnical friction
  factors, supporting low, best, and high estimates (LE, BE, HE) and multiple fit types.
- Designed for use in pipeline lateral buckling reliability analysis and geotechnical parameter
  estimation.
- All calculations are vectorized using NumPy and leverage SciPy for statistical fitting.

.. raw:: html

   <hr style="height:6px; background-color:#888; border:none; margin:1.5em 0;" />

'''

import numpy as np
from scipy.stats import lognorm
from scipy.optimize import minimize

class LBDistributions: # pylint: disable=too-many-instance-attributes, too-many-arguments
    """
    Class for lateral buckling calculations, including friction factor distribution fitting.

    Parameters
    ----------
    friction_factor_le : float, optional
        Low estimate (LE) friction factor, representing the 5th percentile.
    friction_factor_be : float, optional
        Best estimate (BE) friction factor, representing the 50th percentile.
    friction_factor_he : float, optional
        High estimate (HE) friction factor, representing the 95th percentile.
    friction_factor_fit_type : str, optional
        Type of fit to perform: 'LE_BE_HE', 'LE_BE', or 'BE_HE'.
    """
    def __init__(
            self,
            *,
            friction_factor_le,
            friction_factor_be,
            friction_factor_he,
            friction_factor_fit_type
        ):
        """
        Initialize with geotechnical friction factor estimates and fit type.
        """
        self.friction_factor_le = np.asarray(friction_factor_le, dtype = float)
        self.friction_factor_be = np.asarray(friction_factor_be, dtype = float)
        self.friction_factor_he = np.asarray(friction_factor_he, dtype = float)
        self.friction_factor_fit_type = np.asarray(friction_factor_fit_type, dtype = object)

    def friction_distribution(self):
        """
        Compute the parameters of the lognormal friction factor distribution (axial or lateral)
        by minimizing the root mean square error (RMSE) between geotechnical estimates and
        back-calculated friction factors from the lognormal distribution.

        Returns
        -------
        mean_friction : np.ndarray
            Array of mean values of the lognormal friction factor distribution.
        std_friction : np.ndarray
            Array of standard deviation values of the lognormal friction factor distribution.
        location_param : np.ndarray
            Array of location parameters of the lognormal friction factor distribution.
        scale_param : np.ndarray
            Array of scale parameters of the lognormal friction factor distribution.
        le_fit : np.ndarray
            Array of fitted LE values.
        be_fit : np.ndarray
            Array of fitted BE values.
        he_fit : np.ndarray
            Array of fitted HE values.
        rmse : np.ndarray
            Array of RMSE values for the best fit type.
        Notes
        -----
        The function calculates the parameters of the lognormal friction factor distribution
        based on LE at 5th percentile, BE at 50th percentile, and HE at 95th percentile

        Examples
        --------
        >>> lb = LBDistributions(
        ...     friction_factor_le=[0.5],
        ...     friction_factor_be=[1.0],
        ...     friction_factor_he=[1.5],
        ...     friction_factor_fit_type=['LE_BE_HE']
        ... )
        >>> lb.friction_distribution()
        (array([0.9684083]), array([0.30043236]), array([-0.07804666]), array([0.3031342]), array([0.56177265]), array([0.92492127]), array([1.52282131]), array([0.05765844]))
        """
        # Initialize lists to store results
        mean_friction_list = []
        std_friction_list = []
        location_param_list = []
        scale_param_list = []
        le_fit_list = []
        be_fit_list = []
        he_fit_list = []
        rmse_list = []

        # Define the objective function
        def objective(
                params,
                friction_factor_le,
                friction_factor_be,
                friction_factor_he,
                friction_factor_fit_type
            ):
            location_param, scale_param = params

            if friction_factor_fit_type == 'LE_BE_HE':
                le_fit = lognorm(scale_param, 0.0, np.exp(location_param)).ppf(0.05)
                be_fit = lognorm(scale_param, 0.0, np.exp(location_param)).ppf(0.50)
                he_fit = lognorm(scale_param, 0.0, np.exp(location_param)).ppf(0.95)
                error = np.sqrt(
                    ((le_fit - friction_factor_le)**2 + (be_fit - friction_factor_be)**2
                     + (he_fit - friction_factor_he)**2) / 3.0
                )
            elif friction_factor_fit_type == 'LE_BE':
                le_fit = lognorm(scale_param, 0.0, np.exp(location_param)).ppf(0.05)
                be_fit = lognorm(scale_param, 0.0, np.exp(location_param)).ppf(0.50)
                error = np.sqrt(
                    ((le_fit - friction_factor_le)**2 + (be_fit - friction_factor_be)**2) / 2.0
                )
            elif friction_factor_fit_type == 'BE_HE':
                be_fit = lognorm(scale_param, 0.0, np.exp(location_param)).ppf(0.50)
                he_fit = lognorm(scale_param, 0.0, np.exp(location_param)).ppf(0.95)
                error = np.sqrt(
                    ((be_fit - friction_factor_be)**2 + (he_fit - friction_factor_he)**2) / 2.0
                )
            else:
                error = np.nan
            return error

        # Loop through the friction factor arrays
        for _, (
            friction_factor_le,
            friction_factor_be,
            friction_factor_he,
            friction_factor_fit_type
        ) in enumerate(
            zip(
                self.friction_factor_le,
                self.friction_factor_be,
                self.friction_factor_he,
                self.friction_factor_fit_type
            )
        ):
            initial_location = np.mean(
                [np.log(friction_factor_le),
                 np.log(friction_factor_be),
                 np.log(friction_factor_he)]
            )
            initial_scale = np.std(
                [np.log(friction_factor_le),
                 np.log(friction_factor_be),
                 np.log(friction_factor_he)],
                ddof=1
            )
            initial_guess = [initial_location, initial_scale]

            # Use minimize to find the parameters that minimize RMSE
            result = minimize(
                objective,
                initial_guess,
                args=(
                    friction_factor_le,
                    friction_factor_be,
                    friction_factor_he,
                    friction_factor_fit_type
                ),
                method='Nelder-Mead'
            )
            location_param, scale_param = result.x

            # Calculate lognormal parameters based on the optimized lognormal distribution
            mean_friction = np.exp(location_param + scale_param**2 / 2)
            std_friction = np.sqrt((np.exp(scale_param**2) - 1) * \
                                   np.exp(2 * location_param + scale_param**2))

            # Calculate the fitted values
            le_fit = lognorm(scale_param, 0.0, np.exp(location_param)).ppf(0.05)
            be_fit = lognorm(scale_param, 0.0, np.exp(location_param)).ppf(0.50)
            he_fit = lognorm(scale_param, 0.0, np.exp(location_param)).ppf(0.95)

            # Calculate RMSE
            if friction_factor_fit_type == 'LE_BE_HE':
                rmse = np.sqrt(
                    ((le_fit - friction_factor_le)**2 + (be_fit - friction_factor_be)**2 +\
                                (he_fit - friction_factor_he)**2) / 3.0
                )
            elif friction_factor_fit_type == 'LE_BE':
                rmse = np.sqrt(
                    ((le_fit - friction_factor_le)**2 + (be_fit - friction_factor_be)**2) / 2.0
                )
            elif friction_factor_fit_type == 'BE_HE':
                rmse = np.sqrt(
                    ((be_fit - friction_factor_be)**2 + (he_fit - friction_factor_he)**2) / 2.0
                )
            else:
                rmse = np.nan

            # Append results for this iteration
            mean_friction_list.append(mean_friction)
            std_friction_list.append(std_friction)
            location_param_list.append(location_param)
            scale_param_list.append(scale_param)
            le_fit_list.append(le_fit)
            be_fit_list.append(be_fit)
            he_fit_list.append(he_fit)
            rmse_list.append(rmse)

        # Convert lists to NumPy arrays
        mean_friction = np.array(mean_friction_list)
        std_friction = np.array(std_friction_list)
        location_param = np.array(location_param_list)
        scale_param = np.array(scale_param_list)
        le_fit = np.array(le_fit_list)
        be_fit = np.array(be_fit_list)
        he_fit = np.array(he_fit_list)
        rmse = np.array(rmse_list)

        return (
            mean_friction,
            std_friction,
            location_param,
            scale_param,
            le_fit,
            be_fit,
            he_fit,
            rmse
        )

def calc_expand_kp(df, kp_col):

    '''
    Function to expand the KP array with 1000 intervals from 1000 to nearest maximum KP.

    Parameters
    ----------
    df : pandas Dataframe
        Dataframe containing the original KP values.
    kp_col : string
        The column name of the KP values to expand.

    Returns
    -------
    df : pandas Dataframe
        Dataframe containing the expanded KP values.
    '''

    # Rename kp_col to 'KP From'
    df = df.rename(columns = {kp_col: 'KP From'})

    # Expand the KP array with 1000 intervals from 1000 to nearest maximum KP
    max_kp = np.floor(df['KP From'].max() / 1000.0) * 1000.0
    kp_array = np.arange(1000, max_kp + 1.0, 1000)

    # Create a dataframe for the expanded kp
    df_expand = pd.DataFrame({'Point ID From': [np.nan] * len(kp_array), 'KP From': kp_array})
    df = pd.concat([df, df_expand], ignore_index = True).sort_values(
        by = 'KP From').drop_duplicates('KP From').reset_index(drop = True).ffill()

    # Calculate relative length between KP and KP To
    df['KP To'] = df['KP From'].shift(-1)
    df = df.dropna()
    df['Length'] = df['KP To'] - df['KP From']

    # Calculate element number and element size
    df['Elem No.'] = np.ceil(df['Length'] / 100.0)
    df['Elem Size'] = df['Length'] / df['Elem No.']

    return df

def calc_element_array(df):

    '''
    Function to create element array based on KP, KP TO and element number.

    Parameters
    ----------
    df : pandas Dataframe
        Dataframe containing the expanded KP values.

    Returns
    -------
    df : pandas Dataframe
        Dataframe containing the elements between each KP value.
    '''

    # Create the elements between each KP points
    elem_array = np.empty(0)
    elem_array = df.apply(lambda x: pd.Series(np.append(elem_array, np.linspace(
        x['KP From'], x['KP To'], int(x['Elem No.'] + 1.0)))), axis = 1)

    # Convert the element dataframe to np array and flatten
    elem_array = elem_array.to_numpy().flatten()

    # Remove duplicated values at 1000*n and np.nan
    elem_array = np.unique(elem_array)
    elem_array = elem_array[~np.isnan(elem_array)]

    return elem_array

def calc_kp_interpolation(elem_array, df_oper):

    '''
    Function to interpolate the RLT, pressure and temperature using KP and operating profile.

    Parameters
    ----------
    elem_array : np Array
        Array containing the kp value of the elements.
    df_oper : pandas Dataframe
        Dataframe containing the original operating profiles data.

    Returns
    -------
    df : pandas Dataframe
        Dataframe containing the interpolated operating profiles data.
    '''

    # Interpolate operating profile based on KP
    df = pd.DataFrame({'KP': elem_array})
    df['Pressure Installation'] = np.interp(
        df['KP'], df_oper['KP'], df_oper['Pressure Installation'])
    df['Pressure Hydrotest'] = np.interp(
        df['KP'], df_oper['KP'], df_oper['Pressure Hydrotest'])
    df['Pressure Operation'] = np.interp(
        df['KP'], df_oper['KP'], df_oper['Pressure Operation'])
    df['Temperature Installation'] = np.interp(
        df['KP'], df_oper['KP'], df_oper['Temperature Installation'])
    df['Temperature Hydrotest'] = np.interp(
        df['KP'], df_oper['KP'], df_oper['Temperature Hydrotest'])
    df['Temperature Operation'] = np.interp(
        df['KP'], df_oper['KP'], df_oper['Temperature Operation'])
    df['RLT'] = np.interp(df['KP'], df_oper['KP'], df_oper['RLT'])

    return df

def calc_operating_profiles(df, df_route, pipeline_set, loadcase_set):

    """
    Calculate operating profiles data and process it.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing the operating profiles data.
    df_route : pandas.DataFrame
        DataFrame containing route data and calculated route data.
    pipeline_set : str
        Identifier of the pipeline set.
    loadcase_set : str
        Identifier of the loadcase set.

    Returns
    -------
    df : pandas.DataFrame
        DataFrame containing the operating profiles data and calculated operating data.
    """

    # Filter df DataFrame based on pipeline_set and loadcase_set
    df_profile = df.loc[(df['Pipeline'] == pipeline_set) & (df['Loadcase Set'] == loadcase_set)]

    # Select the 'Point ID From' and 'KP To' columns
    df_route = df_route[['Point ID From', 'KP To']].reset_index(drop = True)

    # Add the end row of route and the start KP
    end_row = pd.DataFrame({'Point ID From': 'End', 'KP To': np.nan}, index = [99999])
    df_route = pd.concat([df_route, end_row], ignore_index = True)

    # Shift KP column 1 downwards and assign 0.0 to the first KP
    df_route['KP To'] = df_route['KP To'].shift().fillna(0.0)

    # Expand the KP array with 1000 intervals from 1000 to nearest maximum KP
    df_route = calc_expand_kp(df_route, 'KP To')

    # Create the elements between each KP points
    elem_array = calc_element_array(df_route)

    # Interpolate the RLT, pressure and temperature using KP and operating profile
    df = calc_kp_interpolation(elem_array, df_profile)

    # Insert pipeline_set and loadcase_set columns as the first and second columns
    df.insert(0, 'Pipeline', [pipeline_set] * df.shape[0])
    df.insert(1, 'Loadcase Set', [loadcase_set] * df.shape[0])

    return df

def calc_route_data(df, layout_set, pipeline_set):

    """
    Extract and process route data for calculations.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing route data.
    layout_set : str
        Identifier of the layout set.
    pipeline_set : str
        Identifier of the pipeline set.

    Returns
    -------
    df : pandas.DataFrame
        DataFrame containing route data and calculated route data.
    df_ends : pandas.DataFrame 
        DataFrame containing end boundary conditions.

    Notes
    -----
    This function extracts route ends and route data based on pipeline_set and layout_set. It
    selects specific columns for route ends data. Route Type is converted from string to
    float for numerical representation. Route ends data is converted to a NumPy array for
    efficient processing.
    """

    # Extract route ends and route data based on pipeline_set and layout_set
    df_ends = df.loc[(df['Pipeline'] == pipeline_set) &
                             (df['Layout Set'] == layout_set)].iloc[[0, -1]]
    df = df.loc[(df['Pipeline'] == pipeline_set) &
                        (df['Layout Set'] == layout_set)].iloc[1:-1]

    # Select specific columns for route ends data
    df_ends = df_ends[['Route Type', 'KP From', 'KP To', 'Reaction Installation',
                                   'Reaction Hydrotest', 'Reaction Operation']]

    # Convert 'Route Type' from string to float for numerical representation
    df_ends.loc[df_ends['Route Type'] == 'Spool', 'Route Type'] = 1
    df_ends.loc[df_ends['Route Type'] == 'Fixed', 'Route Type'] = 2
    df_ends['Route Type'] = df_ends['Route Type'].astype(float)

    # Convert KP From and KP to to float
    df[['KP From', 'KP To']] = df[['KP From', 'KP To']].astype(float)

    return df, df_ends

def calc_pipe_data(df, pipeline_set):

    """
    Calculate properties of pipes for a specific pipeline set.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing the pipe data.
    pipeline_set : str
        Identifier of the pipeline set.

    Returns
    -------
    df : pandas.DataFrame
        DataFrame containing the pipe data and calculated pipe properties.

    Notes
    -----
    This function filters the df DataFrame based on the pipeline_set. It computes the
    inner diameter (ID), cross-sectional area (As), inner area (Ai), moment of inertia (I),
    hydrotest characteristic buckling force (SChar HT), and operation characteristic buckling
    force (SChar OP) of the pipe.
    """

    # Compute the inner diameter (ID) of the pipe
    df['ID'] = df['OD'] - 2.0 * df['WT']

    # Compute the cross-sectional area (As) of the pipe
    df['As'] = np.pi / 4.0 * (df['OD'] ** 2 - df['ID'] ** 2)

    # Compute the inner area (Ai) of the pipe
    df['Ai'] = np.pi / 4.0 * df['ID'] ** 2

    # Compute the moment of inertia (I) of the pipe
    df['I'] = np.pi / 64.0 * (df['OD'] ** 4 - df['ID'] ** 4)

    # Compute the hydrotest characteristic buckling force (SChar HT) of the pipe
    df['SChar HT'] = 2.26 * (df['E'] * df['As']) ** 0.25 * (
         df['E'] * df['I']) ** 0.25 * df['sw Hydrotest'] ** 0.5

    # Compute the operation characteristic buckling force (SChar OP) of the pipe
    df['SChar OP'] = 2.26 * (df['E'] * df['As']) ** 0.25 * (
        df['E'] * df['I']) ** 0.25 * df['sw Operation'] ** 0.5

    # Filter df DataFrame based on pipeline_set
    df = df.loc[(df['Pipeline'] == pipeline_set)]

    return df

def calc_oper_data(df, df_route_ends, pipeline_set, loadcase_set):

    """
    Calculate operating data and process it.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing the operating data.
    df_route_ends : pandas.DataFrame
        DataFrame containing the end boundary conditions.
    pipeline_set : str
        Identifier of the pipeline set.
    loadcase_set : str
        Identifier of the loadcase set.

    Returns
    -------
    df : pandas.DataFrame
        DataFrame containing the operating data and calculated operating data.

    Notes
    -----
    This function filters df DataFrame based on pipeline_set, loadcase_set, and 'KP To'.
    It calculates rolling mean and difference, assigns the 'Length' column, resets the index, and
    drops rows with NaN values before returning the preprocessed DataFrame.
    """

    # Filter df DataFrame based on pipeline_set, loadcase_set and 'KP To'
    df = df.loc[(df['Pipeline'] == pipeline_set) &
                (df['Loadcase Set'] == loadcase_set) &
                (df['KP'] <= df_route_ends['KP To'].iloc[-1])]

    # Calculate the rolling mean of df grouped by Pipeline and Loadcase Set
    df_rolling_mean = df.groupby(['Pipeline', 'Loadcase Set']).rolling(2).mean()

    # Calculate the rolling difference of df grouped by Pipeline and Loadcase Set
    df_rolling_difference = df.groupby(
        ['Pipeline', 'Loadcase Set']).rolling(2).max() - df.groupby(
            ['Pipeline', 'Loadcase Set']).rolling(2).min()

    # Assign the 'Length' column in df_rolling_mean
    df_rolling_mean['Length'] = df_rolling_difference['KP']

    # Reset the index of df_rolling_mean and drop the 'level_2' index level
    df_rolling_mean = df_rolling_mean.reset_index().drop('level_2', axis=1)

    # Drop rows with NaN values
    df_rolling_mean = df_rolling_mean.dropna()

    return df_rolling_mean

def calc_soil_data(df, pipeline_set):

    """
    Calculate soil data and axial and lateral friction factor distributions and assign them to
    DataFrame columns.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing soil data.
    pipeline_set : str
        Identifier of the pipeline set.

    Returns
    -------
    df : pandas.DataFrame
        DataFrame containing soil data and calculated friction factor distributions.

    Notes
    -----
    This function filters df DataFrame based on pipeline_set value. It computes lognormal
    distributions for axial and lateral friction factors and assigns them to DataFrame columns.
    """

    # Compute lognormal or normal distributions for axial friction and assign arrays to DataFrame columns
    df['muax Array'], df['muax CDF Array'] = zip(
        *df.apply(
            lambda x: calc_lognorm_soil(x['Axial Mean'], x['Axial STD']),
            axis=1
        ).apply(np.array)
    )

    # Compute lognormal distributions for lateral hydrotest friction and assign arrays to DataFrame columns
    df['mul HT Array'], df['mul HT CDF Array'] = zip(
        *df.apply(
            lambda x: calc_lognorm_soil(x['Lateral Hydrotest Mean'], x['Lateral Hydrotest STD']),
            axis=1
        ).apply(np.array)
    )

    # Compute lognormal distributions for lateral operation friction and assign arrays to DataFrame columns
    df['mul OP Array'], df['mul OP CDF Array'] = zip(
        *df.apply(
            lambda x: calc_lognorm_soil(x['Lateral Operation Mean'], x['Lateral Operation STD']),
            axis=1
        ).apply(np.array)
    )

    # Filter soil data based on pipeline set
    df = df[df['Pipeline'] == pipeline_set]

    return df

def calc_scenario_data(df_route, df_pipe, df_oper, df_soil):

    """
    Calculate scenario data based on route, pipe, operating, and soil data.

    Parameters
    ----------
    df_route : pandas.DataFrame
        DataFrame containing route data.
    df_pipe : pandas.DataFrame
        DataFrame containing pipe data.
    df_oper : pandas.DataFrame
        DataFrame containing operating data.
    df_soil : pandas.DataFrame
        DataFrame containing soil data.

    Returns
    -------
    df: pandas.DataFrame
        DataFrame containing the calculated scenario data.

    Notes
    -----
    This function merges route, pipe, operating, and soil data to compute various scenario
    parameters. It calculates various attributes such as lognormal distributions, buckling forces,
    and section counts. The resulting DataFrame includes a subset of calculated columns and is
    filled with 0 for missing values.
    """

    # Merge operating data with route data based on 'KP'
    df = pd.merge_asof(left=df_oper, right=df_route, left_on='KP', right_on='KP From',
                             direction='backward', left_by='Pipeline', right_by='Pipeline')

    # Merge resulting DataFrame with pipe data
    df = pd.merge(left=df, right=df_pipe, left_on=['Pipeline', 'Pipe Set'],
                       right_on=['Pipeline', 'Pipe Set'])

    # Merge resulting DataFrame with soil data
    df = pd.merge(left=df, right=df_soil, left_on=['Pipeline', 'Friction Set'],
                       right_on=['Pipeline', 'Friction Set'])

    # Compute lognormal distributions for soil properties and assign to DataFrame columns
    df['HOOS X Array'], df['HOOS CDF Array'] = zip(*df.apply(
        lambda x: calc_lognorm_hoos(x['Route Type'], x['Length'], x['HOOS Mean'],
                                     x['HOOS STD'], x['HOOS Reference Length'], x['RCM Buckling Force']), axis=1)
                                     .apply(np.array))

    # Compute various buckling forces based on calculated parameters
    df['FRF HT'] = df['RLT'] + df['E'] * df['Alpha'] * df['As'] * (
                df['Temperature Hydrotest'] - df['Temperature Installation']) + (
                                1 - 2 * df['Poisson']) * (
                                df['Pressure Hydrotest'] - df['Pressure Installation']) * df['Ai']
    df['FRF OP'] = df['RLT'] + df['E'] * df['Alpha'] * df['As'] * (
                df['Temperature Operation'] - df['Temperature Installation']) + (
                                 1 - 2 * df['Poisson']) * (
                                 df['Pressure Operation'] - df['Pressure Installation']) * df['Ai']
    df['FRF OP Pressure'] = df['RLT'] + (
                         1 - 2 * df['Poisson']) * df['Pressure Operation'] * df['Ai']
    df['FRF OP Temperature'] = df['E'] * df['As'] * df['Alpha'] * (
                            df['Temperature Operation'] - df['Temperature Installation'])
    df['Sv HT'] = 4.0 * np.sqrt(df['E'] * df['I'] * df['sw Hydrotest'] / df['Sleeper Height'])
    df['Sv OP'] = 4.0 * np.sqrt(df['E'] * df['I'] * df['sw Operation'] / df['Sleeper Height'])

    # Calculate section-related parameters
    df['KP Section'] = df['KP'] - df['KP From']
    df['Reference Section'] = (df['KP Section'] / df['HOOS Reference Length']).apply(np.floor)
    df['Section Count'] = 0.0
    df.loc[
        (df['Route Type'] != df['Route Type'].shift()) |
        (df['Reference Section'] != df['Reference Section'].shift()), 'Section Count'] = 1.0
    df['Section Count'] = df['Section Count'].cumsum()

    # Select relevant columns and rename them for clarity
    df = df[['KP', 'Length', 'Route Type', 'KP From', 'KP To', 'Point ID From', 'Point ID To',
             'Bend Radius', 'muax Array', 'muax CDF Array',
             'mul HT Array', 'mul HT CDF Array', 'mul OP Array', 'mul OP CDF Array',
             'HOOS X Array', 'HOOS CDF Array', 'sw Installation', 'sw Hydrotest', 'sw Operation',
             'SChar HT', 'SChar OP', 'Sv HT', 'Sv OP', 'RCM Buckling Force', 'RLT', 'FRF HT',
             'FRF OP Pressure', 'FRF OP Temperature', 'FRF OP', 'Residual Buckle Length Hydrotest',
             'Residual Buckle Force Hydrotest', 'Residual Buckle Length Operation',
             'Residual Buckle Force Operation', 'Section Count', 'KP Section', 'Reference Section',
             'Axial Mean', 'Lateral Hydrotest Mean', 'Lateral Operation Mean', 'HOOS Mean']]

    df = df.rename(columns={'sw Installation': 'sw IN',
                            'sw Hydrotest': 'sw HT',
                            'sw Operation': 'sw OP',
                            'Residual Buckle Length Hydrotest': 'buckleLength HT',
                            'Residual Buckle Force Hydrotest': 'buckleEAF HT',
                            'Residual Buckle Length Operation': 'buckleLength OP',
                            'Residual Buckle Force Operation': 'buckleEAF OP'})

    # Convert route type strings to numerical representation
    df.loc[df['Route Type'] == 'Straight', 'Route Type'] = 1
    df.loc[df['Route Type'] == 'Bend', 'Route Type'] = 2
    df.loc[df['Route Type'] == 'Sleeper', 'Route Type'] = 3
    df.loc[df['Route Type'] == 'RCM', 'Route Type'] = 4
    df['Route Type'] = df['Route Type'].astype(float)

    # Fill missing values with 0
    df = df.fillna(0)

    return df

def calc_monte_carlo_data(df, df_ends):

    """
    Convert the scenario data and pipeline end boundary conditions data to NumPy arrays for
    Monte Carlo simulations.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing the scenario data.
    df_ends : pandas.DataFrame
        DataFrame containing the pipeline end boundary conditions data.

    Returns
    -------
    np_distr : numpy.ndarray
        2D array with probabilistic distributions (rows) along the route mesh (columns).
    np_scen : numpy.ndarray
        2D array with scenario properties (rows) along the route mesh (columns).
    np_ends : numpy.ndarray
        2D array with end properties (rows) for the pipeline ends.

    Notes
    -----
    The arrays have the following row layout (index : meaning):

    np_distr:
      - 0 : MUAX_ARRAY
      - 1 : MUAX_CDF_ARRAY
      - 2 : MULAT_ARRAY_HT
      - 3 : MULAT_CDF_ARRAY_HT
      - 4 : MULAT_ARRAY_OP
      - 5 : MULAT_CDF_ARRAY_OP
      - 6 : HOOS_ARRAY
      - 7 : HOOS_CDF_ARRAY

    np_scen:
      - 0  : KP
      - 1  : LENGTH
      - 2  : ROUTE_TYPE
      - 3  : BEND_RADIUS
      - 4  : SW_INST
      - 5  : SW_HT
      - 6  : SW_OP
      - 7  : SCHAR_HT
      - 8  : SCHAR_OP
      - 9  : SV_HT
      - 10 : SV_OP
      - 11 : CBF_RCM
      - 12 : RLT
      - 13 : FRF_HT
      - 14 : FRF_P_OP
      - 15 : FRF_T_OP
      - 16 : FRF_OP
      - 17 : L_BUCKLE_HT
      - 18 : EAF_BUCKLE_HT
      - 19 : L_BUCKLE_OP
      - 20 : EAF_BUCKLE_OP
      - 21 : SECTION_ID
      - 22 : SECTION_KP
      - 23 : SECTION_REF
      - 24 : MUAX_MEAN
      - 25 : MULAT_HT_MEAN
      - 26 : MULAT_OP_MEAN
      - 27 : HOOS_MEAN

    np_ends:
      - 0 : ROUTE_TYPE
      - 1 : KP_FROM
      - 2 : KP_TO
      - 3 : REAC_INST
      - 4 : REAC_HT
      - 5 : REAC_OP
    """

    # Convert probabilistic distributions to numpy array
    list_temp1 = []
    prob_label_list = ['muax Array', 'muax CDF Array', 'mul HT Array', 'mul HT CDF Array',
                       'mul OP Array', 'mul OP CDF Array', 'HOOS X Array', 'HOOS CDF Array']
    for array_label in prob_label_list:
        list_temp2 = []
        for i in range(df[array_label].size):
            list_temp2.append(df[array_label][i])
        list_temp1.append(list_temp2)
    np_distr = np.array(list_temp1, dtype='float64')

    # Add extra columns to remove
    columns_drop = ['KP From', 'KP To', 'Point ID From', 'Point ID To']
    columns_drop = np.append(columns_drop, prob_label_list)

    # Convert scenario properties to numpy array
    np_scen = df.drop(columns_drop, axis=1).to_numpy().transpose()

    # Convert end properties to numpy array
    np_ends = df_ends.to_numpy().transpose()

    return np_distr, np_scen, np_ends

def calc_pp_data(df, np_array, pipeline_id, layout_set):

    """
    Calculate post-processing data set for a given layout set.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing post-processing data.
    np_array : numpy.ndarray
        NumPy array containing pipeline end boundary conditions.
    pipeline_id : str
        Identifier of the pipeline.
    layout_set : str
        Identifier of the layout set.

    Returns
    -------
    df : pandas.DataFrame
        DataFrame containing calculated post-processing data.

    Notes
    -----
    This function filters the DataFrame based on the layout set. It resets the index, renames
    columns, and selects relevant columns. Adjusts the last 'KP_to' value if it is smaller
    than the maximum value in np_array. Converts data types of columns to appropriate numeric
    types.
    """

    # Filter DataFrame based on layout_set
    df = df.loc[(df['Pipeline'] == pipeline_id) & (df['Layout Set'] == layout_set)]

    # Reset index, rename columns, and select relevant columns
    df = df.reset_index(drop=True).rename(columns={'Post-Processing Set': 'pp_set',
                                                    'KP From': 'KP_from',
                                                    'KP To': 'KP_to',
                                                    'Post-Processing Description': 'description'})
    df = df[['pp_set', 'KP_from', 'KP_to', 'description', 'Characteristic VAS Probability']]

    # Adjust last 'KP_to' value if necessary
    kp_max = np_array[KP_TO, -1]
    if kp_max > (df['KP_to'].iloc[-1]):
        df.loc[df.index[-1], 'KP_to'] = kp_max

    # Convert columns to appropriate numeric types
    df['pp_set'] = df['pp_set'].astype(np.int64)
    df['KP_from'] = df['KP_from'].astype(np.float64)
    df['KP_to'] = df['KP_to'].astype(np.float64)

    return df

def import_scenario(work_dir, file_name, pipeline_id, scenario_no, bl_verbose=False):

    """
    Import scenario data from an Excel file and preprocess it.

    Parameters
    ----------
    work_dir : str
        Directory where the Excel file is located.
    file_name : str
        Name of the Excel file.
    pipeline_id : str
        Identifier of the pipeline.
    scenario_no : int
        Identifier of the scenario.

    Returns
    -------
    df_scen : pandas.DataFrame
        Dataframe containing the scenario data
    np_distr : numpy.ndarray
        Array containing the friction factor distributions
    np_scen : numpy.ndarray
        Array containing the scenario data
    np_ends : numpy.ndarray
        Array containing the end boundary conditions
    df_pp : pandas.DataFrame
        Array containing the post-processing data
    n_sim : int
        Number of simulations

    Notes
    -----
    This function reads scenario data from an Excel file and preprocesses it. It extracts layout,
    pipeline, and loadcase sets, and the number of simulations from the Excel file. Postprocesses
    route, pipe, operating, soil, and scenario data. Processes post-processing sets and defines
    the NumPy arrays for Monte Carlo Simulations.

    Other Parameters
    ----------------
    bl_verbose : boolean, optional
        True if intermediate printouts are required (False by default).
    """

    # Starting time of the pre-processing module
    start_time = time.time()

    # Print out in the terminal that the assembly of the main dataframe has started
    if bl_verbose:
        print("1. Assembly of the main dataframe")

    # Read scenario data from the input Excel file
    df_sens = pd.read_excel(rf'{work_dir}/{file_name}', sheet_name = 'Scenario')
    scenario_no = int(scenario_no)

    # Define layout, pipeline and loadcase sets and number of simulations
    layout_set = df_sens.loc[(df_sens['Pipeline'] == pipeline_id) &
                             (df_sens['Scenario'] == scenario_no), 'Layout Set'].values[0]
    pipeline_set = df_sens.loc[(df_sens['Pipeline'] == pipeline_id) &
                               (df_sens['Scenario'] == scenario_no), 'Pipeline'].values[0]
    loadcase_set = df_sens.loc[(df_sens['Pipeline'] == pipeline_id) &
                               (df_sens['Scenario'] == scenario_no), 'Loadcase Set'].values[0]
    friction_sampling = df_sens.loc[(df_sens['Pipeline'] == pipeline_id) &
                                    (df_sens['Scenario'] == scenario_no), 'Friction Sampling'].values[0]
    prob_charac_friction = df_sens.loc[(df_sens['Pipeline'] == pipeline_id) &
                                      (df_sens['Scenario'] == scenario_no), 'Char. Friction Prob.'].values[0]
    n_sim = df_sens.loc[(df_sens['Pipeline'] == pipeline_id) &
                        (df_sens['Scenario'] == scenario_no), 'Simulations'].values[0]

    # Read route data from the input Excel file and postprocess it
    df_route = pd.read_excel(rf'{work_dir}/{file_name}', sheet_name='Route')
    df_route, df_route_ends = calc_route_data(df_route, layout_set, pipeline_set)

    # Read pipe data from the input Excel file and postprocess it
    df_pipe = pd.read_excel(rf'{work_dir}/{file_name}', sheet_name = 'Pipe')
    df_pipe = calc_pipe_data(df_pipe, pipeline_set)

    # Read operating data from the input Excel file and interpolate it
    df_oper = pd.read_excel(rf'{work_dir}/{file_name}', sheet_name = 'Operating')
    df_oper = calc_operating_profiles(df_oper, df_route, pipeline_set, loadcase_set)
    df_oper = calc_oper_data(df_oper, df_route_ends, pipeline_set, loadcase_set)

    # Read soil data from the input Excel file and postprocess it
    df_soil = pd.read_excel(rf'{work_dir}/{file_name}', sheet_name = 'Soils')
    # Axial
    df_soil['Axial Mean'], df_soil['Axial STD'] = LBDistributions(
        friction_factor_le=[df_soil['Axial LE']],
        friction_factor_be=[df_soil['Axial BE']],
        friction_factor_he=[df_soil['Axial HE']],
        friction_factor_fit_type=[df_soil['Axial Fit Bounds']]
    ).friction_distribution()[:2]
    # Lateral Hydrotest
    df_soil['Lateral Hydrotest Mean'], df_soil['Lateral Hydrotest STD'] = LBDistributions(
        friction_factor_le=[df_soil['Lateral Hydrotest LE']],
        friction_factor_be=[df_soil['Lateral Hydrotest BE']],
        friction_factor_he=[df_soil['Lateral Hydrotest HE']],
        friction_factor_fit_type=[df_soil['Lateral Hydrotest Fit Bounds']]
    ).friction_distribution()[:2]
    # Lateral Operation
    df_soil['Lateral Operation Mean'], df_soil['Lateral Operation STD'] = LBDistributions(
        friction_factor_le=[df_soil['Lateral Operation LE']],
        friction_factor_be=[df_soil['Lateral Operation BE']],
        friction_factor_he=[df_soil['Lateral Operation HE']],
        friction_factor_fit_type=[df_soil['Lateral Operation Fit Bounds']]
    ).friction_distribution()[:2]
    df_soil = calc_soil_data(df_soil, pipeline_set)

    # Postprocess scenario data
    df_scen  = calc_scenario_data(df_route, df_pipe, df_oper, df_soil)

    # Define the NumPy arrays used in the Monte Carlo Simulations
    np_distr, np_scen, np_ends = calc_monte_carlo_data(df_scen, df_route_ends)

    # Read post-processing sets from the input Excel file and postprocess them
    df_pp = pd.read_excel(rf'{work_dir}/{file_name}', sheet_name = 'Post-Processing')
    df_pp = calc_pp_data(df_pp, np_ends, pipeline_id, layout_set)

    # Print out in the terminal time taken to create main dataframe
    if bl_verbose:
        print(f'   Time taken to create main dataframe: {time.time() - start_time:.1f}s')

    return df_scen, np_distr, np_scen, np_ends, df_pp, n_sim, friction_sampling, prob_charac_friction

def calc_lognorm_soil(mu_mean, mu_std):

    """
    Compute the parameters of a lognormal distribution for friction factors (axial or lateral).

    Parameters
    ----------
    mu_mean : float
        The mean of the friction factor distribution.
    mu_std : float
        The standard deviation of the friction factor distribution.

    Returns
    -------
    mu_range : numpy.ndarray
        An array of values representing the range of the friction factor distribution
        between probabilities of exceedance between 0.01% and 99.99%.
    cdf_range : numpy.ndarray
        An array of cumulative density function (CDF) values corresponding to `mu_range`.

    Notes
    -----
        The function calculates the shape and scale parameters of a friction factor lognormal
        distribution based on the provided mean (`mu_mean`) and standard deviation (`mu_std`).
        It then computes the cumulative density function (CDF) for the generated range of values.

    """

    # Calculate shape and scale parameters of the lognormal distribution
    mu_shape = np.sqrt(np.log(1 + mu_std**2 / mu_mean**2))
    mu_scale = np.log(mu_mean**2 / np.sqrt(mu_mean**2 + mu_std**2))

    # Calculate the lower and upper bounds of the distribution
    mu_lower = lognorm(mu_shape, 0.0, np.exp(mu_scale)).ppf(0.0001)
    mu_upper = lognorm(mu_shape, 0.0, np.exp(mu_scale)).ppf(0.9999)

    # Generate a range of values within the distribution
    mu_range = np.linspace(mu_lower, mu_upper, 10000)

    # Compute the cumulative density function (CDF) for the generated range
    cdf_range = lognorm.cdf(mu_range, mu_shape, 0.0, np.exp(mu_scale))

    return mu_range, cdf_range

def calc_lognorm_hoos(type_elt, length_elt, hoos_mean, hoos_std, length_ref, rcm_charac):

    """
    Compute the parameters of the horizontal out-of-straightness (HOOS) lognormal distribution
    for different types of elements (e.g., Straight, Bend, Sleeper, RCM). This function takes into
    account the scaling factor of the HOOS distribution. For RCM, the HOOS factor is not a factor
    but the critical buckling force.

    Parameters
    ----------
    type_elt : str
        Type of the element.
    length_elt : float
        Length of the element.
    hoos_mean : float
        Mean of the HOOS distribution.
    hoos_std : float
        Standard deviation of the HOOS distribution.
    length_ref : float
        Reference length.
    rcm_charac : float
        Characteristic buckling force for the Residual Curvature Method (RCM).

    Returns
    -------
    x_range : numpy.ndarray
        An array of values representing the range of the friction factor distribution
        between probabilities of exceedance between 0.01% and 99.99%.
    cdf_range : numpy.ndarray
        An array of cumulative density function (CDF) values corresponding to `x_range`.

    Notes
    -----
    This function computes the parameters of a lognormal distribution for different types of
    elements such as Straight, Bend, Sleeper, and RCM (Residual Curvature Method). It
    calculates the cumulative density function (CDF) for the generated range of values
    based on the HOOS distribution parameters.

    """

    # Extract the type of element (e.g., Straight, Bend, Sleeper, RCM)
    type_elt_split = type_elt.split(' ')[0]

    # Compute the ratio of the reference length to the element length
    n = length_ref / length_elt

    if type_elt_split == 'Straight' or type_elt_split == 'Bend':
        # Calculate parameters for straight or bend elements
        shape_hoos = np.sqrt(np.log(1 + hoos_std**2 / hoos_mean**2))
        scale_hoos = np.log(hoos_mean**2 / (np.sqrt(hoos_mean**2 + hoos_std**2)))

        # Define the range of the HOOS distribution
        hoos_lower = 0.0
        hoos_upper = 20.0
        x = np.linspace(hoos_lower, hoos_upper, 200000)

        # Calculate the cumulative density function (CDF) considering the scaling factor
        cdf = 1-(1-lognorm.cdf(x, shape_hoos, 0.0, np.exp(scale_hoos)))**(1/n)

        # Generate a range of CDF values
        cdf_range = np.arange(0.0, 1.0, 0.0001)

        # Interpolate to get the corresponding values of the distribution
        x_range = np.interp(cdf_range, cdf, x)

    elif type_elt_split == 'Sleeper':
        # Calculate parameters for sleeper elements
        shape_hoos = np.sqrt(np.log(1 + hoos_std**2 / hoos_mean**2))
        scale_hoos = np.log(hoos_mean**2 / (np.sqrt(hoos_mean**2 + hoos_std**2)))

        # Calculate the lower and upper bounds of the distribution for sleeper elements
        hoos_lower = lognorm(shape_hoos, 0.0, np.exp(scale_hoos)).ppf(0.0001)
        hoos_upper = lognorm(shape_hoos, 0.0, np.exp(scale_hoos)).ppf(0.9999)

        # Generate a range of values within the distribution
        x_range = np.linspace(hoos_lower, hoos_upper, 10000)

        # Compute the cumulative density function (CDF) for the generated range
        cdf_range = lognorm.cdf(x_range, shape_hoos, 0.0, np.exp(scale_hoos))

    elif type_elt_split == 'RCM':
        # Calculate parameters for RCM elements
        shape_hoos = np.sqrt(np.log(1 + hoos_std**2 / hoos_mean**2))
        scale_hoos = np.log(hoos_mean**2 / (np.sqrt(hoos_mean**2 + hoos_std**2)))
        scale_hoos = scale_hoos + np.log(rcm_charac)

        # Calculate the lower and upper bounds of the distribution for RCM elements
        hoos_lower = lognorm(shape_hoos, 0.0, np.exp(scale_hoos)).ppf(0.0001)
        hoos_upper = lognorm(shape_hoos, 0.0, np.exp(scale_hoos)).ppf(0.9999)

        # Generate a range of values within the distribution
        x_range = np.linspace(hoos_lower, hoos_upper, 10000)

        # Compute the cumulative density function (CDF) for the generated range
        cdf_range = lognorm.cdf(x_range, shape_hoos, 0.0, np.exp(scale_hoos))

    return x_range, cdf_range
