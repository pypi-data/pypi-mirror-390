"""
This module contains the plot functions of BuckPy result files.
"""

import time
import pandas as pd
import matplotlib.pyplot as plt

def read_output(output_file_name):

    '''
    Read the data from the BuckPy result file.

    Parameters
    ----------
    output_file_name : string
        File path of the BuckPy result file.

    Returns
    -------
    df_sets : pandas DataFrame
        DataFrame containing the data in the 'Sets' tab.
    df_buckle : pandas DataFrame
        DataFrame containing the data related to the number of buckles.
    df_force_prof : pandas DataFrame
        DataFrame containing the force profile data.
    '''

    # Read all tabs in the BuckPy result file
    all_sheets_dict = pd.read_excel(output_file_name, sheet_name = None)

    # Read the 'Sets', 'No Buckles' and 'Force Profiles' tabs
    df_sets = all_sheets_dict['Sets']
    df_buckle = all_sheets_dict['No Buckles']
    df_force_prof = all_sheets_dict['Force Profiles']

    return df_sets, df_buckle, df_force_prof

def read_input(work_dir, input_file_name, pipeline_id, scenario_no):

    '''
    Read the route bend and post-processing data from the BuckPy input file and select
    the data for the current scenario.

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

    Returns
    -------
    df_routes : pandas DataFrame
        DataFrame containing the data in the 'Route' tab.
    df_pps : pandas DataFrame
        DataFrame containing the data in the 'Post-Processing' tab.
    '''

    # Read all tabs in the BuckPy input file
    all_sheets_dict = pd.read_excel(rf'{work_dir}/{input_file_name}', sheet_name = None)

    # Read 'Scenario', 'Route' and "Post-Processing" tabs
    df_scens = all_sheets_dict['Scenario']
    df_routes = all_sheets_dict['Route']
    df_pps = all_sheets_dict['Post-Processing']
    scenario_no = int(scenario_no)

    # Obtain layout number
    layout_no = df_scens.loc[(df_scens['Pipeline'] == pipeline_id) &
                             (df_scens['Scenario'] == scenario_no), 'Layout Set'].iloc[0]

    # Obtain the data for current scenario
    df_routes = df_routes[(df_routes['Pipeline'] == pipeline_id) &
                          (df_routes['Layout Set'] == layout_no)]
    df_pps = df_pps[(df_pps['Pipeline'] == pipeline_id) & (df_pps['Layout Set'] == layout_no)]

    return df_routes, df_pps

def assembly_dataframe_bend_sleeper_ilt(df):

    '''
    Read the route bend data from the BuckPy input file and select the KP
    of the 'Bend', 'Sleeper', 'RCM' and 'ILT' from the 'Route Type' column.

    Parameters
    ----------
    df : pandas DataFrame
        DataFrame containing the data in the 'Route' tab.

    Returns
    -------
    df1 : pandas DataFrame
        DataFrame containing the 'Bend' route type data.
    df2 : pandas DataFrame
        DataFrame containing the 'Sleeper' route type data.
    df3 : pandas DataFrame
        DataFrame containing the 'RCM' route type data.
    df4 : pandas DataFrame
        DataFrame containing the 'ILT' route type data.
    '''

    # Select route bend and KP columns
    cols = ['Route Type', 'Point ID From', 'Point ID To', 'KP From', 'KP To']
    df = df[cols]

    # Select rows of route bend from 'Route Type'
    df1 = df.loc[df['Route Type'] == 'Bend'].copy()
    df1 = df1.reset_index(drop = True)

    # Select rows of sleeper from 'Point ID'
    df2 = df.iloc[1:-1].loc[df['Route Type'] == 'Sleeper'].copy()
    df2 = df2.reset_index(drop = True)

    # Select rows of RCM from 'Point ID'
    df3 = df.iloc[1:-1].loc[df['Route Type'] == 'RCM'].copy()
    df3 = df3.reset_index(drop = True)

    # Select rows of ILT from 'Point ID'
    df4 = df.iloc[1:-1].loc[df['Point ID From'].str.contains('ILT') &
                            df['Point ID To'].str.contains('ILT')].copy()
    df4 = df4.reset_index(drop = True)

    return df1, df2, df3, df4

