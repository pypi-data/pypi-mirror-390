# -----------------------------------------------------------------------------------------------------
# WaLSAtools - Wave analysis tools
# Copyright (C) 2025 WaLSA Team - Shahin Jafarzadeh et al.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
# http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# 
# Note: If you use WaLSAtools for research, please consider citing:
# Jafarzadeh, S., Jess, D. B., Stangalini, M. et al. 2025, Nature Reviews Methods Primers, 5, 21
# -----------------------------------------------------------------------------------------------------

from IPython.display import HTML, display # type: ignore
import shutil

single_series_parameters = {
    'fft': {
        'return_values': 'power, frequency, significance, amplitude',
        'parameters': {
            'signal': {'type': 'array', 'description': 'The input signal (1D).'},
            'time': {'type': 'array', 'description': 'The time array corresponding to the signal.'},
            'siglevel': {'type': 'float', 'description': 'Significance level for the confidence intervals. Default: 0.95.'},
            'nperm': {'type': 'int', 'description': 'Number of permutations for significance testing. Default: 1000.'},
            'nosignificance': {'type': 'bool', 'description': 'If True, skip significance calculation. Default: False.'},
            'apod': {'type': 'float', 'description': 'Extent of apodization edges (of a Tukey window). Default: 0.1.'},
            'pxdetrend': {'type': 'int', 'description': 'Subtract linear trend with time per pixel. Options: 1 (simple) or 2 (advanced). Default: 2.'},
            'polyfit': {'type': 'int', 'description': 'Degree of polynomial fit for detrending the data. If set, a polynomial fit (instead of linear) is applied. Default: None'},
            'meantemporal': {'type': 'bool', 'description': 'If True, apply simple temporal detrending by subtracting the mean signal from the data, skipping fitting procedures. Default: False.'},
            'meandetrend': {'type': 'bool', 'description': 'If True, subtract the linear trend with time for the image means (spatial detrending). Default: False.'},
            'recon': {'type': 'bool', 'description': 'If True, perform Fourier reconstruction of the input time series. This does not preserve amplitudes but is useful for examining frequencies far from the low-frequency range. Default: False.'},
            'resample_original': {'type': 'bool', 'description': 'If True, and if recon is set to True, approximate values close to the original are returned for comparison. Default: False.'},
            'nodetrendapod': {'type': 'bool', 'description': 'If True, neither detrending nor apodization is performed. Default: False.'},
            'amplitude': {'type': 'bool', 'description': ' If True, return the amplitudes of the Fourier transform. Default: False.'},
            'silent': {'type': 'bool', 'description': 'If True, suppress print statements. Default: False.'}
        }
    },
    'wavelet': {
        'return_values': 'power, period, significance, coi, gws_power, gws_significance, rgws_power',
        'parameters': {
            'signal': {'type': 'array', 'description': 'The input signal (1D).'},
            'time': {'type': 'array', 'description': 'The time array corresponding to the signal.'},
            'siglevel': {'type': 'float', 'description': 'Significance level for the confidence intervals. Default: 0.95.'},
            'nperm': {'type': 'int', 'description': 'Number of permutations for significance testing. Default: 1000.'},
            'mother': {'type': 'str', 'description': 'The mother wavelet function to use. Default: "morlet".'},
            'GWS': {'type': 'bool', 'description': 'If True, calculate the Global Wavelet Spectrum. Default: False.'},
            'RGWS': {'type': 'bool', 'description': 'If True, calculate the Refined Global Wavelet Spectrum (time-integrated power, excluding COI and insignificant areas). Default: False.'},
            'dj': {'type': 'float', 'description': 'Scale spacing. Smaller values result in better scale resolution but slower calculations. Default: 0.025.'},
            's0': {'type': 'float', 'description': 'Initial (smallest) scale of the wavelet. Default: 2 * dt.'},
            'J': {'type': 'int', 'description': 'Number of scales minus one. Scales range from s0 up to s0 * 2**(J * dj), giving a total of (J + 1) scales. Default: (log2(N * dt / s0)) / dj.'},
            'lag1': {'type': 'float', 'description': 'Lag-1 autocorrelation. Default: 0.0.'},
            'apod': {'type': 'float', 'description': 'Extent of apodization edges (of a Tukey window). Default: 0.1.'},
            'pxdetrend': {'type': 'int', 'description': 'Subtract linear trend with time per pixel. Options: 1 (simple) or 2 (advanced). Default: 2.'},
            'polyfit': {'type': 'int', 'description': 'Degree of polynomial fit for detrending the data. If set, a polynomial fit (instead of linear) is applied. Default: None'},
            'meantemporal': {'type': 'bool', 'description': 'If True, apply simple temporal detrending by subtracting the mean signal from the data, skipping fitting procedures. Default: False.'},
            'meandetrend': {'type': 'bool', 'description': 'If True, subtract the linear trend with time for the image means (spatial detrending). Default: False.'},
            'recon': {'type': 'bool', 'description': 'If True, perform Fourier reconstruction of the input time series. This does not preserve amplitudes but is useful for examining frequencies far from the low-frequency range. Default: False.'},
            'resample_original': {'type': 'bool', 'description': 'If True, and if recon is set to True, approximate values close to the original are returned for comparison. Default: False.'},
            'nodetrendapod': {'type': 'bool', 'description': 'If True, neither detrending nor apodization is performed. Default: False.'},
            'silent': {'type': 'bool', 'description': 'If True, suppress print statements. Default: False.'}
        }
    },
    'lombscargle': {
        'return_values': 'power, frequency, significance',
        'parameters': {
            'signal': {'type': 'array', 'description': 'The input signal (1D).'},
            'time': {'type': 'array', 'description': 'The time array corresponding to the signal.'},
            'siglevel': {'type': 'float', 'description': 'Significance level for the confidence intervals. Default: 0.95.'},
            'nperm': {'type': 'int', 'description': 'Number of permutations for significance testing. Default: 1000.'},
            'dy': {'type': 'array', 'description': 'Errors or observational uncertainties associated with the time series.'},
            'fit_mean': {'type': 'bool', 'description': 'If True, include a constant offset as part of the model at each frequency. This improves accuracy, especially for incomplete phase coverage.'},
            'center_data': {'type': 'bool', 'description': 'If True, pre-center the data by subtracting the weighted mean of the input data. This is especially important if fit_mean=False.'},
            'nterms': {'type': 'int', 'description': 'Number of terms to use in the Fourier fit. Default: 1.'},
            'normalization': {'type': 'str', 'description': 'The normalization method for the periodogram. Options: "standard", "model", "log", "psd". Default: "standard".'},
            'nosignificance': {'type': 'bool', 'description': 'If True, skip significance calculation. Default: False.'},
            'apod': {'type': 'float', 'description': 'Extent of apodization edges (of a Tukey window). Default: 0.1.'},
            'pxdetrend': {'type': 'int', 'description': 'Subtract linear trend with time per pixel. Options: 1 (simple) or 2 (advanced). Default: 2.'},
            'polyfit': {'type': 'int', 'description': 'Degree of polynomial fit for detrending the data. If set, a polynomial fit (instead of linear) is applied. Default: None'},
            'meantemporal': {'type': 'bool', 'description': 'If True, apply simple temporal detrending by subtracting the mean signal from the data, skipping fitting procedures. Default: False.'},
            'meandetrend': {'type': 'bool', 'description': 'If True, subtract the linear trend with time for the image means (spatial detrending). Default: False.'},
            'recon': {'type': 'bool', 'description': 'If True, perform Fourier reconstruction of the input time series. This does not preserve amplitudes but is useful for examining frequencies far from the low-frequency range. Default: False.'},
            'resample_original': {'type': 'bool', 'description': 'If True, and if recon is set to True, approximate values close to the original are returned for comparison. Default: False.'},
            'nodetrendapod': {'type': 'bool', 'description': 'If True, neither detrending nor apodization is performed. Default: False.'},
            'silent': {'type': 'bool', 'description': 'If True, suppress print statements. Default: False.'}
        }
    },
    'welch': {
        'return_values': 'power, frequency, significance',
        'parameters': {
            'signal': {'type': 'array', 'description': 'The 1D time series signal.'},
            'time': {'type': 'array', 'description': 'The time array corresponding to the signal.'},
            'nperseg': {'type': 'int', 'description': 'Length of each segment for analysis. Default: 256.'},
            'noverlap': {'type': 'int', 'description': 'Number of points to overlap between segments. Default: 128.'},
            'window': {'type': 'str', 'description': 'Type of window function used in the Welch method. Default: "hann".'},
            'siglevel': {'type': 'float', 'description': 'Significance level for confidence intervals. Default: 0.95.'},
            'nperm': {'type': 'int', 'description': 'Number of permutations for significance testing. Default: 1000.'},
            'silent': {'type': 'bool', 'description': 'If True, suppress print statements. Default: False.'}
        }
    },
    'emd': {
        'return_values': 'HHT_power, HHT_significance, HHT_frequency, psd_spectra, psd_significance, IMFs, IMF_significance, instantaneous_frequency',
        'parameters': {
            'signal': {'type': 'array', 'description': 'The input signal (1D).'},
            'time': {'type': 'array', 'description': 'The time array of the signal.'},
            'siglevel': {'type': 'float', 'description': 'Significance level for the confidence intervals. Default: 0.95.'},
            'nperm': {'type': 'int', 'description': 'Number of permutations for significance testing. Default: 1000.'},
            'EEMD': {'type': 'bool', 'description': 'If True, use Ensemble Empirical Mode Decomposition (EEMD) instead of Empirical Mode Decomposition (EMD). Default: False.'},
            'Welch_psd': {'type': 'bool', 'description': 'If True, calculate Welch PSD spectra instead of FFT PSD spectra (for the psd_spectra and psd_confidence_levels). Default: False.'},
            'significant_imfs': {'type': 'bool', 'description': 'If True, only significant IMFs and their associated parameters are retured. Default: False.'},
            'apod': {'type': 'float', 'description': 'Extent of apodization edges (of a Tukey window). Default: 0.1.'},
            'pxdetrend': {'type': 'int', 'description': 'Subtract linear trend with time per pixel. Options: 1 (simple) or 2 (advanced). Default: 2.'},
            'polyfit': {'type': 'int', 'description': 'Degree of polynomial fit for detrending the data. If set, a polynomial fit (instead of linear) is applied. Default: None.'},
            'meantemporal': {'type': 'bool', 'description': 'If True, apply simple temporal detrending by subtracting the mean signal from the data, skipping fitting procedures. Default: False.'},
            'meandetrend': {'type': 'bool', 'description': 'If True, subtract the linear trend with time for the image means (spatial detrending). Default: False.'},
            'recon': {'type': 'bool', 'description': 'If True, perform Fourier reconstruction of the input time series. This does not preserve amplitudes but is useful for examining frequencies far from the low-frequency range. Default: False.'},
            'resample_original': {'type': 'bool', 'description': 'If True, and if recon is set to True, approximate values close to the original are returned for comparison. Default: False.'},
            'nodetrendapod': {'type': 'bool', 'description': 'If True, neither detrending nor apodization is performed. Default: False.'},
            'silent': {'type': 'bool', 'description': 'If True, suppress print statements. Default: False.'}
        }
    },
    'k-omega': {
        'return_values': 'power, wavenumber, frequency, filtered_cube, spatial_fft_map, torus_map, spatial_fft_filtered_map, temporal_fft, temporal_filter, temporal_frequencies, spatial_frequencies',
        'parameters': {
            'signal': {'type': 'array', 'description': 'Input datacube, normally in the form of [x, y, t] or [t, x, y]. Note that the input datacube must have identical x and y dimensions. If not, the datacube will be cropped accordingly.'},
            'time': {'type': 'array', 'description': 'Time array corresponding to the input datacube.'},
            'pixelsize': {'type': 'float', 'description': 'Spatial sampling of the input datacube. If not given, it is plotted in units of "pixel".'},
            'filtering': {'type': 'bool', 'description': 'If True, filtering is applied, and the filtered datacube (filtered_cube) is returned. Otherwise, None is returned. Default: False.'},
            'f1': {'type': 'float', 'description': 'Optional lower (temporal) frequency to filter, in Hz.'},
            'f2': {'type': 'float', 'description': 'Optional upper (temporal) frequency to filter, in Hz.'},
            'k1': {'type': 'float', 'description': 'Optional lower (spatial) wavenumber to filter, in units of pixelsize^-1 (k = (2 * π) / wavelength).'},
            'k2': {'type': 'float', 'description': 'Optional upper (spatial) wavenumber to filter, in units of pixelsize^-1.'},
            'spatial_torus': {'type': 'bool', 'description': 'If True, makes the annulus used for spatial filtering have a Gaussian-shaped profile, useful for preventing aliasing. Default: True.'},
            'temporal_torus': {'type': 'bool', 'description': 'If True, makes the temporal filter have a Gaussian-shaped profile, useful for preventing aliasing. Default: True.'},
            'no_spatial_filt': {'type': 'bool', 'description': 'If True, ensures no spatial filtering is performed on the dataset (i.e., only temporal filtering is applied).'},
            'no_temporal_filt': {'type': 'bool', 'description': 'If True, ensures no temporal filtering is performed on the dataset (i.e., only spatial filtering is applied).'},
            'silent': {'type': 'bool', 'description': 'If True, suppresses the k-ω diagram plot.'},
            'smooth': {'type': 'bool', 'description': 'If True, power is smoothed. Default: True.'},
            'mode': {'type': 'int', 'description': 'Output power mode: 0 = log10(power) (default), 1 = linear power, 2 = sqrt(power) = amplitude.'},
            'processing_maps': {'type': 'bool', 'description': 'If True, the function returns the processing maps (spatial_fft_map, torus_map, spatial_fft_filtered_map, temporal_fft, temporal_filter, temporal_frequencies, spatial_frequencies). Otherwise, they are all returned as None. Default: False.'}
        }
    },
    'pod': {
        'return_values': 'pod_results',
        'parameters': {
            'signal': {'type': 'array', 'description': '3D data cube with shape (time, x, y) or similar.'},
            'time': {'type': 'array', 'description': '1D array representing the time points for each time step in the data.'},
            'num_modes': {'type': 'int, optional', 'description': 'Number of top modes to compute. Default is None (all modes).'},
            'num_top_frequencies': {'type': 'int, optional', 'description': 'Number of top frequencies to consider. Default is None (all frequencies).'},
            'top_frequencies': {'type': 'list, optional', 'description': 'List of top frequencies to consider. Default is None.'},
            'num_cumulative_modes': {'type': 'int, optional', 'description': 'Number of cumulative modes to consider. Default is None (all modes).'},
            'welch_nperseg': {'type': 'int, optional', 'description': "Number of samples per segment for Welch's method. Default is 150."},
            'welch_noverlap': {'type': 'int, optional', 'description': "Number of overlapping samples for Welch's method. Default is 25."},
            'welch_nfft': {'type': 'int, optional', 'description': 'Number of points for the FFT. Default is 2^14.'},
            'welch_fs': {'type': 'int, optional', 'description': 'Sampling frequency for the data. Default is 2.'},
            'nperm': {'type': 'int, optional', 'description': 'Number of permutations for significance testing. Default is 1000.'},
            'siglevel': {'type': 'float, optional', 'description': 'Significance level for the Welch spectrum. Default is 0.95.'},
            'timestep_to_reconstruct': {'type': 'int, optional', 'description': 'Timestep of the datacube to reconstruct using the top modes. Default is 0.'},
            'num_modes_reconstruct': {'type': 'int, optional', 'description': 'Number of modes to use for reconstruction. Default is None (all modes).'},
            'reconstruct_all': {'type': 'bool, optional', 'description': 'If True, reconstruct the entire time series using the top modes. Default is False.'},
            'spod': {'type': 'bool, optional', 'description': 'If True, perform Spectral Proper Orthogonal Decomposition (SPOD) analysis. Default is False.'},
            'spod_filter_size': {'type': 'int, optional', 'description': 'Filter size for SPOD analysis. Default is None.'},
            'spod_num_modes': {'type': 'int, optional', 'description': 'Number of SPOD modes to compute. Default is None.'},
            'print_results': {'type': 'bool, optional', 'description': 'If True, print a summary of results. Default is True.'}
        }
    },
    'dominantfreq': {
        'return_values': 'power, frequency, significance',
        'parameters': {
            'signal': 'Input signal array (1D or 2D).',
            'time': 'Time array corresponding to the signal.',
            'method': 'Analysis method (e.g., fft, wavelet, etc.).',
            'kwargs': 'Additional optional parameters for customization.'
        }
    }
}

