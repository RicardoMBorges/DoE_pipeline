# data_processing.py

import os
import pandas as pd
import glob
import numpy as np
from scipy.signal import correlate

### USE
# import data_processing as dp

# ex.: normalized_df = dp.min_max_normalize(combined_df)

  # Ensure that the Python file data_processing.py is in the same directory as your Jupyter Notebook or in a directory that's on the Python path.
  # If you make changes to data_processing.py, you might need to reload the module in your Jupyter Notebook. 
  # You can use the %load_ext autoreload and %autoreload 2 magic commands at the start of your notebook for automatic reloading.





### IMPORT DATA 
def extract_data(file_path):
    data = []
    start_extraction = False

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if not line:  # Stop at the first empty line
                if start_extraction:
                    break
                continue
            if line.startswith("R.Time (min)"):  # Start extraction after this line
                start_extraction = True
                continue
            if start_extraction:
                columns = line.split()
                if len(columns) == 2:  # Ensure only two columns
                    columns = [col.replace(',', '.') for col in columns]
                    data.append(columns)

    return data

def combine_and_trim_data(input_folder, output_folder, retention_time_start, retention_time_end):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for file_name in os.listdir(input_folder):
        if file_name.endswith(".txt"):
            file_path = os.path.join(input_folder, file_name)
            data = extract_data(file_path)

            # Save the extracted data to a CSV
            output_file_path = os.path.join(output_folder, f"{os.path.splitext(file_name)[0]}_table.csv")
            with open(output_file_path, 'w') as output_file:
                for row in data:
                    output_file.write('\t'.join(row) + '\n')

    # Combine all *_table.csv files into one DataFrame
    file_list = glob.glob(os.path.join(output_folder, '*_table.csv'))
    combined_df = pd.DataFrame()

    for file in file_list:
        column_name = os.path.basename(file).split('_table.csv')[0]
        df = pd.read_csv(file, delimiter='\t', header=None)
        if combined_df.empty:
            combined_df["RT(min)"] = df.iloc[:, 0]
        combined_df[column_name] = df.iloc[:, 1]

    # Ensure "RT(min)" is a string and process
    if combined_df["RT(min)"].dtype != "object":
        combined_df["RT(min)"] = combined_df["RT(min)"].astype(str)

    combined_df["RT(min)"] = pd.to_numeric(combined_df["RT(min)"].str.replace(',', '.'), errors="coerce")
    
    # Replace NaN with 0
    combined_df["RT(min)"] = combined_df["RT(min)"].fillna(0)
    combined_df = combined_df.fillna(0)  # Replace all NaN values with 0

    # Trim the DataFrame to the specified retention time range
    start_index = (combined_df["RT(min)"] - retention_time_start).abs().idxmin()
    end_index = (combined_df["RT(min)"] - retention_time_end).abs().idxmin()
    combined_df = combined_df.loc[start_index:end_index].reset_index(drop=True)

    # Save the combined and trimmed DataFrame
    combined_output_file = os.path.join(output_folder, "combined_data.csv")
    combined_df.to_csv(combined_output_file, sep=";", index=False)

    return combined_df



# Example usage
# input_folder = 'path_to_input_folder'
# output_folder = 'path_to_output_folder'
# retention_time_start = 2
# retention_time_end = 30
# combined_df2 = combine_and_trim_data(input_folder, output_folder, retention_time_start, retention_time_end)