def assembly_double_rows(df):

    """
    Double each row of the dataframe based on KP.

    Parameters
    ----------
    df : pandas DataFrame
        DataFrame containing the KP and results.

    Returns
    -------
    df : pandas DataFrame
        DataFrame containing the doubled rows of KP and results.
    """

    # Double each row of the df
    df_temp1 = df.copy()
    df_temp1 = df_temp1.rename(columns = {'KP To (m)': 'KP'})
    df_temp1 = df_temp1.drop(labels = 'KP From (m)', axis = 1)
    df_temp1['sort'] = 1

    df_temp2 = df.copy()
    df_temp2 = df_temp2.rename(columns = {'KP From (m)': 'KP'})
    df_temp2 = df_temp2.drop(labels = 'KP To (m)', axis = 1)
    df_temp2['sort'] = 2

    # Double the rows except the start and end
    df = pd.concat([df_temp1, df_temp2])
    df = df.sort_values(by = ['KP', 'sort']).reset_index(drop = True)

    # Double the start and end rows and fill nan with 0
    first_row = pd.DataFrame({'KP': [df['KP'].min()]})
    last_row = pd.DataFrame({'KP': [df['KP'].max()]})
    df = pd.concat([first_row, df, last_row], ignore_index = True)
    df = df.fillna(0)

    return df

def assembly_dataframe_plot(df_sets, df_pps):

    """
    Assemble the dataframes on the probabilistic results and
    post-processing input data from BuckPy.

    Parameters
    ----------
    df_sets : pandas DataFrame
        DataFrame containing the output data in the  'Sets' tab.
    df_pps : pandas DataFrame
        DataFrame containing the input data in the 'Post-Processing' tab.

    Returns
    -------
    df : pandas DataFrame
        DataFrame containing the doubled rows of KP and results.
    """

    # Dataframe with post-processing inputs from the BuckPy input file
    df_pps = df_pps.rename(columns = {'Post-Processing Set': 'Set Label',
                                      'KP From': 'KP From (m)',
                                      'KP To': 'KP To (m)'})
    df_pps = df_pps[['Set Label', 'KP From (m)', 'KP To (m)']]

    # DataFrame of the 'Sets' tab from the BuckPy output
    df_sets = df_sets[['Set Label', 'KP From (m)', 'KP To (m)', 'Probability of Buckling',
                       'Characteristic VAS Probability',
                       'Characteristic VAS, Unconditional (m)',
                       'Characteristic Lateral Breakout Friction Probability',
                       'Characteristic Lateral Breakout Friction, Buckles',
                       'Lateral Breakout Friction, HE, Geotech']]

    # Add sets without outputs
    df = pd.concat([df_sets, df_pps])
    df = df.drop_duplicates(subset = ['Set Label', 'KP From (m)', 'KP To (m)'],
                            keep = 'first')
    df = df.sort_values(by = ['KP From (m)'])

    # Double each row for KP
    df = assembly_double_rows(df)

    # Add initial and final rows with zeros
    df_temp1 = pd.DataFrame({'KP': [df['KP'].min()],
                             'Probability of Buckling': [0.0],
                             'Characteristic VAS, Unconditional (m)': [0.0],
                             'Characteristic Lateral Breakout Friction, Buckles': [0.0]})
    df_temp2 = pd.DataFrame({'KP': [df['KP'].max()],
                             'Probability of Buckling': [0.0],
                             'Characteristic VAS, Unconditional (m)': [0.0],
                             'Characteristic Lateral Breakout Friction, Buckles': [0.0]})
    df = pd.concat([df_temp1, df, df_temp2], ignore_index = True)
    df = df.fillna(0.0)

    # Replace 0.0 with NaN for Geotech friction column
    df.loc[df['Characteristic Lateral Breakout Friction, Buckles'] == 0.0,
           'Lateral Breakout Friction, HE, Geotech'] = 0.0

    return df

