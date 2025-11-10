'''
This is the main module of BuckPy.
'''

import tkinter as tk
from . import buckpy_gui
from . import buckpy_preprocessing
from . import buckpy_solver
from . import buckpy_postprocessing
from . import buckpy_visualisation

def main():

    '''
    Main BuckPy function.
    '''

    # Load user inputs from the GUI interface
    root = tk.Tk()
    gui = buckpy_gui.GUI(root)
    root.mainloop()

    # Retrieve user selections from the GUI
    work_dir = gui.work_dir
    input_file_name = gui.input_file_name
    pipeline_id = gui.pipeline_id

    # Check if the user selected a file and provided required info
    if not work_dir or not input_file_name:
        print('No input file selected. Exiting.')
        return

    # Print start message
    print('======================  Start Processing  ========================')

    # Parse scenario IDs as a list of integers
    scenario_list_id = [int(s.strip()) for s in gui.scenario_id.split(',') if s.strip().isdigit()]
    bl_verbose = gui.bl_verbose
    output_combination = gui.output_combination

    # Loop over each scenario ID and run the BuckPy workflow
    for scenario_id in scenario_list_id:
        # Load and preprocess scenario data from the input Excel file
        df_scen, np_distr, np_scen, np_ends, df_pp_set, n_sim, fric_sampling, prob_exceed_char_fric = buckpy_preprocessing.import_scenario(
            work_dir,
            input_file_name,
            pipeline_id,
            scenario_id,
            bl_verbose=bl_verbose
        )
        # Run BuckPy solver for deterministic and Monte Carlo simulations
        df_pp_plot, df_vap_plot, df_pp_buckle_prop = buckpy_solver.exec_buckpy(
            fric_sampling,
            np_distr,
            np_scen,
            np_ends,
            n_sim,
            bl_verbose=bl_verbose
        )

        # Post-process simulation results and generate summary outputs
        buckpy_postprocessing.pp_buckpy(
            work_dir,
            input_file_name,
            pipeline_id,
            scenario_id,
            prob_exceed_char_fric,
            df_pp_plot,
            df_vap_plot,
            df_pp_buckle_prop,
            df_scen,
            df_pp_set,
            n_sim,
            output_combination,
            bl_verbose=bl_verbose
        )

        # Generate additional plots and visualizations for BuckPy results
        buckpy_visualisation.plot_buckpy(
            work_dir,
            input_file_name,
            pipeline_id,
            scenario_id,
            bl_verbose=bl_verbose
        )

    # Print end message
    print('=======================  End Processing  =========================')

if __name__ == '__main__':
    main()
