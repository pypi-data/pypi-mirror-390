![TopoCurve Logo](./TC-removebg-preview.png)

# TopoCurve
TopoCurve is a Python library for processing digital elevation models (DEM) stored in GeoTIFF format. This library provides functionalities to extract metadata, calculate principal curvatures and curvature features, as well as plot elevation values. It also includes spectral filtering capabilities for advanced DEM processing.

## Installation

To install TopoCurve, simply clone the repository and install the dependencies listed in `requirements.txt`:

```
git clone https://github.com/username/topo_curve.git
cd topo_curve
pip install -r requirements.txt
```

## Usage

```
from TopoCurve import TopoCurve
from SpectralFiltering import SpectralFiltering

# Instantiate TopoCurve object with a GeoTIFF file
dem = TopoCurve('path/to/your/file.tif')

# Instantiate SpectralFiltering object with a GeoTIFF file
spectral_filter = SpectralFiltering('path/to/your/file.tif')

# Apply FFT filtering
dx, dy, filtered_elevation = spectral_filter.FFT(filter, 'filtertype', alphaIn)

# Calculate principal curvatures and curvature features
K1, K2, KM, KG = dem.CurveCalc(ZFilt, dx, dy, kt)

# Plot and save elevation values
dem.plot(input_array, 'output_image.png')
```

## Example

```
from TopoCurve import TopoCurve
from SpectralFiltering import SpectralFiltering

# Instantiate TopoCurve object with a GeoTIFF file
dem = TopoCurve('references\DEM_files\Purgatory.tif')

# Instantiate SpectralFiltering object with a GeoTIFF file
spectral_filter = SpectralFiltering('references\DEM_files\Purgatory.tif')

# Apply FFT filtering
dx, dy, filtered_elevation = spectral_filter.FFT([190, 200], 'lowpass', 0)

# Calculate principal curvatures and curvature features
K1, K2, KM, KG = dem.CurveCalc(filtered_elevation, dx, dy, 0)

# Plot and save elevation values
dem.plot(filtered_elevation, 'output_image.png')
```

## API Documentation

### TopoCurve Class

#### `TopoCurve(tiff_file)`

Initialize the TopoCurve object with a GeoTIFF file.

- **Parameters:**
  - `tiff_file` (str): Path to the GeoTIFF file.

---

#### `CurveCalc(ZFilt, dx, dy, kt)`

Calculate principal curvatures and curvature features.

- **Parameters:**

  - `ZFilt` (numpy.ndarray): Filtered surface data.
  - `dx` (float): Grid spacing in the x direction.
  - `dy` (float): Grid spacing in the y direction.
  - `kt` (float): Threshold value.

- **Returns:**
  - `K1, K2` (tuple): Principal curvatures.
  - `KM` (tuple): Mean curvature.
  - `KG` (tuple): Gaussian curvature.

---

#### `plot(input, filename)`

Plot the elevation values and save the plot as an image file to reports/figures.

- **Parameters:**
  - `input` (numpy.ndarray): Input elevation values.
  - `filename` (str): Name of the output image file.

---

### Spectral Filtering Class

#### `SpectralFiltering(tiff_file)`

Initialize the SpectralFiltering object with a GeoTIFF file.

- **Parameters:**
  - `tiff_file` (str): Path to the GeoTIFF file.

#### `detrend()`

Detrend the elevation values using least squares plane fitting.

- **Returns:**
  - `Z_detrended` (numpy.ndarray): Detrended elevation values.
  - `plane` (numpy.ndarray): Trend component of the elevation values.

#### `mirror_dem()`

Mirror the elevation values.

- **Returns:**
  - `mirrored_array` (numpy.ndarray): Mirrored elevation values.

#### `tukeyWindow(alphaIn)`

Apply a Tukey window to the elevation values.

- **Arguments:**

  - `alphaIn` (float): Parameter controlling the shape of the Tukey window.

- **Returns:**
  - `tukey_array` (numpy.ndarray): Elevation values after applying the Tukey window.

#### `padding(alphaIn)`

Pad the elevation values.

- **Arguments:**

  - `alphaIn` (float): Parameter controlling the shape of the Tukey window.

- **Returns:**
  - `padded_window_array` (numpy.ndarray): Padded elevation values.

#### `FFT(filter, filterType, alphaIn)`

Apply FFT filtering to the elevation values.

- **Arguments:**

  - `filter` (float): Filter parameter.
  - `filterType` (str): Type of filter ('lowpass' or 'highpass').
  - `alphaIn` (float): Parameter controlling the shape of the Tukey window.

- **Returns:**
  - `dx` (float): Grid spacing in the x direction.
  - `dy` (float): Grid spacing in the y direction.
  - `ZFilt` (numpy.ndarray): Filtered elevation values.

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Project Organization
```
├── LICENSE              
├── Makefile             
├── README.md           
├── TC-removebg-preview.png <- Project logo.

├── docs/                <- Documentation source files for the project:
│   ├── Makefile        
│   ├── commands.rst     
│   ├── conf.py          
│   ├── getting-started.rst 
│   ├── index.rst        
│   └── make.bat        

├── references/          <- Supporting files and research materials:
│   ├── DEM_files/       <- Contains Digital Elevation Model (DEM) test files.
│   ├── paper.md         <- Markdown file with detailed project research or report.
│   └── .gitkeep        

├── reports/             <- Generated analyses and reports:
│   ├── figures/         <- Directory for report graphics and visualizations.
│   └── .gitkeep    

├── requirements.txt     
├── setup.py             
├── src/                 <- Source code for the project:
│   ├── __init__.py      
│   ├── SpectralFiltering.py <- Contains FFT-based spectral filtering methods.
│   ├── TopoCurve.py     <- Core script for curvature calculations and DEM processing.
│   ├── code_play.py     <- Experimental script with templates for further development.
│   └── test.py          <- Unit tests to validate functionality.

├── test_environment.py  
└── tox.ini              
```

## Credits

- **Principal Contributor:** [Sonie Taylor Schermer](https://github.com/tschermer02)
- **Contributions:**  [Joel Nash](https://github.com/jxnash), [Nate Klema](https://github.com/ntklema), [Leif Karlstrom](https://github.com/leifkarlstrom)



<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
```