def plot_interactive_peaks(data, column, rt_column='RT(min)', peaks=None, baseline=None, corrected_intensity=None):
    """
    Plots an interactive graph for the given column with original intensity, baseline, corrected intensity, and peaks.
    
    Parameters:
        data (pd.DataFrame): The dataset containing the chromatogram data.
        column (str): The column name to plot.
        rt_column (str): The name of the column containing retention times (default: 'RT(min)').
        peaks (array-like): Indices of detected peaks (optional).
        baseline (array-like): Baseline correction values (optional).
        corrected_intensity (array-like): Corrected intensity values (optional).
    """
    # Extract intensity values
    intensity_values = data[column].fillna(0).values

    # Compute baseline and corrected intensity if not provided
    if baseline is None or corrected_intensity is None:
        from scipy.signal import savgol_filter
        baseline = savgol_filter(intensity_values, window_length=51, polyorder=3)
        corrected_intensity = intensity_values - baseline
    
    # Compute peaks if not provided
    if peaks is None:
        from scipy.signal import find_peaks
        peaks, _ = find_peaks(corrected_intensity, height=1000, prominence=2000, distance=2, width=(2, None))

    # Create a Plotly figure
    fig = go.Figure()

    # Add original intensity trace
    fig.add_trace(go.Scatter(
        x=data[rt_column],
        y=intensity_values,
        mode='lines',
        name='Original Intensity'
    ))

    # Add corrected intensity trace
    fig.add_trace(go.Scatter(
        x=data[rt_column],
        y=corrected_intensity,
        mode='lines',
        name='Corrected Intensity'
    ))

    # Add baseline trace
    fig.add_trace(go.Scatter(
        x=data[rt_column],
        y=baseline,
        mode='lines',
        name='Baseline',
        line=dict(dash='dash')
    ))

    # Add detected peaks
    fig.add_trace(go.Scatter(
        x=data[rt_column][peaks],
        y=corrected_intensity[peaks],
        mode='markers',
        name='Peaks',
        marker=dict(color='red', size=10)
    ))

    # Update layout for zoomable and interactive features
    fig.update_layout(
        title=f"Interactive Peaks for {column}",
        xaxis_title="RT (min)",
        yaxis_title="Intensity",
        legend_title="Legend",
        hovermode="closest"
    )

    # Show the plot
    fig.show()

import os
import pandas as pd
import glob

# Extract data function remains the same
def extract_data2(file_path):
    data = []
    start_extraction = False

    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith("R.Time (min)"):
                start_extraction = True
                continue
            if start_extraction:
                columns = line.strip().split()
                if len(columns) == 2:
                    # Replace commas with dots in each column
                    columns = [col.replace(',', '.') for col in columns]
                    data.append(columns)

    return data
    

