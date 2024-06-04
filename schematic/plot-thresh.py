import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

def save_variable_distribution(ncdata, variable_name, output_dir='./'):
    """
    Saves the KDE of the given variable from the NetCDF dataset as a PNG with a vertical line at the 95th percentile.

    Parameters:
    - ncdata: xarray.Dataset, the loaded NetCDF dataset
    - variable_name: str, the name of the variable to plot
    - output_dir: str, the directory to save the output PNG files
    """
    # Extract the variable data
    variable_data = ncdata[variable_name]

    if variable_name == 'wdswe':
        print("flip!")
        variable_data = -variable_data

    # Flatten the variable data to create the KDE
    variable_values = variable_data.values.flatten()

    # Plot the KDE
    plt.figure(figsize=(10, 6))

    scale_offset = 1.15
    font_size = 16  # Adjust this value as needed

    if variable_name == 'wdswe':
        percentile_95th = np.percentile(variable_values, 5)
        sns.kdeplot(variable_values, fill=True, color='red')
        plt.title(f'PDF of daily snowmelt (dSWE) values for JRA (SRB)', fontsize=font_size+2)
        plt.text(scale_offset*percentile_95th, plt.ylim()[1] * 0.9, f'$t_{{dSWE}}$ = {percentile_95th:.1f} mm/day', color='black', ha='right', fontsize=font_size)
        plt.xlabel('Snowmelt (dSWE, mm/day)', fontsize=font_size)
        plt.xlim(-10, 10)  # Set x-axis limits for dSWE
    elif variable_name == 'wrof':
        percentile_95th = np.percentile(variable_values, 95)
        sns.kdeplot(variable_values, fill=True, color='blue')
        plt.title(f'PDF of daily surface runoff (ROF) values for JRA (SRB)', fontsize=font_size+2)
        plt.text(scale_offset*percentile_95th, plt.ylim()[1] * 0.9, f'$t_{{ROF}}$ = {percentile_95th:.1f} mm/day', color='black', ha='left', fontsize=font_size)
        plt.xlabel('Surface runoff (ROF, mm/day)', fontsize=font_size)
        plt.xlim(0, 5)
    else:
        percentile_95th = np.percentile(variable_values, 95)
        sns.kdeplot(variable_values, fill=True, color='lightblue')
        plt.title(f'PDF of daily {variable_name} values for JRA (SRB)', fontsize=font_size+2)
        plt.text(scale_offset*percentile_95th, plt.ylim()[1] * 0.9, f'95th percentile = {percentile_95th:.1f} mm/day', color='black', ha='left', fontsize=font_size)
        plt.xlabel(variable_name, fontsize=font_size)

    print(percentile_95th)

    # Add a vertical line for the 95th percentile
    plt.axvline(percentile_95th, color='black', linestyle='--', linewidth=2.0)
    # Set labels and title
    plt.ylabel('Density', fontsize=font_size)

    # Increase tick label sizes
    plt.xticks(fontsize=font_size)
    plt.yticks(fontsize=font_size)

    # Save the plot as a PNG file
    output_file = f"{output_dir}/{variable_name}_distribution.pdf"
    plt.savefig(output_file, bbox_inches='tight')
    plt.close()

# Load the NetCDF file
ncdata = xr.open_dataset("../output/srb/tseries/tseries_JRA_srb_95.nc")

# Variables to plot
variables_to_plot = ["wdswe", "wrof"]

# Loop over the variables and plot their distribution
for variable in variables_to_plot:
    save_variable_distribution(ncdata, variable)
