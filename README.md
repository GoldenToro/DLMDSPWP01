# CSV to SQLite Database Processor and Visualizer

## Overview

This project processes CSV data files, stores the data in an SQLite database, and provides functionality to visualize the data. The project is implemented in Python and follows object-oriented design principles, making use of libraries such as `pandas`, `matplotlib`, `sqlalchemy`, and custom logging and visualization modules.

## Additional Task and Bokeh 

The visualization on main works with matplotlib, to use the bokeh library checkout or merge the 'bokeh' branch.
These are the commands for mergin the branch 'bokeh' into 'develop':
    
    git clone https://github.com/GoldenToro/DLMDSPWP01.git
    cd DLMDSPWP01
    git fetch --all
    git checkout bokeh
    git checkout develop
    git merge bokeh
    # Resolve conflicts if any, then:
    git add <resolved_file>
    git commit
    # Finally, push changes if you have write access:
    git push origin develop 


## Features

- Load CSV data into an SQLite database.
- Visualize data from the database.
- Assign test data to ideal functions based on minimum deviations.
- Comprehensive logging for easy debugging and monitoring.
- Command-line interface for easy interaction.

## Requirements

- Python 3.6+
- `pandas`
- `matplotlib`
- `sqlalchemy`
- `argparse`

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/csv-to-sqlite-processor.git
   cd csv-to-sqlite-processor
   
2. Create and activate a virtual environment (optional but recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   
3. Install the required packages:

   ```bash
   pip install -r requirements.txt
   
## Usage
### Command-Line Interface

Run the main script with the desired arguments:

    python csv_processor.py -csv <path_to_csv_directory> -db <path_to_db_file> [options]

### Arguments
- csv, --csv_path: Path to the directory containing the CSV files (default: Dataset2).
- db, --db_path_to_file: Path to the SQLite database file (default: db.sqlite3).
- o, --overwrite: Overwrite the existing database if it already exists.
- v, --visualize_import: Visualize every important step.
- e, --visualize_result: Visualize only end-results.
- t, ----test: Run unit tests before executing main program.

### Examples:

    python csv_processor.py -csv ./data -db ./database.db -o -v -t

This command tests all unit tests and then loads the CSV data from the ./data directory, saves it to ./database.db, overwrites the existing database if it exists, and visualizes the import steps and the end-results.

    python csv_processor.py

This runs the program with the standard parameter, without testing, visualizing or saving the data 
### Hint

For changing the log level, change line 4 in fancy_logging.py
