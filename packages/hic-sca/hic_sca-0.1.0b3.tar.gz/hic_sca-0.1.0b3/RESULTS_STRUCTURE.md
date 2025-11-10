# HiCSCA Results Dictionary Structure

This document describes the structure of the results dictionary returned by the HiCSCA pipeline.

## Overview

The HiCSCA class stores results in a nested dictionary structure:

```python
hicsca.results[resolution][chr_name] = result_dict
```

Where:
- `resolution`: Resolution in base pairs (e.g., 100000, 50000, etc.)
- `chr_name`: Chromosome name (e.g., "chr1", "chr2", etc.)
- `result_dict`: Dictionary containing analysis results and metadata

## Result Dictionary Fields

Each `result_dict` contains the following fields:

### Core Status Fields

| Field | Type | Description |
|-------|------|-------------|
| `Success` | `bool` | Whether the compartment prediction succeeded |
| `Eig Converged` | `bool` | Whether eigenvalue decomposition converged |

### Compartment Prediction Results

| Field | Type | Description |
|-------|------|-------------|
| `assigned_AB_compartment` | `np.ndarray` | **Main output**: Normalized compartment eigenvector where positive values indicate A compartment, negative values indicate B compartment, and zero indicates excluded loci. Length equals the number of bins at this resolution. |
| `selected_eig_idx` | `int` | Index of the selected eigenvector (1-10) |
| `modified_inter_eigval_score` | `float` | Eigenvector selection score weighted by relative eigenvalue: `inter_AB_score / rel_eigval` |
| `unmodified_inter_AB_score` | `float` | Raw inter-compartment contact score before eigenvalue weighting |

### Eigendecomposition Results

| Field | Type | Description |
|-------|------|-------------|
| `eigvals` | `np.ndarray` | All eigenvalues from decomposition (11 values: trivial eigenvalue + 10 non-trivial) |
| `eigenvects` | `np.ndarray` | All eigenvectors from decomposition (11 x N matrix, where N is number of included bins) stored in row-major format for easier indexing |

### Filtering and Quality Control

| Field | Type | Description |
|-------|------|-------------|
| `cutoff` | `float` | Low-coverage filter cutoff value determined by histogram-based peak detection |
| `include_bool` | `np.ndarray` | Boolean array (length = number of bins) indicating which bins passed the low-coverage filter and were included in eigendecomposition |
| `non_zero_not_included_bool` | `np.ndarray` | Boolean array (length = number of bins) indicating bins with non-zero contacts that were excluded by filtering |
| `deg` | `np.ndarray` | Degree (column sums) of the filtered O/E normalized matrix (length = number of included bins) |
| `OE_normed_diag` | `np.ndarray` | Diagonal elements of the O/E normalized matrix for included bins only (length = number of included bins). Used for A-B orientation selection. |

## Usage Examples

### Accessing Basic Results

```python
from hic_sca import HiCSCA

# Initialize and run pipeline
hicsca = HiCSCA("data/sample.hic", resolutions=[100000])
hicsca.process_all_chromosomes(verbose=True)

# Access results for chr1 at 100kb resolution
result = hicsca.results[100000]["chr1"]

if result['Success']:
    compartments = result['assigned_AB_compartment']
    eig_idx = result['selected_eig_idx']
    score = result['modified_inter_eigval_score']

    print(f"Selected eigenvector {eig_idx} with score {score:.4f}")

    # Identify A and B compartments
    A_bins = compartments > 0
    B_bins = compartments < 0
    excluded_bins = compartments == 0
```

### Understanding Filtering

```python
result = hicsca.results[100000]["chr1"]

# Total number of bins at this resolution
chr_length = hicsca.hic_loader.chr_length_dict["chr1"]
total_bins = int(np.ceil(chr_length / 100000))

# Number of bins that passed filtering
included_bins = result['include_bool'].sum()
excluded_bins = (~result['include_bool']).sum()

# Bins with non-zero contacts that were filtered out
excluded_nonzero_bins = result['non_zero_not_included_bool'].sum()

print(f"Total bins: {total_bins}")
print(f"Included in analysis: {included_bins}")
print(f"Excluded (low coverage): {excluded_bins}")
print(f"Excluded (had contacts but below cutoff): {excluded_nonzero_bins}")
```

### Accessing Eigendecomposition Details

```python
result = hicsca.results[100000]["chr1"]

if result['Success']:
    eigvals = result['eigvals']
    eigvects = result['eigenvects']
    selected_eig = result['selected_eig_idx']

    # Get the selected eigenvector (for included bins only)
    selected_eigvect = eigvects[selected_eig]

    # Eigenvalue spectrum
    print(f"Trivial eigenvalue: {eigvals[0]:.6f}")
    print(f"Selected eigenvalue (Eig{selected_eig}): {eigvals[selected_eig]:.6f}")
    print(f"Eigenvalue gap: {eigvals[1] - eigvals[2]:.6f}")
```

### Reconstructing Full Compartment Vector

```python
result = hicsca.results[100000]["chr1"]

if result['Success']:
    # The assigned_AB_compartment already includes all bins
    # (included bins have compartment values, excluded bins are zero)
    full_compartments = result['assigned_AB_compartment']

    # Verify it matches include_bool
    assert (full_compartments != 0).sum() == result['include_bool'].sum()

    # Get only the non-zero compartment values
    included_idx = np.nonzero(result['include_bool'])[0]
    compartment_values = full_compartments[included_idx]
```

## Multi-Sample/Multi-Resolution Structure

For evaluation modules (`hicsca_eval.py`) that compare multiple datasets or resolutions, results are organized as follows:

### HiCSCA Structure (Single Dataset)
Single dataset, multiple resolutions:
```python
# HiCSCA native structure
results[resolution][chr_name] = result_dict
```

### Cross-Dataset Analysis Structure
Multiple datasets at same resolution(s):
```python
# Multi-dataset structure (dict of HiCSCA results)
dataset_dict[dataset_id] = hicsca_results  # where hicsca_results is results[resolution][chr_name]
# Fully expanded:
dataset_dict[dataset_id][resolution][chr_name] = result_dict
```

Where `dataset_id` is a string identifier for each dataset.

## Field Availability by Success Status

Not all fields are available when processing fails:

### Always Available
- `Success`: Always present
- `Eig Converged`: Always present if eigendecomposition was attempted

### Available on Success
When `Success == True`, all fields are populated.

### Available on Convergence Failure
When `Eig Converged == False`:
- `cutoff`: Available
- `deg`: Available
- All other fields: May not be present

### Available on Eigenvector Selection Failure
When eigendecomposition succeeds but no valid eigenvector is found:
- `Eig Converged`: True
- `Success`: False
- `eigvals`, `eigenvects`: Available
- `cutoff`, `deg`: Available
- Compartment results: Not available

## Notes

1. **Array Lengths**:
   - `assigned_AB_compartment`, `include_bool`, `non_zero_not_included_bool`: Length = total number of bins
   - `eigvects`, `deg`, `OE_normed_diag`: Length = number of included bins

2. **Normalization**:
   - `assigned_AB_compartment` is L2-normalized
   - Eigenvectors in `eigvects` are also normalized

3. **Orientation**:
   - The sign of `assigned_AB_compartment` is set such that bins with higher O/E diagonal values (typically A compartment) have positive values

4. **Memory Considerations**:
   - Large matrices like eigenvectors can consume significant memory
   - Consider deleting results for unused resolutions/chromosomes if memory is limited