cross_correlation_parameters = {
    'wavelet': {
        'return_values': 'cross_power, cross_period, cross_sig, cross_coi, coherence, coh_period, coh_sig, coh_coi, phase_angle',
        'parameters': {
            'data1': {'type': 'array', 'description': 'The first 1D time series signal.'},
            'data2': {'type': 'array', 'description': 'The second 1D time series signal.'},
            'time': {'type': 'array', 'description': 'The time array corresponding to the signals.'},
            'siglevel': {'type': 'float', 'description': 'Significance level for the confidence intervals. Default: 0.95.'},
            'nperm': {'type': 'int', 'description': 'Number of permutations for significance testing. Default: 1000.'},
            'mother': {'type': 'str', 'description': 'The mother wavelet function to use. Default: "morlet".'},
            'GWS': {'type': 'bool', 'description': 'If True, calculate the Global Wavelet Spectrum. Default: False.'},
            'RGWS': {'type': 'bool', 'description': 'If True, calculate the Refined Global Wavelet Spectrum (time-integrated power, excluding COI and insignificant areas). Default: False.'},
            'dj': {'type': 'float', 'description': 'Scale spacing. Smaller values result in better scale resolution but slower calculations. Default: 0.025.'},
            's0': {'type': 'float', 'description': 'Initial (smallest) scale of the wavelet. Default: 2 * dt.'},
            'J': {'type': 'int', 'description': 'Number of scales minus one. Scales range from s0 up to s0 * 2**(J * dj), giving a total of (J + 1) scales. Default: (log2(N * dt / s0)) / dj.'},
            'lag1': {'type': 'float', 'description': 'Lag-1 autocorrelation. Default: 0.0.'},
            'apod': {'type': 'float', 'description': 'Extent of apodization edges (of a Tukey window). Default: 0.1.'},
            'pxdetrend': {'type': 'int', 'description': 'Subtract linear trend with time per pixel. Options: 1 (simple) or 2 (advanced). Default: 2.'},
            'polyfit': {'type': 'int', 'description': 'Degree of polynomial fit for detrending the data. If set, a polynomial fit (instead of linear) is applied. Default: None.'},
            'meantemporal': {'type': 'bool', 'description': 'If True, apply simple temporal detrending by subtracting the mean signal from the data, skipping fitting procedures. Default: False.'},
            'meandetrend': {'type': 'bool', 'description': 'If True, subtract the linear trend with time for the image means (spatial detrending). Default: False.'},
            'recon': {'type': 'bool', 'description': 'If True, perform Fourier reconstruction of the input time series. This does not preserve amplitudes but is useful for examining frequencies far from the low-frequency range. Default: False.'},
            'resample_original': {'type': 'bool', 'description': 'If True, and if recon is set to True, approximate values close to the original are returned for comparison. Default: False.'},
            'nodetrendapod': {'type': 'bool', 'description': 'If True, neither detrending nor apodization is performed. Default: False.'},
            'silent': {'type': 'bool', 'description': 'If True, suppress print statements. Default: False.'}
        }
    },
    'welch': {
        'return_values': 'frequency, cospectrum, phase_angle, power_data1, power_data2, frequency_coherence, coherence',
        'parameters': {
            'data1': {'type': 'array', 'description': 'The first 1D time series signal.'},
            'data2': {'type': 'array', 'description': 'The second 1D time series signal.'},
            'time': {'type': 'array', 'description': 'The time array corresponding to the signals.'},
            'nperseg': {'type': 'int', 'description': 'Length of each segment for analysis. Default: 256.'},
            'noverlap': {'type': 'int', 'description': 'Number of points to overlap between segments. Default: 128.'},
            'window': {'type': 'str', 'description': 'Type of window function used in the Welch method. Default: "hann".'},
            'siglevel': {'type': 'float', 'description': 'Significance level for confidence intervals. Default: 0.95.'},
            'nperm': {'type': 'int', 'description': 'Number of permutations for significance testing. Default: 1000.'},
            'silent': {'type': 'bool', 'description': 'If True, suppress print statements. Default: False.'}
        }
    },
    'fft': {
        'return_values': 'frequency, cospectrum, phase_angle, power_data1, power_data2, frequency_coherence, coherence',
        'parameters': {
            'Warning': {
                'type': 'str',
                'description': 'FFT method selected. Cross-spectra calculations will use Welch instead, '
                            'which segments the signal into multiple parts to reduce noise sensitivity. '
                            'Adjust frequency resolution vs. noise reduction with "nperseg".'
            },
            'data1': {'type': 'array', 'description': 'The first 1D time series signal.'},
            'data2': {'type': 'array', 'description': 'The second 1D time series signal.'},
            'time': {'type': 'array', 'description': 'The time array corresponding to the signals.'},
            'nperseg': {'type': 'int', 'description': 'Length of each segment for analysis. Default: 256.'},
            'noverlap': {'type': 'int', 'description': 'Number of points to overlap between segments. Default: 128.'},
            'window': {'type': 'str', 'description': 'Type of window function used in the Welch method. Default: "hann".'},
            'siglevel': {'type': 'float', 'description': 'Significance level for confidence intervals. Default: 0.95.'},
            'nperm': {'type': 'int', 'description': 'Number of permutations for significance testing. Default: 1000.'},
            'silent': {'type': 'bool', 'description': 'If True, suppress print statements. Default: False.'}
        }
    }
}