def plot_bend_sleeper_ilt(a1, df1, df2, df3, df4, y_max):

    """
    Plot route bend, sleeper and ILT.

    Parameters
    ----------
    a1 : Matplotlib plot
        Axis of the Matplotlib plot.
    df1 : pandas DataFrame
        Dataframe containing the locations of the route bends.
    df2 : pandas DataFrame
        Dataframe containing the locations of sleepers.
    df3 : pandas DataFrame
        Dataframe containing the locations of RCMs.
    df4 : pandas DataFrame
        Dataframe containing the locations of ILTs.
    """

    # Plot bends
    for index, row in df1.iterrows():
        if index == 0:
            a1.plot([row['KP From'], row['KP To']], 2 * [0.1 * y_max],
                    color = 'C2', label = 'Route Bend', linestyle = 'dotted')
        else:
            a1.plot([row['KP From'], row['KP To']], 2 * [0.1 * y_max],
                    color = 'C2', linestyle = 'dotted')

    # Plot sleepers
    for index, row in df2.iterrows():
        kp_centre = 0.5 * (row['KP From'] + row['KP To'])
        if index == 0:
            a1.scatter(kp_centre, 0.1 * y_max,
                       color = 'C3', label = 'Sleeper', marker = '*')
        else:
            a1.scatter(kp_centre, 0.1 * y_max,
                       color = 'C3', marker = '*')

    # Plot RCMs
    for index, row in df3.iterrows():
        kp_centre = 0.5 * (row['KP From'] + row['KP To'])
        if index == 0:
            a1.scatter(kp_centre, 0.1 * y_max,
                       color = 'C4', label = 'RCM', marker = 'o')
        else:
            a1.scatter(kp_centre, 0.1 * y_max,
                       color = 'C4', marker = 'o')

    # Plot ILTs
    for index, row in df4.iterrows():
        kp_centre = 0.5 * (row['KP From'] + row['KP To'])
        if index == 0:
            a1.scatter(kp_centre, 0.1 * y_max,
                       color = 'C5', label = 'ILT', marker = '+')
        else:
            a1.scatter(kp_centre, 0.1 * y_max,
                       color = 'C5', marker = '+')

