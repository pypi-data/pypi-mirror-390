# -----------------------------------------------------------------------------------------------------
# WaLSAtools: Wave analysis tools
# Copyright (C) 2025 WaLSA Team - Shahin Jafarzadeh
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

from .analysis_modules.WaLSA_detrend_apod import WaLSA_detrend_apod
from .analysis_modules.WaLSA_speclizer import WaLSA_speclizer
from .analysis_modules.WaLSA_k_omega import WaLSA_k_omega
from .analysis_modules.WaLSA_pod import WaLSA_pod
from .analysis_modules.WaLSA_cross_spectra import WaLSA_cross_spectra
from .analysis_modules.WaLSA_io import WaLSA_save_pdf, WaLSA_histo_opt
from .analysis_modules.WaLSA_plot_k_omega import WaLSA_plot_k_omega
from .WaLSAtools import WaLSAtools

__all__ = ['WaLSAtools', 'WaLSA_detrend_apod', 'WaLSA_speclizer',
           'WaLSA_save_pdf', 'WaLSA_histo_opt', 'WaLSA_plot_k_omega', 
           'WaLSA_k_omega', 'WaLSA_pod', 'WaLSA_cross_spectra']