# For the Jupyter-based interactive function
def display_parameters_html(method_name, category):
    """Display parameters as an HTML table (for Jupyter Notebooks)."""
    if category == 'Cross-correlation between two time series':
        parameter_definitions = cross_correlation_parameters
    else:
        parameter_definitions = single_series_parameters
    parameters = parameter_definitions.get(method_name, {}).get('parameters')
    if not parameters:
        display(HTML(f"<p><strong>No parameters available for method: {method_name}</strong></p>"))
        return

    # Check if there's a 'Warning' parameter defined explicitly
    warning_html = ''
    if 'Warning' in parameters:
        warning_html = f"""
        <div style="border: 2px solid #27AE60; padding: 10px; margin-left: 30px; margin-bottom: 15px; background-color: #E9F7EF; border-radius: 4px;">
            <strong style="color: #196F3D;">Note: </strong>{parameters['Warning']['description']}
        </div>
        """
        # Remove the Warning from parameters to avoid duplication in the table
        parameters = {k: v for k, v in parameters.items() if k != 'Warning'}

    # Parameters Table
    table = '<table style="border-collapse: collapse; border: 1px solid #222; width: calc(100% - 30px); box-sizing: border-box; margin-left: 30px; table-layout: auto;">'
    table += '<tr style="background-color: #fff;"><th colspan="3" style="text-align: left; color: #000; font-size: 110%;">Parameters (**kwargs)</th></tr>'
    table += '<tr style="background-color: #222;">'
    table += '<th style="color: #fff; border-right: 1px solid #ccc; text-align: left; white-space: nowrap;"><strong>Parameter</strong></th>'
    table += '<th style="color: #fff; border-right: 1px solid #ccc; text-align: left; white-space: nowrap;"><strong>Type</strong></th>'
    table += '<th style="color: #fff; text-align: left; width: 100%;"><strong>Description</strong></th>'
    table += '</tr>'
    for param, info in parameters.items():
        param_type = info['type']
        description = info['description']
        table += f'<tr>'
        table += f'<td style="border: 1px solid #222; padding: 8px; text-align: left; white-space: nowrap;">{param}</td>'
        table += f'<td style="border: 1px solid #222; padding: 8px; text-align: left; white-space: nowrap;">{param_type}</td>'
        table += f'<td style="border: 1px solid #222; padding: 8px; text-align: left;">{description}</td>'
        table += '</tr>'
    table += '</table>'
    
    # Display Warning above the table (if exists), then the table
    display(HTML(warning_html + table))