# Updated combine function to have a unique RT(min) column
def combine_data2(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Process each file in the input folder
    for file_name in os.listdir(input_folder):
        if file_name.endswith(".txt"):
            file_path = os.path.join(input_folder, file_name)
            data = extract_data(file_path)

            # Save each extracted data into a new .csv file
            output_file_path = os.path.join(output_folder, f"{os.path.splitext(file_name)[0]}_table.csv")
            with open(output_file_path, 'w') as output_file:
                for row in data:
                    output_file.write('\t'.join(row) + '\n')

    # List all saved *_table.csv files
    file_list = glob.glob(os.path.join(output_folder, '*_table.csv'))

    # Initialize an empty dictionary to store dataframes with varying sizes
    data_frames = {}

    # Read the first file to establish a common RT(min) axis
    first_file = file_list[0]
    base_df = pd.read_csv(first_file, delimiter='\t', header=None, names=["RT(min)", os.path.basename(first_file).split('_table.csv')[0]])

    # Use the RT(min) column from the first file as the reference axis
    rt_column = base_df["RT(min)"]

    # Store the first file's data excluding the RT(min) column
    data_frames[os.path.basename(first_file).split('_table.csv')[0]] = base_df.iloc[:, 1]

    # Read each subsequent file and align its data to the reference RT(min)
    for file in file_list[1:]:
        column_name = os.path.basename(file).split('_table.csv')[0]
        df = pd.read_csv(file, delimiter='\t', header=None, names=["RT(min)", column_name])

        # Align data using the reference RT(min) column
        aligned_df = pd.merge(rt_column.to_frame(), df, on="RT(min)", how="left")
        data_frames[column_name] = aligned_df[column_name]

    # Combine all dataframes into one, with the common RT(min) column
    combined_df = pd.concat([rt_column] + list(data_frames.values()), axis=1)

    # Substitute NaN values with zeros
    combined_df.fillna(0, inplace=True)

    # Save the combined DataFrame to a CSV file
    combined_df.to_csv(os.path.join(output_folder, "combined_data.csv"), sep=";", index=False)

    return combined_df

### REMOVE UNWANTED REGIONS
def remove_unwanted_regions(df, start_value, end_value):
    """
    Remove unwanted regions by substituting sample values with zeros between specified 
    start and end values in the RT(min) axis.

    Parameters:
    df (pd.DataFrame): DataFrame containing the data.
    start_value (float/int): Starting value of the RT(min) range.
    end_value (float/int): Ending value of the RT(min) range.

    Returns:
    pd.DataFrame: DataFrame with substituted values.
    
    # Example usage
    start = 2  # Starting value of RT(min) for substitution
    end = 5    # Ending value of RT(min) for substitution
    modified_df = remove_unwanted_regions(combined_df.copy(), start, end)
    """
    # Identify the rows where RT(min) is within the specified range
    rows_to_substitute = df['RT(min)'].between(start_value, end_value)

    # Columns to be modified (excluding RT(min))
    sample_columns = [col for col in df.columns if col != 'RT(min)']

    # Substitute values with zeros in the specified range for all sample columns
    df.loc[rows_to_substitute, sample_columns] = 0

    return df
##


### ALIGNMENT FUNCTIONS
def align_samples(df, reference_column):
    """
    Function to align samples to a Reference Sample
    This method assumes linear shifts and may not work well with non-linear distortions.
    The choice of reference sample can affect the results.
    The data should be appropriately scaled or normalized if necessary.
    """
    ref_signal = df[reference_column]
    max_shifts = {}
    for column in df.columns:
        if column != 'RT(min)' and column != reference_column:
            shift = np.argmax(correlate(df[column], ref_signal)) - (len(ref_signal) - 1)
            max_shifts[column] = shift
            df[column] = np.roll(df[column], -shift)
    return df, max_shifts

# Align samples
#aligned_df, shifts = dp.align_samples(combined_df, 'Sample1')
##


# Function to align samples to a median
def align_samples_to_median(df):
    """
    We calculate the median profile across all samples for each time point.
    Each sample is then aligned to this median profile using cross-correlation.
    The shifts are calculated and applied to each sample to align them.
    """
    median_profile = df.drop('RT(min)', axis=1).median(axis=1)
    max_shifts = {}
    for column in df.columns:
        if column != 'RT(min)':
            shift = np.argmax(correlate(df[column], median_profile)) - (len(median_profile) - 1)
            max_shifts[column] = shift
            df[column] = np.roll(df[column], -shift)
    return df, max_shifts

# Align samples to the median profile
#aligned_df, shifts = align_samples_to_median(combined_df)
##    We calculate the standard deviation profile across all samples.


# Function to align samples using Standard Deviation
def align_samples_using_std(df):
    """
    Less common for direct alignment purposes, but it can be a useful method for identifying the degree of variability or inconsistency among your samples.
    We identify a stable region around the point of lowest standard deviation.
    We then align each sample to a reference sample (Sample1 in this case) but only focusing on this stable region.
    The shifts are then calculated and applied.
    """
    std_profile = df.drop('RT(min)', axis=1).std(axis=1)
    # Identify stable regions (low standard deviation)
    # For simplicity, let's assume we use the overall lowest std value
    stable_point = std_profile.idxmin()
    max_shifts = {}
    for column in df.columns:
        if column != 'RT(min)':
            # Align using the stable point
            stable_region = df.loc[stable_point-5:stable_point+5, column] # Adjust the range as needed
            shift = np.argmax(correlate(stable_region, df.loc[stable_point-5:stable_point+5, 'Sample1'])) - 5
            max_shifts[column] = shift
            df[column] = np.roll(df[column], -shift)
    return df, max_shifts

# Align samples using standard deviation
#aligned_df, shifts = align_samples_using_std(combined_df)
##


### NORMALIZATION FUNCTIONS
def min_max_normalize(df):
    """
    Min-max normalization scales the data so that it fits within a specific range, typically 0 to 1.
    """
    for column in df.columns:
        if column != 'RT(min)':
            min_val = df[column].min()
            max_val = df[column].max()
            df[column] = (df[column] - min_val) / (max_val - min_val)
    return df

#normalized_df = min_max_normalize(combined_df.copy())
##


# Z-score normalization.
def z_score_normalize(df):
    """
    Z-score normalization transforms the data to have a mean of 0 and a standard deviation of 1.
    """
    for column in df.columns:
        if column != 'RT(min)':
            mean_val = df[column].mean()
            std_val = df[column].std()
            df[column] = (df[column] - mean_val) / std_val
    return df

#normalized_df = z_score_normalize(combined_df.copy())
##


# Normalization by a Control.
def normalize_by_control(df, control_column):
    """
    Normalization by a control is specific to experimental designs where a control feature is available.
    """
    control = df[control_column]
    for column in df.columns:
        if column != 'RT(min)' and column != control_column:
            df[column] = df[column] / control
    return df

#normalized_df = normalize_by_control(combined_df.copy(), 'ControlSample')
##


### SCALING FUNCTIONS
def min_max_scale(df, new_min=0, new_max=1):
    """
    This is similar to min-max normalization but can be used to scale the data to a range different from 0 to 1.
    """
    for column in df.columns:
        if column != 'RT(min)':
            min_val = df[column].min()
            max_val = df[column].max()
            df[column] = (df[column] - min_val) / (max_val - min_val) * (new_max - new_min) + new_min
    return df

#scaled_df = min_max_scale(combined_df.copy(), 0, 1)  # Example range 0 to 1
##


# Standard Scaling (Z-Score Scaling)
def standard_scale(df):
    """
    Standard Scaling (Z-Score Scaling) involves scaling the data to have a mean of 0 and a standard deviation of 1, similar to Z-score normalization.
    It's ideal for algorithms that assume the data is centered around zero and has a standard deviation of one.
    """
    for column in df.columns:
        if column != 'RT(min)':
            mean_val = df[column].mean()
            std_val = df[column].std()
            df[column] = (df[column] - mean_val) / std_val
    return df

#scaled_df = standard_scale(combined_df.copy())
##


# Robust scaling uses the median and the interquartile range, making it effective in cases where the data contains outliers.
def robust_scale(df):
    """
    Robust scaling uses the median and the interquartile range, making it effective in cases where the data contains outliers.
    """
    for column in df.columns:
        if column != 'RT(min)':
            median_val = df[column].median()
            Q1 = df[column].quantile(0.25)
            Q3 = df[column].quantile(0.75)
            IQR = Q3 - Q1
            df[column] = (df[column] - median_val) / IQR
    return df

#scaled_df = robust_scale(combined_df.copy())
##


### ANALYSIS
def plot_pca_scores(scores_df, pc_x, pc_y, explained_variance):
    """
    Create an interactive scatter plot for specified PCA components.

    Parameters:
    scores_df (pd.DataFrame): DataFrame containing PCA scores.
    pc_x (int): The principal component number for the x-axis.
    pc_y (int): The principal component number for the y-axis.
    explained_variance (list): List of explained variance ratios for each component.
    """
    # Create the scatter plot
    fig = px.scatter(scores_df, x=f'PC{pc_x}', y=f'PC{pc_y}', text=scores_df.index, title=f'PCA Score Plot: PC{pc_x} vs PC{pc_y}')

    # Update layout with titles and labels
    fig.update_layout(
        xaxis_title=f'PC{pc_x} ({explained_variance[pc_x-1]:.2f}%)',
        yaxis_title=f'PC{pc_y} ({explained_variance[pc_y-1]:.2f}%)'
    )

    # Add hover functionality
    fig.update_traces(marker=dict(size=7),
                      selector=dict(mode='markers+text'))

    # Show the interactive plot
    fig.show()
##

### VIP from PLS-DA
# Calculate the VIP scores from the fitted PLS model
def calculate_vip_scores(pls_model, X):
    t = pls_model.x_scores_  # Scores
    w = pls_model.x_weights_  # Weights
    q = pls_model.y_loadings_  # Loadings
    p, h = w.shape
    vip = np.zeros((p,))
    s = np.diag(t.T @ t @ q.T @ q).reshape(h, -1)
    total_s = np.sum(s)

    for i in range(p):
        weight = np.array([(w[i, j] / np.linalg.norm(w[:, j]))**2 for j in range(h)])
        vip[i] = np.sqrt(p * (s.T @ weight) / total_s)

    return vip
##



# STOCSY_LCDAD
def STOCSY_LCDAD(target,X,ppm):
    
    """
    Function designed to calculate covariance/correlation and plots its color coded projection of NMR spectrum
    Originally designed for NMR, but not limited to NMR
    
    Adapted for LC-DAD data
        
    target - driver peak to be used 
    X -      the data itself (samples as columns and chemical shifts as rows)
    ppm -    the axis 
    
    Created on Mon Feb 14 21:26:36 2022
    @author: R. M. Borges and Stefan Kuhn
    """
    
    import numpy as np
    from scipy import stats
    import matplotlib.pyplot as plt
    from matplotlib import collections as mc
    import pylab as pl
    import math
    import os
        
    if type(target) == float:
        idx = np.abs(ppm - target).idxmin() #axis='index') #find index for a given target
        target_vect = X.iloc[idx] #locs the values of the target(th) index from different 'samples'
    else:
        target_vect = target
    #print(target_vect)
    
    #compute Correlation and Covariance
    """Matlab - corr=(zscore(target_vect')*zscore(X))./(size(X,1)-1);"""
    corr = (stats.zscore(target_vect.T,ddof=1)@stats.zscore(X.T,ddof=1))/((X.T.shape[0])-1)
        
    """#Matlab - covar=(target_vect-mean(target_vect))'*(X-repmat(mean(X),size(X,1),1))./(size(X,1)-1);"""
    covar = (target_vect-(target_vect.mean()))@(X.T-(np.tile(X.T.mean(),(X.T.shape[0],1))))/((X.T.shape[0])-1)
        
    x = np.linspace(0, len(covar), len(covar))
    y = covar
    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    
    fig, axs = plt.subplots(1, 1, sharex=True, sharey=True, figsize=(16,4))
    norm = plt.Normalize(corr.min(), corr.max())
    lc = mc.LineCollection(segments, cmap='jet', norm=norm)
    lc.set_array(corr)
    lc.set_linewidth(2)
    line = axs.add_collection(lc)
    fig.colorbar(line, ax=axs)
    axs.set_xlim(x.min(), x.max())
    axs.set_ylim(y.min(), y.max())
    #axs.invert_xaxis()
        
    #This sets the ticks to ppm values
    minppm = min(ppm)
    maxppm = max(ppm)
    ticksx = []
    tickslabels = []
    if maxppm<30:
       ticks = np.linspace(int(math.ceil(minppm)), int(maxppm), int(maxppm)-math.ceil(minppm)+1)
    else:
       ticks = np.linspace(int(math.ceil(minppm / 10.0)) * 10, (int(math.ceil(maxppm / 10.0)) * 10)-10, int(math.ceil(maxppm / 10.0))-int(math.ceil(minppm / 10.0)))
    currenttick=0;
    for ppm in ppm:
       if currenttick<len(ticks) and ppm>ticks[currenttick]:
           position=int((ppm-minppm)/(maxppm-minppm)*max(x))
           if position<len(x):
               ticksx.append(x[position])
               tickslabels.append(ticks[currenttick])
           currenttick=currenttick+1
    plt.xticks(ticksx,tickslabels, fontsize=10)
    axs.set_xlabel('RT (min)', fontsize=12)
    axs.set_ylabel(f"Covariance with \n signal at {target:.2f} min", fontsize=12)
    axs.set_title(f'STOCSY from signal at {target:.2f} min', fontsize=14)

    text = axs.text(1, 1, '')
    lnx = plt.plot([60,60], [0,1.5], color='black', linewidth=0.3)
    lny = plt.plot([0,100], [1.5,1.5], color='black', linewidth=0.3)
    lnx[0].set_linestyle('None')
    lny[0].set_linestyle('None')

    def hover(event):
        if event.inaxes == axs:
            inv = axs.transData.inverted()
            maxcoord=axs.transData.transform((x[0], 0))[0]
            mincoord=axs.transData.transform((x[len(x)-1], 0))[0]
            ppm=((maxcoord-mincoord)-(event.x-mincoord))/(maxcoord-mincoord)*(maxppm-minppm)+minppm
            cov=covar[int(((maxcoord-mincoord)-(event.x-mincoord))/(maxcoord-mincoord)*len(covar))]
            cor=corr[int(((maxcoord-mincoord)-(event.x-mincoord))/(maxcoord-mincoord)*len(corr))]
            text.set_visible(True)
            text.set_position((event.xdata, event.ydata))
            text.set_text('{:.2f}'.format(ppm)+" min, covariance: "+'{:.6f}'.format(cov)+", correlation: "+'{:.2f}'.format(cor))
            lnx[0].set_data([event.xdata, event.xdata], [-1, 1])
            lnx[0].set_linestyle('--')
            lny[0].set_data([x[0],x[len(x)-1]], [cov,cov])
            lny[0].set_linestyle('--')
        else:
            text.set_visible(False)
            lnx[0].set_linestyle('None')
            lny[0].set_linestyle('None')
        fig.canvas.draw_idle()

    fig.canvas.mpl_connect("motion_notify_event", hover)    
    pl.show()
    if not os.path.exists('images'):
        os.mkdir('images')
    plt.savefig(f"images/stocsy_from_{target}.pdf", transparent=True, dpi=300)
    
    return corr, covar, fig



import numpy as np

def NMR_alignment(spectra, reference, method='PAFFT', seg_size=50, shift=None, lookahead=1):
    """
    Perform NMR alignment using PAFFT or RAFFT methods.

    Parameters:
        spectra (ndarray): 2D array of spectra to be shift corrected (D x N, where D is number of samples, N is number of data points).
        reference (ndarray): Reference spectrum (must be the same length as spectra).
        method (str): 'PAFFT' or 'RAFFT' to select the alignment method.
        seg_size (int): Segment size for PAFFT alignment.
        shift (int, optional): Maximum shift allowed for each segment.
        lookahead (int, optional): Allows the recursive algorithm to check local misalignments (for RAFFT).

    Returns:
        aligned_spectra (ndarray): Aligned spectra.
	
	Application: 
    
    from nmr_alignment import NMR_alignment
    
    # Example data preparation: Extracting the spectra and reference from your NMR data
    # Replace 'nmr_data' with your actual data variable
    spectra = nmr_data.iloc[:, 1:]  # Exclude the first index column
    reference = spectra.iloc[0].values  # Use the first row as the reference spectrum

    # Convert the dataframe to a numpy array
    spectra_array = spectra.values

    # Set parameters for the alignment
    seg_size = 50  # Segment size for PAFFT (adjust if needed)
    shift = None   # Optional, max shift value for PAFFT and RAFFT
    lookahead = 1  # Lookahead value for RAFFT

    # Calling the PAFFT alignment method
    try:
        aligned_spectra_pafft = NMR_alignment(spectra_array, reference, method='PAFFT', seg_size=seg_size, shift=shift)
        print("PAFFT aligned spectra shape:", aligned_spectra_pafft.shape)
    except Exception as e:
        print(f"Error in PAFFT alignment: {e}")

    # Calling the RAFFT alignment method
    try:
        aligned_spectra_rafft = NMR_alignment(spectra_array, reference, method='RAFFT', shift=shift, lookahead=lookahead)
        print("RAFFT aligned spectra shape:", aligned_spectra_rafft.shape)
    except Exception as e:
        print(f"Error in RAFFT alignment: {e}")
    """
    if method == 'PAFFT':
        return PAFFT_alignment(spectra, reference, seg_size, shift)
    elif method == 'RAFFT':
        return RAFFT_alignment(spectra, reference, shift, lookahead)
    else:
        raise ValueError("Invalid method specified. Choose either 'PAFFT' or 'RAFFT'.")

def PAFFT_alignment(spectra, reference, seg_size, shift=None):
    if len(reference) != spectra.shape[1]:
        raise ValueError("Reference and spectra must be of equal lengths.")
    elif len(reference) == 1:
        raise ValueError("Reference cannot be of length 1.")
    
    if shift is None:
        shift = len(reference)
    
    aligned_spectrum = []

    for i in range(spectra.shape[0]):
        startpos = 0
        aligned = []

        while startpos < len(spectra[i]):
            endpos = startpos + (seg_size * 2)

            # Adjust segment sizes to ensure equal lengths
            if endpos >= len(spectra[i]):
                samseg = spectra[i, startpos:]
                refseg = reference[startpos:]
            else:
                samseg = spectra[i, startpos + seg_size:endpos]
                refseg = reference[startpos + seg_size:endpos]
                minpos = find_min(samseg, refseg)
                endpos = startpos + minpos + seg_size
                samseg = spectra[i, startpos:endpos]
                refseg = reference[startpos:endpos]

            # Ensure segments are of equal length before FFT operation
            min_length = min(len(samseg), len(refseg))
            samseg = samseg[:min_length]
            refseg = refseg[:min_length]

            # Check for segment size compatibility
            if len(samseg) != len(refseg):
                raise ValueError(f"Segments are not equal after trimming: {len(samseg)} vs {len(refseg)}")

            # Pad segments to match FFT requirements
            max_length = max(len(samseg), len(refseg))
            samseg = np.pad(samseg, (0, max_length - len(samseg)), 'constant')
            refseg = np.pad(refseg, (0, max_length - len(refseg)), 'constant')

            # Debug check after padding
            if len(samseg) != len(refseg):
                raise ValueError(f"Segments are not equal even after padding: {len(samseg)} vs {len(refseg)}")

            # FFT cross-correlation to determine the lag
            M = len(refseg)
            diff = 1e6
            for i in range(20):
                curdiff = (2 ** i) - M
                if 0 < curdiff < diff:
                    diff = curdiff

            refseg = np.pad(refseg, (0, diff), 'constant')
            samseg = np.pad(samseg, (0, diff), 'constant')
            M += diff

            X = np.fft.fft(refseg)
            Y = np.fft.fft(samseg)
            R = X * np.conj(Y) / M
            rev = np.fft.ifft(R)
            vals = np.real(rev)

            maxpos = 0
            maxi = -np.inf

            shift = min(shift, M)

            for i in range(shift):
                if vals[i] > maxi:
                    maxi = vals[i]
                    maxpos = i
                if vals[-i - 1] > maxi:
                    maxi = vals[-i - 1]
                    maxpos = len(vals) - i - 1

            if maxi < 0.1:
                lag = 0
            elif maxpos > len(vals) // 2:
                lag = maxpos - len(vals) - 1
            else:
                lag = maxpos - 1

            # Apply the determined lag to shift the segment
            if lag == 0 or lag >= len(samseg):
                movedSeg = samseg
            elif lag > 0:
                ins = np.ones(lag) * samseg[0]
                movedSeg = np.concatenate([ins, samseg[:len(samseg) - lag]])
            else:
                lag = abs(lag)
                ins = np.ones(lag) * samseg[-1]
                movedSeg = np.concatenate([samseg[lag:], ins])

            aligned.extend(movedSeg)
            startpos = endpos + 1

        aligned_spectrum.append(aligned)

    # Pad aligned spectra to ensure all rows have the same length
    max_len = max(map(len, aligned_spectrum))
    aligned_spectrum = [np.pad(row, (0, max_len - len(row)), 'constant') for row in aligned_spectrum]

    return np.array(aligned_spectrum)

def RAFFT_alignment(spectra, reference, shift=None, lookahead=1):
    if len(reference) != spectra.shape[1]:
        raise ValueError("Reference and spectra must be of equal lengths.")
    elif len(reference) == 1:
        raise ValueError("Reference cannot be of length 1.")
    
    if shift is None:
        shift = len(reference)
    
    aligned_spectra = np.array([recur_align(spectrum, reference, shift, lookahead) for spectrum in spectra])
    return aligned_spectra

def recur_align(spectrum, reference, shift, lookahead):
    if len(spectrum) < 10:
        return spectrum

    lag = FFTcorr(spectrum, reference, shift)
    
    if lag == 0 and lookahead <= 0:
        return spectrum
    else:
        if lag == 0:
            lookahead -= 1

        aligned = move_segment(spectrum, lag)
        mid = find_mid(aligned)
        
        first_spectrum_half = aligned[:mid]
        first_reference_half = reference[:mid]
        second_spectrum_half = aligned[mid:]
        second_reference_half = reference[mid:]
        
        aligned1 = recur_align(first_spectrum_half, first_reference_half, shift, lookahead)
        aligned2 = recur_align(second_spectrum_half, second_reference_half, shift, lookahead)
        
        return np.concatenate([aligned1, aligned2])

def FFTcorr(spectrum, target, shift):
    M = len(target)
    diff = 1e6
    for i in range(20):
        curdiff = (2 ** i) - M
        if 0 < curdiff < diff:
            diff = curdiff

    target = np.pad(target, (0, diff), 'constant')
    spectrum = np.pad(spectrum, (0, diff), 'constant')
    M += diff

    X = np.fft.fft(target)
    Y = np.fft.fft(spectrum)
    R = X * np.conj(Y) / M
    rev = np.fft.ifft(R)
    vals = np.real(rev)

    maxpos = 0
    maxi = -np.inf
    shift = min(shift, M)

    for i in range(shift):
        if vals[i] > maxi:
            maxi = vals[i]
            maxpos = i
        if vals[-i - 1] > maxi:
            maxi = vals[-i - 1]
            maxpos = len(vals) - i - 1

    if maxi < 0.1:
        return 0
    if maxpos > len(vals) // 2:
        return maxpos - len(vals) - 1
    return maxpos - 1

def move_segment(seg, lag):
    if lag == 0 or lag >= len(seg):
        return seg
    elif lag > 0:
        ins = np.ones(lag) * seg[0]
        return np.concatenate([ins, seg[:-lag]])
    else:
        lag = abs(lag)
        ins = np.ones(lag) * seg[-1]
        return np.concatenate([seg[lag:], ins])

def find_mid(spec):
    M = len(spec) // 2
    specM = spec[M - M//4 : M + M//4]
    mid = np.argmin(specM) + M - M//4
    return mid

def find_min(samseg, refseg):
    return min(len(samseg), len(refseg))  # Placeholder function, may need refinement
