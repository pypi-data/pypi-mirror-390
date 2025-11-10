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

import subprocess
import shutil
import os
import stat
import numpy as np # type: ignore
from matplotlib.backends.backend_pdf import PdfPages # type: ignore

def WaLSA_save_pdf(fig, pdf_path, color_mode='RGB', dpi=300, bbox_inches=None, pad_inches=0):
    """
    Save a PDF from a Matplotlib figure with an option to convert to CMYK if Ghostscript is available.
    
    Parameters:
    - fig: Matplotlib figure object to save.
    - pdf_path: Path to save the PDF file.
    - color_mode: 'RGB' (default) to save in RGB, or 'CMYK' to convert to CMYK.
    - dpi: Resolution in dots per inch. Default is 300.
    - bbox_inches: Set to 'tight' to remove extra white space. Default is 'tight'.
    - pad_inches: Padding around the figure. Default is 0.
    """

    # Save the initial PDF in RGB format using fig.savefig to apply bbox_inches, pad_inches, and dpi
    if bbox_inches is None:
        # Save the initial PDF in RGB format
        with PdfPages(pdf_path) as pdf:
            pdf.savefig(fig, transparent=True)

        if color_mode.upper() == 'CMYK':
            # Check if Ghostscript is installed
            if shutil.which("gs") is not None:
                # Set permissions on the initial RGB PDF to ensure access for Ghostscript
                os.chmod(pdf_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)

                # Define a temporary path for the CMYK file
                temp_cmyk_path = pdf_path.replace('.pdf', '_temp_cmyk.pdf')

                # Run Ghostscript to create the CMYK PDF as a temporary file
                subprocess.run([
                    "gs", "-o", temp_cmyk_path,
                    "-sDEVICE=pdfwrite",
                    "-dProcessColorModel=/DeviceCMYK",
                    "-dColorConversionStrategy=/CMYK",
                    "-dNOPAUSE", "-dBATCH", "-dSAFER",
                    "-dPDFSETTINGS=/prepress", pdf_path
                ], check=True)

                # Replace the original RGB PDF with the CMYK version
                os.remove(pdf_path)  # Delete the RGB version
                os.rename(temp_cmyk_path, pdf_path)  # Rename CMYK as the original file
                print(f"PDF saved in CMYK format as '{pdf_path}'")
            
            else:
                print("Warning: Ghostscript is not installed, so the PDF remains in RGB format.")
                print("To enable CMYK saving, please install Ghostscript:")
                print("- On macOS, use: brew install ghostscript")
                print("- On Ubuntu, use: sudo apt install ghostscript")
                print("- On Windows, download from: https://www.ghostscript.com/download.html")
        else:
            print(f"PDF saved in RGB format as '{pdf_path}'")

    else:
        # Temporary path for the RGB version of the PDF
        temp_pdf_path = pdf_path.replace('.pdf', '_temp.pdf')

        fig.savefig(
            temp_pdf_path, 
            format='pdf', 
            dpi=dpi, 
            bbox_inches=bbox_inches, 
            pad_inches=pad_inches, 
            transparent=True
        )

        if color_mode.upper() == 'CMYK':
            # Check if Ghostscript is installed
            if shutil.which("gs") is not None:
                # Set permissions on the initial RGB PDF to ensure access for Ghostscript
                os.chmod(temp_pdf_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)

                # Run Ghostscript to create the CMYK PDF as a temporary file
                subprocess.run([
                    "gs", "-o", pdf_path,
                    "-sDEVICE=pdfwrite",
                    "-dProcessColorModel=/DeviceCMYK",
                    "-dColorConversionStrategy=/CMYK",
                    "-dNOPAUSE", "-dBATCH", "-dSAFER",
                    "-dPDFSETTINGS=/prepress", temp_pdf_path
                ], check=True)

                # Remove the temporary PDF file
                os.remove(temp_pdf_path)
                print(f"PDF saved in CMYK format as '{pdf_path}'")
            
            else:
                print("Warning: Ghostscript is not installed, so the PDF remains in RGB format.")
                print("To enable CMYK saving, please install Ghostscript:")
                print("- On macOS, use: brew install ghostscript")
                print("- On Ubuntu, use: sudo apt install ghostscript")
                print("- On Windows, download from: https://www.ghostscript.com/download.html")
        else:
            # Rename the temporary file as the final file if no CMYK conversion is needed
            os.rename(temp_pdf_path, pdf_path)
            print(f"PDF saved in RGB format as '{pdf_path}'")


def WaLSA_histo_opt(image, cutoff=1e-3, top_only=False, bot_only=False):
    """
    Clip image values based on the cutoff percentile to enhance contrast.
    Inspired by IDL's "iris_histo_opt" function (Copyright: P.Suetterlin, V.Hansteen, and M. Carlsson)
    
    Parameters:
    - image: 2D array (image data).
    - cutoff: Fraction of values to clip at the top and bottom (default is 0.001).
    - top_only: If True, clip only the highest values.
    - bot_only: If True, clip only the lowest values.
    
    Returns:
    - Clipped image for better contrast.
    """
    # Ignore NaNs in the image
    finite_values = image[np.isfinite(image)]
    
    # Calculate lower and upper bounds based on cutoff percentiles
    lower_bound = np.percentile(finite_values, cutoff * 100)
    upper_bound = np.percentile(finite_values, (1 - cutoff) * 100)
    
    # Clip image according to bounds and options
    if top_only:
        return np.clip(image, None, upper_bound)
    elif bot_only:
        return np.clip(image, lower_bound, None)
    else:
        return np.clip(image, lower_bound, upper_bound)
    