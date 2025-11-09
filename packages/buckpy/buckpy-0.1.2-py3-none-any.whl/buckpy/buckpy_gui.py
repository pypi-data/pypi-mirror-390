'''
This module contains the GUI of BuckPy.
'''

import os
import tkinter as tk
from tkinter import ttk
from tkinter import font
from tkinter import filedialog
import pandas as pd
from importlib.resources import files, as_file
from pathlib import Path

class GUI:
    '''
    BuckPy Graphical User Interface (GUI) class.

    This class creates and manages the main window for user interaction,
    allowing users to select input files, enter pipeline and scenario IDs,
    choose options, and view scenario data in a table. It handles all
    user input validation and provides a structured interface for running
    BuckPy workflows.
    '''

    def __init__(self, root):
        '''
        Initialize the BuckPy GUI.

        Sets up the main window, configures fonts and geometry, creates
        top and bottom frames, and initializes all widgets for user input.
        '''
        # Store the root window
        self.root = root

        # Set window title
        self.root.title('BuckPy')

        # Set window icon
        try:
            logo_res = files("buckpy").joinpath("_static", "logo.png")
            with as_file(logo_res) as logo_path:
                self.root.iconphoto(False, tk.PhotoImage(file=str(logo_path)))
        except Exception:
            # Fallback to source tree when running from repo
            try:
                fallback = Path(__file__).with_name("_static") / "logo.png"
                if fallback.exists():
                    self.root.iconphoto(False, tk.PhotoImage(file=str(fallback)))
            except Exception:
                pass

        # Update geometry info
        self.root.update_idletasks()
        window_width = 1366
        window_height = 768
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.root.geometry(f'{window_width}x{window_height}+{x}+{y}')

        # Set modern default font
        default_font = font.nametofont('TkDefaultFont')
        default_font.configure(family='Segoe UI', size=11)
        self.root.option_add('*Font', default_font)

        # Create top and bottom frames for layout
        self.top_frame = tk.Frame(self.root, padx=20, pady=20)
        self.top_frame.grid(row=0, column=0, sticky='ew')
        self.bottom_frame = tk.Frame(self.root, padx=20)
        self.bottom_frame.grid(row=1, column=0, sticky='nsew')

        # Add a bottom padding frame for spacing
        self.bottom_padding = tk.Frame(self.root, height=20)
        self.bottom_padding.grid(row=2, column=0, sticky='ew')

        # Configure grid weights for resizing behavior
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=0)

        # Set minimum sizes and weights for columns in the top frame
        self.top_frame.grid_columnconfigure(1, minsize=200)
        self.top_frame.grid_columnconfigure(3, minsize=100)
        self.top_frame.grid_columnconfigure(5, minsize=200, weight=1)

        # Make the Treeview expand in the bottom frame
        self.bottom_frame.grid_rowconfigure(0, weight=1)
        self.bottom_frame.grid_columnconfigure(0, weight=1)

        # Initialize file path variables
        self.work_dir = None
        self.input_file_name = None

        # Add all widgets to the GUI
        self.create_widgets()

    def create_widgets(self):
        '''
        Create and place all widgets in the GUI.

        Adds labels, entry fields, buttons, comboboxes, and separators
        to the top frame for user input and configuration.
        '''
        # Initialize row index for grid placement
        self.irow_tree = 0

        # Add a horizontal separator at the top
        separator_horizontal = tk.Frame(self.top_frame, height=1, bg='#000000')
        separator_horizontal.grid(row=self.irow_tree, column=0, columnspan=7, sticky='ew')

        # Add header labels for Parameter, Input Entry, and Comments
        self.irow_tree += 1
        self.excel_label = tk.Label(self.top_frame, text='Parameter', anchor='w', font=('Segoe UI', 11, 'bold'))
        self.excel_label.grid(row=self.irow_tree, column=1, sticky='ew', padx=10, pady=5, ipadx=10, ipady=3)
        self.excel_label = tk.Label(self.top_frame, text='Input Entry', anchor='center', font=('Segoe UI', 11, 'bold'), width=10)
        self.excel_label.grid(row=self.irow_tree, column=3, sticky='ew', padx=10, pady=5, ipadx=10, ipady=3)
        self.excel_label = tk.Label(self.top_frame, text='Comments', anchor='w', font=('Segoe UI', 11, 'bold'))
        self.excel_label.grid(row=self.irow_tree, column=5, sticky='ew', padx=10, pady=5, ipadx=10, ipady=3)

        # Add a horizontal separator below the headers
        self.irow_tree += 1
        separator_horizontal = tk.Frame(self.top_frame, height=1, bg='#000000')
        separator_horizontal.grid(row=self.irow_tree, column=0, columnspan=7, sticky='ew')

        # Add Excel file selection row
        self.irow_tree += 1
        self.excel_label = tk.Label(self.top_frame, text='Select Excel input file:', anchor='w')
        self.excel_label.grid(row=self.irow_tree, column=1, sticky='ew', padx=10, pady=5, ipadx=10, ipady=3)
        self.excel_button = tk.Button(self.top_frame, text='Open', command=self.open_file, anchor='center', width=10)
        self.excel_button.grid(row=self.irow_tree, column=3, sticky='ew', padx=10, pady=5, ipadx=10)
        self.excel_label = tk.Label(self.top_frame, text='Excel input file name', anchor='w')
        self.excel_label.grid(row=self.irow_tree, column=5, sticky='ew', padx=10, pady=5, ipadx=10, ipady=3)

        # Add Pipeline ID entry row
        self.irow_tree += 1
        self.pipeline_id_label = tk.Label(self.top_frame, text='Pipeline ID:', anchor='w')
        self.pipeline_id_label.grid(row=self.irow_tree, column=1, sticky='w', padx=10, pady=5, ipadx=10, ipady=3)
        self.pipeline_id_entry = tk.Entry(self.top_frame, justify='center', width=10)
        self.pipeline_id_entry.grid(row=self.irow_tree, column=3, sticky='nsew', padx=10, pady=5, ipadx=10, ipady=3)
        self.pipeline_id_entry.insert(0, 'Empty')
        self.pipeline_id = self.pipeline_id_entry.get()

        # Add Scenario IDs entry row
        self.irow_tree += 1
        self.scenario_id_label = tk.Label(self.top_frame, text='Scenario IDs (comma-separated):', anchor='w')
        self.scenario_id_label.grid(row=self.irow_tree, column=1, sticky='w', padx=10, pady=5, ipadx=10, ipady=3)
        self.scenario_id_entry = tk.Entry(self.top_frame, justify='center', width=10)
        self.scenario_id_entry.grid(row=self.irow_tree, column=3, sticky='nsew', padx=10, pady=5, ipadx=10, ipady=3)
        self.scenario_id_entry.insert(0, 'e.g. 1,2,3')
        self.scenario_id = self.scenario_id_entry.get()

        # Add verbose output combobox row
        self.irow_tree += 1
        self.bl_verbose_label = tk.Label(self.top_frame, text='Enable verbose output', anchor='w')
        self.bl_verbose_label.grid(row=self.irow_tree, column=1, sticky='w', padx=10, pady=5, ipadx=10, ipady=3)
        self.bl_verbose_list = ['True', 'False']
        self.combobox_bl_verbose = ttk.Combobox(self.top_frame, values=self.bl_verbose_list, justify='center', width=10)
        self.combobox_bl_verbose.set(self.bl_verbose_list[0])
        self.combobox_bl_verbose.grid(row=self.irow_tree, column=3, sticky='nsew', padx=10, pady=5, ipadx=10, ipady=3)
        self.bl_verbose = self.combobox_bl_verbose.get()

        # Add output combination combobox row
        self.irow_tree += 1
        self.bl_output_combination_label = tk.Label(self.top_frame, text='Extract extended results', anchor='w')
        self.bl_output_combination_label.grid(row=self.irow_tree, column=1, sticky='w', padx=10, pady=5, ipadx=10, ipady=3)
        self.bl_output_combination_list = ['True', 'False']
        self.combobox_bl_output_combination = ttk.Combobox(self.top_frame, values=self.bl_output_combination_list, justify='center', width=10)
        self.combobox_bl_output_combination.set(self.bl_output_combination_list[-1])
        self.combobox_bl_output_combination.grid(row=self.irow_tree, column=3, sticky='nsew', padx=10, pady=5, ipadx=10, ipady=3)
        self.output_combination = self.combobox_bl_output_combination.get()

        # Add OK button row
        self.irow_tree += 1
        self.bl_verbose_label = tk.Label(self.top_frame, text='Run all scenarios', anchor='w')
        self.bl_verbose_label.grid(row=self.irow_tree, column=1, sticky='w', padx=10, pady=5, ipadx=10, ipady=3)
        self.ok_button = tk.Button(self.top_frame, text='OK', command=self.close_app, width=10)
        self.ok_button.grid(row=self.irow_tree, column=3, sticky='nsew', padx=10, pady=5, ipadx=10)

        # Add a horizontal separator at the bottom
        self.irow_tree += 1
        separator_horizontal = tk.Frame(self.top_frame, height=1, bg='#000000')
        separator_horizontal.grid(row=self.irow_tree, column=0, columnspan=7, sticky='ew')

        # Add vertical separators between columns
        separator = tk.Frame(self.top_frame, width=1, bg='#000000')
        separator.grid(row=0, column=0, rowspan=self.irow_tree+1, sticky='ns', padx=0, pady=0)
        separator = tk.Frame(self.top_frame, width=1, bg='#000000')
        separator.grid(row=0, column=2, rowspan=self.irow_tree+1, sticky='ns', padx=0, pady=0)
        separator = tk.Frame(self.top_frame, width=1, bg='#000000')
        separator.grid(row=0, column=4, rowspan=self.irow_tree+1, sticky='ns', padx=0, pady=0)
        separator = tk.Frame(self.top_frame, width=1, bg='#000000')
        separator.grid(row=0, column=6, rowspan=self.irow_tree+1, sticky='ns', padx=0, pady=0)

    def open_file(self):
        '''
        Open a file dialog for the user to select an Excel input file.

        Updates the displayed file name and triggers loading of scenario
        data into the table if a valid file is selected.
        '''
        # Open a file dialog for Excel files
        file_path = filedialog.askopenfilename(
            initialdir=os.getcwd(),
            filetypes=[('Excel files', '*.xlsx *.xls *.xlsm')],
            title='Select Excel input file'
        )

        # If the user cancels the dialog, exit the method
        if not file_path:
            return

        # Store the directory of the selected file
        self.work_dir = os.path.dirname(file_path)

        # Store the file name of the selected file
        self.input_file_name = os.path.basename(file_path)

        # Update the label to display the selected file name
        self.excel_label.config(text=self.input_file_name)

        # Load the scenario data into the Treeview
        self.setup_treeview()

    def setup_treeview(self):
        '''
        Set up and populate the Treeview widget with scenario data.

        Reads the selected Excel file, configures the table columns and
        headings, and inserts scenario data rows for user review.
        '''
        # Read the 'Scenario' sheet from the selected Excel file into a DataFrame
        self.df_sens = pd.read_excel(rf'{self.work_dir}/{self.input_file_name}', sheet_name='Scenario')
        columns = self.df_sens.columns.tolist()
        
        # Create the Treeview widget with columns from the DataFrame
        self.tree = ttk.Treeview(self.bottom_frame, columns=self.df_sens.columns.tolist(), show='headings')
        self.tree.grid(row=0, column=0, sticky='nsew')

        # Configure Treeview and heading styles
        style = ttk.Style()
        style.theme_use('default')
        style.configure('Treeview.Heading', font=('Segoe UI', 10, 'bold'), padding=[0, 10], background='#f5f5f5')
        style.configure('Treeview',font=('Segoe UI', 10), rowheight=30, borderwidth=1, relief='solid', background='#f5f5f5', fieldbackground='#f5f5f5')

        # Set up column headings and widths
        for i, col in enumerate(columns):
            # Last column: left-aligned, stretchable
            if i == len(columns) - 1:
                self.tree.heading(col, text=col, anchor='w')
                self.tree.column(col, stretch=True, anchor='w')
            # Second and third last columns: center-aligned, fixed width
            elif (i == len(columns) - 2) or (i == len(columns) - 3):
                self.tree.heading(col, text=col, anchor='center')
                self.tree.column(col, width=140, stretch=False, anchor='center')
            # All other columns: center-aligned, smaller fixed width
            else:
                self.tree.heading(col, text=col, anchor='center')
                self.tree.column(col, width=100, stretch=False, anchor='center')

        # Insert each row of the DataFrame into the Treeview
        for _, row in self.df_sens.iterrows():
            self.tree.insert('', 'end', values=list(row))

        # Reset other relevant fields
        self.pipeline_id_entry.delete(0, tk.END)
        self.scenario_id_entry.delete(0, tk.END)
        self.pipeline_id_entry.insert(0, self.df_sens['Pipeline'].iloc[0])
        self.scenario_id_entry.insert(0, self.df_sens['Scenario'].iloc[0])

    def close_app(self):
        '''
        Validate user input and close the GUI if all inputs are valid.

        Checks that required fields are filled and formatted correctly.
        If validation passes, stores user selections and closes the window.
        Otherwise, displays appropriate warning or error messages.
        '''
        # Get the current values from the entry widgets
        pipeline_id_value = self.pipeline_id_entry.get()
        scenario_id_value = self.scenario_id_entry.get()

        # Check if work_dir and input_file_name are set
        if not self.work_dir or not self.input_file_name:
            tk.messagebox.showwarning('Input Required', 'Please select a valid Excel input file.')
            return

        # Check for empty or placeholder values
        if not pipeline_id_value or pipeline_id_value == 'Empty' or \
           not scenario_id_value or scenario_id_value == 'e.g. 1,2,3':
            tk.messagebox.showwarning('Input Required', 'Please enter valid Pipeline ID and Scenario IDs.')
            return

        # Optional: Check if Pipeline ID is a string
        if pipeline_id_value.isdigit():
            tk.messagebox.showwarning('Invalid Input', 'Pipeline ID should be a string.')
            return

        # Optional: Check if Scenario IDs are comma-separated numbers
        scenario_ids = [s.strip() for s in scenario_id_value.split(',')]
        if not all(s.isdigit() for s in scenario_ids):
            tk.messagebox.showwarning('Invalid Input', 'Scenario IDs should be comma-separated numbers (e.g. 1,2,3).')
            return

        # Additional checks: Ensure pipeline_id_value and scenario_id_value(s) exist in the DataFrame
        if hasattr(self, 'df_sens'):
            # Check if the Pipeline ID exists in the DataFrame
            if pipeline_id_value not in self.df_sens['Pipeline'].astype(str).unique():
                tk.messagebox.showwarning('Invalid Input', f'Pipeline ID "{pipeline_id_value}" not found in the input file.')
                return
            # Check if each Scenario ID exists in the DataFrame
            scenario_unique = set(self.df_sens['Scenario'].astype(str).unique())
            invalid_scenarios = [sid for sid in scenario_ids if sid not in scenario_unique]
            if invalid_scenarios:
                tk.messagebox.showwarning(
                    'Invalid Input',
                    f'Scenario ID(s) {", ".join(invalid_scenarios)} not found in the input file.'
                )
                return

        try:
            # Store the validated values in instance variables
            self.pipeline_id = pipeline_id_value
            self.scenario_id = scenario_id_value
            self.bl_verbose = self.combobox_bl_verbose.get()
            self.output_combination = self.combobox_bl_output_combination.get()
            # Close the GUI window
            self.root.destroy()
        except Exception as e:
            # Show an error message if something unexpected happens
            tk.messagebox.showerror('Error', f'An unexpected error occurred: {e}')