def plot_results(file_name, df_no_buckles, df_force_profiles,
                 df_bends, df_sleepers, df_rcms, df_ilts, df_set_pps):

    """
    Plot probabilistic results of BuckPy in 6 subplots:
    Row 1: unbuckled EAF, Number of Buckles, VAS;
    Row 2: buckled EAF, Probobality of Buckling, Friction.

    Parameters
    ----------
    file_name : str
        The name of the output image file.
    df_no_buckles : pandas DataFrame
        DataFrame containing the data related to the number of buckles.
    df_force_profiles : pandas DataFrame
        DataFrame containing the force profile data.
    df_bends : pandas DataFrame
        DataFrame containing the 'Bend' route type data.
    df_sleepers : pandas DataFrame
        DataFrame containing the 'Sleeper' route type data.
    df_rcms : pandas DataFrame
        DataFrame containing the 'RCM' route type data.
    df_ilts : pandas DataFrame
        DataFrame containing the 'ILT' route type data.
    df_set_pps : pandas DataFrame
        DataFrame containing the doubled rows of KP and results from
        'Sets' and 'Post-Processing' tabs.
    """

    # Generate matplolib figure
    fig = plt.figure()
    dpi_size = 110
    fig.set_size_inches(19.2 * 100 / dpi_size, 10.8 * 100 / dpi_size)

    # Subplot 1: Plot probabilistic results of the unbuckled EAF
    a1 = fig.add_subplot(231)
    a1.plot(df_force_profiles['KP (m)'],
            df_force_profiles['EAF Operation [without Buckling] (kN)'])

    a1.set_xlabel('KP (m)')
    a1.set_ylabel('EAF [without Buckling] (kN)')
    a1.grid()

    # Subplot 2: Plot distribution of number of buckles
    a2 = fig.add_subplot(232)
    a2.plot(df_no_buckles['Number of Buckles'], df_no_buckles['Probability of Buckling'])

    a2.set_xlabel('Number of Buckles')
    a2.set_ylabel('Probability of Buckling')
    a2.grid()

    # Subplot 3: Plot characteristic VAS with route bend, sleeper, RCM and ILT
    a3 = fig.add_subplot(233)
    a3.plot(df_set_pps['KP'], df_set_pps['Characteristic VAS, Unconditional (m)'],
            label = 'BuckPy')
    plot_bend_sleeper_ilt(a3, df_bends, df_sleepers, df_rcms, df_ilts,
                          df_set_pps['Characteristic VAS, Unconditional (m)'].max())

    a3.set_xlabel('KP (m)')
    a3.set_ylabel('Characteristic VAS (m)')
    a3.legend()
    a3.grid()

    # Subplot 4: Plot probabilistic results of the buckled EAF
    a4 = fig.add_subplot(234)
    a4.plot(df_force_profiles['KP (m)'],
            df_force_profiles['EAF Operation (kN)'])

    a4.set_xlabel('KP (m)')
    a4.set_ylabel('EAF [with Buckling] (kN)')
    a4.grid()

    # Subplot 5: Plot probabilities of buckling with route bend, sleeper, RCM and ILT
    a5 = fig.add_subplot(235)
    a5.plot(df_set_pps['KP'], df_set_pps['Probability of Buckling'], label = 'BuckPy')
    plot_bend_sleeper_ilt(a5, df_bends, df_sleepers, df_rcms, df_ilts,
                          df_set_pps['Probability of Buckling'].max())

    a5.set_xlabel('KP (m)')
    a5.set_ylabel('Probability of Buckling')
    a5.legend()
    a5.grid()

    # Subplot 6: Plot characteristic friction with route bend, sleeper, RCM and ILT
    prob_exceed_char_fric = df_set_pps[
        'Characteristic Lateral Breakout Friction Probability'
    ].max()
    a6 = fig.add_subplot(236)
    a6.plot(df_set_pps['KP'], df_set_pps['Characteristic Lateral Breakout Friction, Buckles'],
            label = f'P{int(100 * prob_exceed_char_fric)} Buckle Friction')
    a6.plot(df_set_pps['KP'], df_set_pps['Lateral Breakout Friction, HE, Geotech'],
            label = f'P{int(100 * prob_exceed_char_fric)} Geotech Friction', linestyle = 'dashed')
    plot_bend_sleeper_ilt(a6, df_bends, df_sleepers, df_rcms, df_ilts,
                          df_set_pps['Characteristic Lateral Breakout Friction, Buckles'].max())

    a6.set_xlabel('KP (m)')
    a6.set_ylabel('Breakout Lateral Friction')
    a6.legend()
    a6.grid()

    # Save the image file and close the plot
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
    plt.savefig(file_name, dpi = dpi_size)
    # plt.show()
    plt.close()

def plot_buckpy(work_dir, input_file_name, pipeline_id, scenario_no, bl_verbose = False):

    """
    Plot the probabilistic buckling results from BuckPy result files.

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
    """

    # Starting time of the plot buckpy results module
    start_time = time.time()

    # Print in the terminal that the plot of the results has started
    if bl_verbose:
        print("5. Plot results")

    # Read the probabilistic outputs from the result Excel file
    file_name_temp = f"{work_dir}/{input_file_name.split('.')[0]}_{pipeline_id}_scen{scenario_no}"
    output_file_name = f"{file_name_temp}_outputs.xlsx"
    df_set, df_no_buckle, df_force_profile = read_output(output_file_name)

    # Read the "Route" and "Post-Processing" tabs from the input file
    df_route, df_pp = read_input(work_dir, input_file_name, pipeline_id, scenario_no)

    # Assembly dataframes with the location of sleepers, RCMs, ILTs and route bends
    df_bend, df_sleeper, df_rcm, df_ilt = assembly_dataframe_bend_sleeper_ilt(df_route)

    # Assembly a dataframe with the "Sets" results using "Post-Processing" tab of input
    df_set_pp = assembly_dataframe_plot(df_set, df_pp)

    # Print in the terminal the time taken to plot results
    if bl_verbose:
        print(f'   Time taken to plot results: {time.time() - start_time:.1f}s')

    # Plot the 6 subplots and save the figure to file
    plot_file_name = f"{file_name_temp}_plots-2.png"
    plot_results(plot_file_name, df_no_buckle, df_force_profile,
                 df_bend, df_sleeper, df_rcm, df_ilt, df_set_pp)
