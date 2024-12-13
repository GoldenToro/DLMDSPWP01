import pandas as pd
from bokeh.plotting import figure, show
from bokeh.layouts import row, column
from bokeh.models import ColumnDataSource, NumeralTickFormatter
from itertools import cycle

# File names from the images
file_names = [
    "results_10Rounds_I4_DataLoadingVector.csv",
    "results_10Rounds_I4_JIT.csv",
    "results_10Rounds_I4_Slow.csv",
    "results_10Rounds_I4_Visualizing.csv"
]

def calculate_average_times(file_names):
    try:
        all_data = []
        colors = cycle(["blue", "red", "green", "orange", "purple"])
        source_colors = {}
        total_averages = []

        for file_name in file_names:
            data = pd.read_csv(file_name)

            # Ensure columns exist
            required_columns = {'function', 'file', 'time', 'lines', 'test_no'}
            if not required_columns.issubset(data.columns):
                print(f"Skipping file {file_name}: Missing required columns.")
                continue

            # Replace empty values in the 'file' column with placeholder
            data['file'] = data['file'].fillna("No File")

            # Extract the relevant part of the file name
            source_label = file_name.split('_')[-1].split('.')[0]
            if source_label not in source_colors:
                source_colors[source_label] = next(colors)

            # Group 'function', 'file', and 'lines' and calculate average time
            average_times = data.groupby(['function', 'file', 'lines'])['time'].mean().reset_index()
            average_times['source_file'] = source_label

            # Calculate total average time for this file
            total_average = average_times.groupby(['lines'])['time'].sum()
            total_averages.append({'source_file': source_label, 'total_average': total_average})

            all_data.append(average_times)

        # Combine all data
        combined_data = pd.concat(all_data, ignore_index=True)

        # Plot for each function, grouping by files
        function_rows = []
        for function_name, function_data in combined_data.groupby('function'):
            plots = []
            for file_name_group, group_data in function_data.groupby('file'):

                # Create the figure
                p = figure(title=f"{function_name} - {file_name_group}",
                           x_axis_label='Lines tested',
                           y_axis_label='Average Time in seconds',
                           # logarithmic scaling
                           x_axis_type='log',
                           width=400, height=400)

                p.xaxis.formatter = NumeralTickFormatter(format="0")
                p.yaxis.formatter = NumeralTickFormatter(format="0.000")

                for source_name_group, source_data in group_data.groupby('source_file'):
                    source = ColumnDataSource(source_data)
                    color = source_colors[source_data['source_file'].iloc[0]]
                    # Add line and circle glyphs
                    p.line('lines', 'time', source=source, legend_label=source_name_group, line_width=2, color=color)
                    p.scatter('lines', 'time', source=source, size=8, legend_label=source_name_group, color=color)

                p.legend.title = "File"
                p.legend.location = "top_left"

                plots.append(p)

            # Add all plots for the same function in one row
            function_rows.append(row(plots))

        # Add summary plot for total average times
        summary_plot = figure(title="Total Average Times by Type",
                              x_axis_label="Source File",
                              y_axis_label="Total Average Time in seconds",
                              # logarithmic scaling
                              x_axis_type='log',
                              width=800, height=400)

        for file_name in total_averages:
            source = ColumnDataSource(pd.DataFrame(file_name['total_average']))
            color = source_colors[file_name['source_file']]

            summary_plot.line('lines', 'time', source=source, legend_label=file_name['source_file'], line_width=2, color=color)
            summary_plot.scatter('lines', 'time', source=source, size=8, legend_label=file_name['source_file'], color=color)

        summary_plot.xaxis.major_label_orientation = 1
        summary_plot.xaxis.formatter = NumeralTickFormatter(format="0")
        summary_plot.yaxis.formatter = NumeralTickFormatter(format="0.000")

        summary_plot.legend.title = "File"
        summary_plot.legend.location = "top_left"

        function_rows.append(row(summary_plot))
        # Show all plots
        show(column(function_rows))


        # calculate percentages
        rows = []
        for entry in total_averages:
            source_file = entry['source_file']
            for lines, time in entry['total_average'].items():
                rows.append({'lines': lines, 'source_file': source_file, 'time': time})

        # Create DataFrame
        df = pd.DataFrame(rows)

        # Merge with the Slow source_file times for comparison
        df = df.merge(
            df[df["source_file"] == "Slow"][["lines", "time"]].rename(columns={"time": "slow_time"}),
            on="lines",
            how="left"
        )

        # Calculate differences in seconds and percentage
        df["time_difference_seconds"] = df["time"] - df["slow_time"]
        df["time_difference_percentage"] = (df["time_difference_seconds"] / df["slow_time"]) * 100

        # Display the resulting dataframe
        print(df.to_string())

    except Exception as e:
        print(f"Error processing data: {e}")

# Run the calculation
if __name__ == "__main__":
    calculate_average_times(file_names)
