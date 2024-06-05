import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from scipy.stats import gaussian_kde

def save_variable_distribution(ncdata, variable_name, output_dir='./'):
    """
    Saves the KDE of the given variable from the NetCDF dataset as a PDF with a vertical line at the 95th percentile.

    Parameters:
    - ncdata: xarray.Dataset, the loaded NetCDF dataset
    - variable_name: str, the name of the variable to plot
    - output_dir: str, the directory to save the output PDF files
    """
    # Extract the variable data
    variable_data = ncdata[variable_name]
    if variable_name == 'wdswe':
        print("flip!")
        variable_data = -variable_data

    # Flatten the variable data to create the KDE
    variable_values = variable_data.values.flatten()

    # Create a KDE object and calculate the density at a range of values
    kde = gaussian_kde(variable_values)
    x_values = np.linspace(variable_values.min(), variable_values.max(), 200)
    density = kde(x_values)

    # Normalize the density to ensure the sum equals 1 (histogram-like)
    density /= density.sum()

    plt.figure(figsize=(10, 6))
    font_size = 24
    scale_offset = 1.15

    # Plot the KDE
    if variable_name == 'wdswe':
        plt.fill_between(x_values, density, alpha=0.8, color='pink')
        percentile_95th = np.percentile(variable_values, 5)
        plt.plot(x_values, density, color='darkred')
        plt.ylim(0, np.ceil(max(density)*10)/10 - 0.06)
        plt.yticks(np.arange(0, np.ceil(max(density)*10)/10, 0.1))
        plt.xlim(-10, 10)
        plt.title(f'PDF of dSWE values for JRA (SRB)', fontsize=font_size+1)
        plt.text(scale_offset*percentile_95th, plt.ylim()[1] * 0.8, f'$t_{{dSWE}}$ = {percentile_95th:.1f} mm/d', color='black', ha='right', fontsize=font_size-2)
        plt.xlabel('Snowmelt (dSWE, mm/day)', fontsize=font_size)
        plt.xticks(range(-9, 9 + 1, 3))
    elif variable_name == 'wrof':
        plt.fill_between(x_values, density, alpha=0.8, color='lightblue')
        plt.plot(x_values, density, color='darkblue')
        percentile_95th = np.percentile(variable_values, 95)
        plt.ylim(0, np.ceil(max(density)*10)/10 - 0.06)
        plt.yticks(np.arange(0, np.ceil(max(density)*10)/10, 0.1))
        plt.xlim(0, 5)
        plt.title(f'PDF of daily ROF values for JRA (SRB)', fontsize=font_size+1)
        plt.text(scale_offset*percentile_95th, plt.ylim()[1] * 0.8, f'$t_{{ROF}}$ = {percentile_95th:.1f} mm/d', color='black', ha='left', fontsize=font_size-2)
        plt.xlabel('Surface runoff (ROF, mm/day)', fontsize=font_size)
    else:
        percentile_95th = np.percentile(variable_values, 95)
        sns.kdeplot(variable_values, fill=True, color='lightblue')
        plt.title(f'PDF of daily {variable_name} values for JRA (SRB)', fontsize=font_size+1)
        plt.text(scale_offset*percentile_95th, plt.ylim()[1] * 0.8, f'95th percentile = {percentile_95th:.1f} mm/d', color='black', ha='left', fontsize=font_size-2)
        plt.xlabel(variable_name, fontsize=font_size)

    plt.axvline(percentile_95th, color='black', linestyle='--', linewidth=2)

    plt.ylabel('Density', fontsize=font_size)
    plt.xticks(fontsize=font_size)
    plt.yticks(fontsize=font_size)
    # plt.legend(fontsize=font_size-2)  # Optionally disable the legend

    # Save the plot as a PDF file
    output_file = f"{output_dir}/{variable_name}_distribution.pdf"
    plt.savefig(output_file, bbox_inches='tight')
    plt.close()

def save_variable_distribution1(ncdata, variable_name, output_dir='./'):
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
    font_size = 24  # Adjust this value as needed

    if variable_name == 'wdswe':
        percentile_95th = np.percentile(variable_values, 5)
        sns.kdeplot(variable_values, fill=True, color='red')
        plt.title(f'PDF of dSWE values for JRA (SRB)', fontsize=font_size+1)
        plt.text(scale_offset*percentile_95th, plt.ylim()[1] * 0.9, f'$t_{{dSWE}}$ = {percentile_95th:.1f} mm/d', color='black', ha='right', fontsize=font_size-2)
        plt.xlabel('Snowmelt (dSWE, mm/day)', fontsize=font_size)
        plt.xlim(-10, 10)  # Set x-axis limits for dSWE
    elif variable_name == 'wrof':
        percentile_95th = np.percentile(variable_values, 95)
        sns.kdeplot(variable_values, fill=True, color='blue')
        plt.title(f'PDF of daily ROF values for JRA (SRB)', fontsize=font_size+1)
        plt.text(scale_offset*percentile_95th, plt.ylim()[1] * 0.9, f'$t_{{ROF}}$ = {percentile_95th:.1f} mm/d', color='black', ha='left', fontsize=font_size-2)
        plt.xlabel('Surface runoff (ROF, mm/day)', fontsize=font_size)
        plt.xlim(0, 5)
    else:
        percentile_95th = np.percentile(variable_values, 95)
        sns.kdeplot(variable_values, fill=True, color='lightblue')
        plt.title(f'PDF of daily {variable_name} values for JRA (SRB)', fontsize=font_size+1)
        plt.text(scale_offset*percentile_95th, plt.ylim()[1] * 0.9, f'95th percentile = {percentile_95th:.1f} mm/d', color='black', ha='left', fontsize=font_size-2)
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