# For the Terminal-based interactive function
import textwrap
def display_parameters_text(method_name, category):
    """Display parameters as a plain text table for the terminal."""
    if category == 'b' or category == 'Cross-correlation between two time series':
        parameter_definitions = cross_correlation_parameters
    else:
        parameter_definitions = single_series_parameters    
    parameters = parameter_definitions.get(method_name, {}).get('parameters')
    if not parameters:
        print(f"No parameters available for method: {method_name}")
        return
    
    # Get terminal width
    terminal_width = shutil.get_terminal_size().columns
    # Calculate 90% of the width (and ensure it's an integer)
    line_width = int(terminal_width * 0.90)

    # Extract and display warning separately
    if 'Warning' in parameters:
        warning_text = parameters['Warning']['description']
        wrapper = textwrap.TextWrapper(width=line_width - 4, initial_indent='    ', subsequent_indent='    ')
        wrapped_warning = wrapper.fill(f"Note: {warning_text}")
        separator = ' ' * 4 + '-' * line_width
        print('\n' + separator)
        print(wrapped_warning)
        print(separator)
        # Remove Warning from parameters to avoid duplication
        parameters = {k: v for k, v in parameters.items() if k != 'Warning'}

    # Calculate column widths
    param_col_width = 20
    type_col_width = 8
    desc_col_width = line_width - param_col_width - type_col_width - 10  # 10 chars for separators and spacing

    separator = '    ' + '-' * line_width
    print(separator)
    print('    | Parameters (**kwargs):')
    print(separator)
    print(f'    | {"Parameter":<{param_col_width}} | {"Type":<{type_col_width}} | {"Description":<{desc_col_width}}')
    print(separator)

    for param, info in parameters.items():
        param_type = info['type']
        description = info['description']

        # Wrap description properly within the cell
        wrapper = textwrap.TextWrapper(width=desc_col_width)
        wrapped_description = wrapper.wrap(description)

        # Print first line with param and type
        print(f'    | {param:<{param_col_width}} | {param_type:<{type_col_width}} | {wrapped_description[0]:<{desc_col_width}}')

        # If there are more wrapped lines, print them with proper indentation
        for line in wrapped_description[1:]:
            print(f'    | {"":<{param_col_width}} | {"":<{type_col_width}} | {line:<{desc_col_width}}')

    print(separator)
