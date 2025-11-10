# HiC-SCA: Hi-C Spectral Compartment Analysis

A Python package for predicting A-B chromosomal compartments from Hi-C (chromosome conformation capture) data using spectral decomposition and observed/expected normalization.

## Overview

HiC-SCA implements a complete pipeline for analyzing Hi-C contact matrices to identify chromatin compartmentalization patterns. It uses spectral decomposition with adaptive tolerance adjustment and an advanced eigenvector selection algorithm to predict A and B chromosomal compartments.

**Key capabilities:**
- Process .hic files at single or multiple resolutions
- Automatic genome-wide O/E normalization with smoothing
- Quality-based eigenvector selection
- Cross-resolution evaluation to identify suitable resolutions
- Multiple output formats (HDF5, Excel, BED, BedGraph, plots)

## Table of Contents

- [Installation](#installation)
  - [Requirements](#requirements)
  - [Install from Source](#install-from-source)
  - [Dependencies](#dependencies)
- [Quick Start](#quick-start)
  - [Command-Line Interface](#command-line-interface)
  - [Python API](#python-api)
- [Command-Line Interface](#command-line-interface-1)
  - [Arguments](#arguments)
  - [Usage Examples](#usage-examples)
  - [Output Files](#output-files)
  - [Troubleshooting CLI](#troubleshooting-cli)
- [Python API](#python-api-1)
  - [Core Classes](#core-classes)
  - [Results Dictionary Structure](#results-dictionary-structure)
  - [Evaluation Tools](#evaluation-tools)
- [Testing](#testing)
- [Other Documentation](#other-documentation)
- [Citation](#citation)
- [License](#license)
- [Contributing](#contributing)
- [Acknowledgments](#acknowledgments)

## Installation

### Requirements

- Python >= 3.10
- pip >= 21.0

### Install from Source

HiC-SCA requires the [h5typer](https://github.com/iQLS-MMS/h5typer) package as a dependency.

```bash
# Clone repositories
git clone https://github.com/iQLS-MMS/h5typer.git
git clone https://github.com/iQLS-MMS/hic-sca.git

# Install h5typer first (required dependency)
cd h5typer
pip install .

# Install HiC-SCA
cd ../hicsca
pip install .

# Or install with test dependencies
pip install ".[tests]"
```

### Dependencies

The package automatically installs:
- hicstraw >= 1.3.0 (reading .hic files)
- numpy >= 1.19.0 (numerical computations)
- scipy >= 1.15.0 (sparse matrices, eigendecomposition)
- h5py >= 3.0.0 (HDF5 I/O)
- pandas >= 1.0.0 (Excel export)
- openpyxl >= 3.0.0 (Excel I/O)
- matplotlib >= 3.0.0 (plotting)
- h5typer >= 0.1.0 (HDF5 type mapping)

## Quick Start

### Command-Line Interface

The easiest way to use HiC-SCA is through the command-line interface:

```bash
# Process single resolution
hic-sca -f hic-sca/tests/test_data/ENCFF216ZNY_Intra_Only.hic -r 100000 -p my_sample

# Process with BED and BedGraph output
hic-sca -f hic-sca/tests/test_data/ENCFF216ZNY_Intra_Only.hic -r 100000 -p my_sample --bed --bedgraph

# Process multiple resolutions
hic-sca -f hic-sca/tests/test_data/ENCFF216ZNY_Intra_Only.hic -r 100000 50000 25000 -p my_sample

# Process all available resolutions with verbose output
hic-sca -f hic-sca/tests/test_data/ENCFF216ZNY_Intra_Only.hic -p my_sample -v

# Specify output directory
hic-sca -f hic-sca/tests/test_data/ENCFF216ZNY_Intra_Only.hic -r 100000 -p my_sample -o results/

# Process specific chromosomes
hic-sca -f hic-sca/tests/test_data/ENCFF216ZNY_Intra_Only.hic -r 100000 -c chr1 chr2 chr3 -p my_sample
```

**Output files:**
- `my_sample_results.h5` - HDF5 file with complete results
- `my_sample_100000bp.xlsx` - Excel file (mandatory)
- `my_sample_100000bp.bed` - BED file (if `--bed` specified)
- `my_sample_100000bp.bedgraph` - BedGraph file (if `--bedgraph` specified)
- `my_sample_chr1_100000bp.png` - Compartment plot for chr1
- `my_sample_cross_resolution_mcc.png` - Cross-resolution MCC heatmap (if multiple resolutions)

### Python API

```python
from hicsca import HiCSCA

# Initialize pipeline with Hi-C file
hicsca = HiCSCA(
    hic_file_path="hic-sca/tests/test_data/ENCFF216ZNY_Intra_Only.hic",
    resolutions=[100000],  # or None for auto-detect all
    chr_names=None  # None = all autosomal chromosomes
)

# Process all chromosomes
hicsca.process_all_chromosomes(verbose=True)

# Access results
result = hicsca.results[100000]['chr1']
if result['Success']:
    compartment = result['assigned_AB_compartment']
    eig_idx = result['selected_eig_idx']
    score = result['modified_inter_eigval_score']
    print(f"chr1: Selected Eig{eig_idx}, Score: {score:.4f}")

# Export results using convenience methods
hicsca.to_bed(100000, "compartments_100kb.bed")
hicsca.to_bedgraph(100000, "compartments_100kb.bedgraph")
hicsca.to_excel(100000, "compartments_100kb.xlsx")
hicsca.to_hdf5("saved_analysis.h5")

# Plot compartments (saves to files)
hicsca.plot_compartments(100000, output_dir="plots", output_prefix="sample")

# Plot cross-resolution MCC correlation
hicsca.plot_cross_resolution_mcc(save_path="cross_res_mcc.png")
```

## Command-Line Interface

### Arguments

**Required (one of):**
- `-f, --hic-file PATH` - Path to input .hic file
- `--load-hdf5 PATH` - Load existing HDF5 results file

**Optional:**
- `-r, --resolutions BP [BP ...]` - Space-separated resolutions in bp (default: auto-detect all)
- `-p, --output-prefix PREFIX` - Prefix for output files (required)
- `-o, --output-dir DIR` - Output directory (default: current directory)
- `-c, --chromosomes CHR [CHR ...]` - Space-separated chromosome names (default: chr1-chr22)
- `-t, --data-type TYPE` - Data type: "observed" or "oe" (default: "observed")
- `-v, --verbose` - Enable verbose output
- `--bed` - Generate BED files for each resolution
- `--bedgraph` - Generate BedGraph files for each resolution

### Usage Examples

```bash
# Basic usage
hic-sca -f data.hic -r 100000 -p my_sample

# With BED and BedGraph output
hic-sca -f data.hic -r 100000 -p my_sample --bed --bedgraph

# Multiple resolutions
hic-sca -f data.hic -r 500000 250000 100000 50000 -p my_sample

# All available resolutions
hic-sca -f data.hic -p my_sample -v

# Custom output directory
hic-sca -f data.hic -r 100000 -p my_sample -o results/

# Specific chromosomes
hic-sca -f data.hic -r 100000 -c chr1 chr2 chr3 -p my_sample

# Use pre-normalized O/E data (skip background normalization)
hic-sca -f data.hic -r 100000 -p my_sample -t oe

# Load existing HDF5 and export to BED/BedGraph
hic-sca --load-hdf5 results.h5 -p output --bed --bedgraph

# Load HDF5 with .hic file (enables processing additional data)
hic-sca --load-hdf5 results.h5 -f data.hic -p output

# Load HDF5 and export filtered data (specific resolutions/chromosomes)
hic-sca --load-hdf5 results.h5 -r 100000 -c chr1 chr2 -p output --bed
```

### Output Files

The CLI generates the following output files:

#### 1. HDF5 Results File (always generated)
**Filename:** `{prefix}_results.h5`

Complete analysis results for all resolutions and chromosomes:
- All compartment predictions
- Pre-computed background normalizations (for fast reloading)
- Eigendecomposition results
- Quality control metrics
- Self-contained: stores chromosome lengths, no .hic file path stored
- Can be loaded with or without .hic file for export or further processing

**Loading HDF5 files:**
```python
from hicsca import HiCSCA

# Load for export only
hicsca = HiCSCA.from_hdf5("results.h5")
hicsca.to_bed(100000, "compartments.bed")

# Load with .hic file to enable processing additional data
hicsca = HiCSCA.from_hdf5("results.h5", hic_file_path="data.hic")
hicsca.process_chromosome("chr1")  # Can process more chromosomes
```

#### 2. Excel Files (always generated)
**Filename:** `{prefix}_{resolution}bp.xlsx`

One file per resolution with:
- **Per-chromosome worksheets** containing:
  - `Start`: Bin start position (1-indexed, in bp)
  - `End`: Bin end position (in bp)
  - `Value`: Compartment eigenvector value
  - `Compartment`: "A" (positive values), "B" (negative values), or "" (excluded bins)
- **Summary worksheet "Inter-AB Scores"** containing:
  - `Chromosome`: Chromosome name
  - `Inter-AB Score`: Quality metric (numeric value or "N/A" if processing failed)
  - `Confidence`: "High Confidence" if 1.75 ≤ score ≤ 3.20, else "Low Confidence"

#### 3. BED Files (optional, with `--bed`)
**Filename:** `{prefix}_{resolution}bp.bed`

BED9 format with RGB colors:
- Consecutive bins of same compartment are merged
- A compartments: red (255,0,0)
- B compartments: blue (0,0,255)
- Zero values (excluded regions) are skipped
- Track header included for genome browser compatibility

**Format:**
```
track name=AB_Compartments_100000bp description="..." itemRgb="On"
chr1    0       300000  A   0   .   0       300000  255,0,0
chr1    400000  800000  B   0   .   400000  800000  0,0,255
```

#### 4. BedGraph Files (optional, with `--bedgraph`)
**Filename:** `{prefix}_{resolution}bp.bedgraph`

Continuous compartment scores for genome browser visualization:
- One value per bin (not merged)
- Zero values (excluded regions) are skipped
- Track header included

**Format:**
```
track type=bedGraph name="AB_Compartments_100000bp"
chr1    0       100000  0.123456
chr1    100000  200000  -0.098765
```

#### 5. Compartment Plots (always generated)
**Filename:** `{prefix}_{chr_name}_{resolution}bp.png`

Publication-quality plots (300 DPI) for each chromosome:
- Red line: A compartment (positive values)
- Blue line: B compartment (negative values)
- Automatic unit scaling (bp, Kbp, Mbp)
- 5 evenly-spaced x-axis ticks

#### 6. Cross-Resolution MCC Plot (if multiple resolutions)
**Filename:** `{prefix}_cross_resolution_mcc.png` and `{prefix}_cross_resolution_mcc_colorbar.png`

Heatmap showing Matthews Correlation Coefficient between resolutions:
- Assesses consistency across different resolutions
- Main heatmap and separate colorbar figure
- Gray cells indicate incompatible resolution pairs (not round multiples)
- Red-white-blue colormap for MCC values (0-1)

### Troubleshooting CLI

**"Error: Must provide either --load-hdf5 or -f/--hic-file"**
- Provide at least one input source: `-f` for new .hic file, or `--load-hdf5` for existing results

**"Error: Hi-C file not found"**
- Verify path to .hic file
- Use absolute paths if relative paths cause issues

**"Error: HDF5 file not found"**
- Verify path to HDF5 results file
- Ensure correct file name with `.h5` extension

**"No resolutions available"**
- Check that .hic file contains data at specified resolutions
- Use auto-detection (omit `-r` flag) to see available resolutions

**Memory errors**
- Process fewer resolutions at once
- Use higher resolutions (e.g., 100kb instead of 10kb)
- Close other applications to free up RAM

## Python API

### Core Classes

#### HiCSCA - Main Pipeline Class

Complete pipeline for A-B compartment prediction from Hi-C data.

**Initialization:**
```python
from hicsca import HiCSCA

hicsca = HiCSCA(
    hic_file_path="data/sample.hic",
    chr_names=None,  # None = all autosomal chromosomes (chr1-chr22)
    resolutions=None,  # None = all available resolutions
    data_type="observed",  # "observed" or "oe"
    norm_type="NONE",
    smoothing_cutoff=400
)
```

**Parameters:**
- `hic_file_path` (str): Path to .hic file
- `chr_names` (list or None): Chromosome names to process (default: all autosomal)
- `resolutions` (list or None): Resolutions in bp (default: auto-detect all)
- `data_type` (str): "observed" (raw contacts with O/E normalization) or "oe" (pre-normalized, skip O/E)
- `norm_type` (str): Normalization type for hicstraw (default: "NONE")
- `smoothing_cutoff` (int): Smoothing parameter for O/E normalization (default: 400, only used when data_type="observed")

**Key Methods:**
```python
# Compute background normalization (automatic when processing, can be called explicitly)
hicsca.compute_background_normalization(resolutions=None)

# Process single chromosome at specified resolutions
hicsca.process_chromosome(chr_name, resolutions=None, verbose=True)

# Process all chromosomes at specified resolutions
hicsca.process_all_chromosomes(resolutions=None, verbose=True)

# Load saved HiCSCA instance
hicsca = HiCSCA.from_hdf5(hdf5_path, hic_file_path=None)
```

**Export Methods:**
```python
# Save complete instance to HDF5
hicsca.to_hdf5(output_path, update=False)

# Generate BED file
hicsca.to_bed(resolution, output_path, chr_names=None, dataset_id=None)

# Generate BedGraph file
hicsca.to_bedgraph(resolution, output_path, chr_names=None, dataset_id=None, track_name=None)

# Generate Excel file
hicsca.to_excel(resolution, output_path, chr_names=None, dataset_id=None)

# Plot compartments (saves to files and/or displays in Jupyter)
hicsca.plot_compartments(
    resolution,
    chr_names=None,
    output_dir=None,  # Specify to save files
    output_prefix=None,
    display=True,  # Set False to disable Jupyter display
    dpi=300,
    figsize=(3.595, 2)
)

# Plot cross-resolution MCC correlation heatmap
hicsca.plot_cross_resolution_mcc(
    chr_name='all',  # 'all' or specific chromosome
    resolutions=None,  # None = all resolutions
    chr_names=None,  # For genome-wide ('all') calculation
    figsize=(2.8, 2.8),
    dpi=300,
    background_alpha=1,  # 0=transparent, 1=opaque
    plot_colorbar=True,  # Generate separate colorbar figure
    save_path=None  # Path to save main figure
)
```

**Usage:**
```python
# Example 1: Using observed data (default - with O/E normalization)
hicsca = HiCSCA(
    "data/sample.hic",
    resolutions=[100000, 50000],
    data_type="observed",
    norm_type="NONE"
)

# Process all chromosomes (results stored in hicsca.results)
hicsca.process_all_chromosomes(verbose=True)

# Access results
result = hicsca.results[100000]["chr1"]
if result['Success']:
    compartment = result['assigned_AB_compartment']
    eig_idx = result['selected_eig_idx']
    score = result['modified_inter_eigval_score']

# Export results
hicsca.to_bed(100000, "compartments_100kb.bed")
hicsca.to_excel(100000, "compartments_100kb.xlsx")
hicsca.to_hdf5("saved_analysis.h5")

# Example 2: Using pre-normalized O/E data (skips background normalization)
hicsca_oe = HiCSCA(
    "data/sample.hic",
    resolutions=[100000],
    data_type="oe",  # Data already O/E normalized
    norm_type="KR"   # Can use normalized data if available
)
hicsca_oe.process_all_chromosomes(verbose=True)

# Example 3: Load previously saved HiCSCA instance
hicsca_loaded = HiCSCA.from_hdf5("saved_analysis.h5")
# All results and normalizations already loaded - no processing needed
result = hicsca_loaded.results[100000]['chr1']
```

### Results Dictionary Structure

Results are stored in: `hicsca.results[resolution][chr_name]`

Each result dictionary contains:

**Core Fields (always present):**
- `Success` (bool): Whether processing succeeded
- `Eig Converged` (bool): Whether eigendecomposition converged

**Compartment Prediction (when Success=True):**
- `assigned_AB_compartment` (ndarray): Normalized compartment eigenvector (positive=A, negative=B, zero=excluded)
- `selected_eig_idx` (int): Index of selected eigenvector (1-10)
- `modified_inter_eigval_score` (float): Eigenvalue-weighted eigenvector selection score
- `unmodified_inter_AB_score` (float): Raw inter-compartment contact score

**Eigendecomposition Results:**
- `eigvals` (ndarray): All eigenvalues (11 values: trivial + 10 non-trivial)
- `eigenvects` (ndarray): All eigenvectors (11 × N matrix, row-major format)

**Quality Control:**
- `cutoff` (float): Low-coverage filter cutoff value
- `include_bool` (ndarray): Boolean array indicating bins included in analysis
- `non_zero_not_included_bool` (ndarray): Boolean array for excluded non-zero bins
- `deg` (ndarray): Degree (column sums) of filtered O/E matrix
- `OE_normed_diag` (ndarray): Diagonal of O/E matrix for included bins

**See RESULTS_STRUCTURE.md for complete documentation.**

### Evaluation Tools

#### CrossResolutionAnalyzer

Analyzes agreement between different resolutions within the same Hi-C dataset.

```python
from hicsca.evals import CrossResolutionAnalyzer

# Initialize with HiCSCA results (auto-detects resolutions and chromosomes)
analyzer = CrossResolutionAnalyzer(hicsca.results)

# Or specify custom resolutions/chromosomes
analyzer = CrossResolutionAnalyzer(
    hicsca.results,
    resolutions=[500000, 250000, 100000, 50000],
    chr_names=['chr1', 'chr2', ..., 'chr22']
)

# Analyze (results stored internally, cached)
analyzer.analyze()

# Plot genome-wide cross-resolution MCC with colorbar
fig, ax, cbar_fig, cbar_ax = analyzer.plot_cross_resolution_mcc()

# Plot specific chromosome with transparent background
fig, ax, cbar_fig, cbar_ax = analyzer.plot_cross_resolution_mcc(
    chr_name='chr1',
    save_path='chr1_mcc.png',
    background_alpha=0
)
# Saves: chr1_mcc.png and chr1_mcc_colorbar.png

# Access MCC matrices directly
genome_wide_mcc = analyzer.mcc_matrices['all']
chr1_mcc = analyzer.mcc_matrices['chr1']
```

#### CrossDatasetAnalyzer

Analyzes agreement between different Hi-C datasets at the same resolution(s).

```python
from hicsca.evals import CrossDatasetAnalyzer

# Create dataset dictionary (dataset_id -> HiCSCA results)
dataset_dict = {
    'dataset1': hicsca_inst1.results,
    'dataset2': hicsca_inst2.results,
    'dataset3': hicsca_inst3.results
}

# Initialize (auto-detects resolutions, dataset_ids, and chromosomes)
analyzer = CrossDatasetAnalyzer(dataset_dict)

# Analyze all resolutions
analyzer.analyze()

# Plot genome-wide MCC correlation at 100kb with colorbar
fig1, ax1, cbar_fig1, cbar_ax1 = analyzer.plot_mcc_correlation(
    100000,
    tick_labels=['A', 'B', 'C'],
    save_path='mcc_100kb.png'
)
# Saves: mcc_100kb.png and mcc_100kb_colorbar.png

# Plot chr1 orientation agreement
fig2, ax2, cbar_fig2, cbar_ax2 = analyzer.plot_orientation_agreement(
    100000,
    chr_name='chr1',
    save_path='orient_chr1_100kb.png'
)

# Access matrices directly
mcc_genome_wide = analyzer.mcc_matrices[100000]['all']
```

#### MCCCalculator

Compute Matthews Correlation Coefficient between compartment predictions.

```python
from hicsca.evals import MCCCalculator

mcc, tp, fp, tn, fn, zeroed, reversed = MCCCalculator.compute_AB_MCC(
    reference_compartments,
    predicted_compartments,
    auto_flip=True  # Automatically handle orientation
)

print(f"MCC: {mcc:.4f}")
```

## Testing

The package includes a comprehensive test suite:

```bash
# Run all tests (including regression tests)
pytest tests/

# Run with coverage
pytest tests/ --cov=hicsca --cov-report=html

# Specific test classes
pytest tests/test_hicsca.py::TestResultStructure
pytest tests/test_hicsca.py::TestRegressionComparison
```

**Test Coverage:**
- Data availability checks
- Result structure validation
- Regression tests (compartment vectors, scores, eigenvalues)
- Cross-resolution analysis validation

**Note**: Regression tests require test data files in `tests/test_data/` (ENCFF216ZNY_Intra_Only.hic and reference.h5).

### Test Data
The test .hic dataset contains only the intra-chromosomal contacts of [ENCFF216ZNY](https://www.encodeproject.org/files/ENCFF216ZNY/). The file is located at [tests/test_data/ENCFF216ZNY_Intra_Only.hic](./tests/test_data/ENCFF216ZNY_Intra_Only.hic)

## Other Documentation

- **RESULTS_STRUCTURE.md**: Complete documentation of results dictionary structure

## Citation

If you use this software in your research, please cite:

Chan, J. & Kono, H. HiC-SCA: A Spectral Clustering Method for Reliable A/B Compartment Assignment From Hi-C Data. Preprint at https://doi.org/10.1101/2025.09.22.677711 (2025).

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

This package uses:
- [hicstraw](https://github.com/aidenlab/straw) for reading .hic files
- NumPy and SciPy for numerical computations and sparse matrix operations
- matplotlib for visualization
- h5py for HDF5 file I/O
- h5typer for automatic HDF5 type mapping
- LOBPCG algorithm (SciPy) for efficient eigenvalue decomposition
