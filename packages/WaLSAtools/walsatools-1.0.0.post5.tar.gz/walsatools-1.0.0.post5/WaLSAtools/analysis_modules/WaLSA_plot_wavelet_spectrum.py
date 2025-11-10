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


import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from mpl_toolkits.axes_grid1 import make_axes_locatable

def WaLSA_plot_wavelet_spectrum(t, power, periods, sig_slevel, coi, dt, normalize_power=False,
                                title='Wavelet Power Spectrum', ylabel='Period [s]', xlabel='Time [s]', 
                                colorbar_label='Power (%)', ax=None, colormap='custom', removespace=False):
    """Plots the wavelet power spectrum of a given signal.

    Parameters:
    - t (array-like): Time values for the signal.
    - power (2D array-like): Wavelet power spectrum.
    - periods (array-like): Period values corresponding to the power.
    - sig_slevel (2D array-like): Significance levels of the power spectrum.
    - coi (array-like): Cone of influence, showing where edge effects might be present.
    - dt (float): Time interval between successive time values.
    - normalize_power (bool): If True, normalize power to 0-100%. Default is False.
    - title (str): Title of the plot. Default is 'Wavelet Power Spectrum'.
    - ylabel (str): Y-axis label. Default is 'Period [s]'.
    - xlabel (str): X-axis label. Default is 'Time [s]'.
    - colorbar_label (str): Label for the color bar. Default is 'Power (%)'.
    - ax (matplotlib axis, optional): Axis to plot on. Default is None, which creates a new figure and axis.
    - colormap (str or colormap, optional): Colormap to be used. Default is 'custom'.
    - removespace (bool, optional): If True, limits the maximum y-range to the peak of the cone of influence.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(12, 6))

    # Custom colormap with white at the lower end
    if colormap == 'custom':
        cmap = LinearSegmentedColormap.from_list('custom_white', ['white', 'blue', 'green', 'yellow', 'red'], N=256)
    else:
        cmap = plt.get_cmap(colormap)

    # Normalize power if requested
    if normalize_power:
        power = 100 * power / np.nanmax(power)

    # Define a larger number of levels to create a continuous color bar
    levels = np.linspace(np.nanmin(power), np.nanmax(power), 100)

    # Plot the wavelet power spectrum
    CS = ax.contourf(t, periods, power, levels=levels, cmap=cmap, extend='neither')  # Removed 'extend' mode for straight ends

    # 95% significance contour
    ax.contour(t, periods, sig_slevel, levels=[1], colors='k', linewidths=[1.0])

    if removespace:
        max_period = np.max(coi)
    else:
        max_period = np.max(periods)

    # Cone-of-influence
    ax.plot(t, coi, '-k', lw=2)

    ax.fill(np.concatenate([t, t[-1:] + dt, t[-1:] + dt, t[:1] - dt, t[:1] - dt]),
            np.concatenate([coi, [1e-9], [max_period], [max_period], [1e-9]]),
            'k', alpha=0.3, hatch='x')

    # Log scale for periods
    ax.set_ylim([np.min(periods), max_period])
    ax.set_yscale('log', base=10)
    ax.yaxis.set_major_formatter(ticker.ScalarFormatter())
    ax.ticklabel_format(axis='y', style='plain')
    ax.invert_yaxis()

    # Set axis limits and labels
    ax.set_xlim([t.min(), t.max()])
    ax.set_ylabel(ylabel, fontsize=14)
    ax.set_xlabel(xlabel, fontsize=14)
    ax.tick_params(axis='both', which='major', labelsize=12)
    ax.set_title(title, fontsize=16)

    # Add a secondary y-axis for frequency in Hz
    ax_freq = ax.twinx()
    # Set limits for the frequency axis based on the `max_period` used for the period axis
    min_frequency = 1 / max_period
    max_frequency = 1 / np.min(periods)
    ax_freq.set_yscale('log', base=10)
    ax_freq.set_ylim([max_frequency, min_frequency])  # Adjust frequency range properly
    ax_freq.yaxis.set_major_formatter(ticker.ScalarFormatter())
    ax_freq.ticklabel_format(axis='y', style='plain')
    ax_freq.invert_yaxis()
    ax_freq.set_ylabel('Frequency (Hz)', fontsize=14)
    ax_freq.tick_params(axis='both', which='major', labelsize=12)

    # Add color bar on top with minimal distance
    divider = make_axes_locatable(ax)
    cax = divider.append_axes('top', size='5%', pad=0.01)  # Use 'pad=0.01' for a small fixed distance
    cbar = plt.colorbar(CS, cax=cax, orientation='horizontal')

    # Move color bar label to the top of the bar
    cbar.set_label(colorbar_label, fontsize=12, labelpad=5)
    cbar.ax.tick_params(labelsize=10, direction='out', top=True, labeltop=True, bottom=False, labelbottom=False)
    cbar.ax.xaxis.set_label_position('top')

    # Adjust layout if a new figure was created
    if ax is None:
        plt.tight_layout()
        plt.show()
