"""
HiC-SCA Formats Module

Handles generation of output files for HiC-SCA analysis results:
- BED format files for genome browsers
- HDF5 files for data persistence and sharing
- BedGraph format (optional)
- Excel export
- A-B compartment plots for visualization
"""

import numpy as np
from typing import Dict, List, Optional, TYPE_CHECKING, Tuple
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import h5typer

# Use TYPE_CHECKING to avoid circular imports while keeping type hints
if TYPE_CHECKING:
    from .hicsca import HiCSCA


def generate_bed_file(resolution: int,
                     output_path: str,
                     hicsca_inst=None,
                     results_dict: Optional[Dict] = None,
                     chr_names: Optional[List[str]] = None,
                     chr_length_dict: Optional[Dict[str, int]] = None,
                     dataset_id: Optional[str] = None) -> None:
    """
    Generate a BED file containing A-B compartment predictions.

    Consecutive bins of the same compartment type (A or B) are merged into
    single regions. Bins with zero values (excluded/uncertain regions) are
    skipped. Output uses BED9 format with RGB colors: A compartments (red),
    B compartments (blue).

    Parameters
    ----------
    resolution : int
        Resolution in base pairs
    output_path : str
        Path to output BED file
    hicsca_inst : HiCSCA, optional
        HiCSCA instance. If provided, results_dict, chr_names, and chr_length_dict
        will be extracted from this instance (unless explicitly provided as parameters).
    results_dict : Dict, optional
        HiCSCA results dictionary with structure:
        - results_dict[resolution][chr_name] if dataset_id is None
        - results_dict[dataset_id][resolution][chr_name] if dataset_id is provided
        If not provided, will be extracted from hicsca_inst.
    chr_names : List[str], optional
        List of chromosome names to include. If not provided, will be extracted from hicsca_inst.
    chr_length_dict : Dict[str, int], optional
        Dictionary mapping chromosome names to their lengths in base pairs.
        If not provided, will be extracted from hicsca_inst.chr_length_dict.
    dataset_id : str, optional
        Dataset identifier (required if results_dict uses dataset_id structure)

    Raises
    ------
    ValueError
        If hicsca_inst is not provided and any of results_dict, chr_names, or chr_length_dict
        are missing, or if no results are available for the specified resolution

    Notes
    -----
    BED9 format: chr start end name score strand thickStart thickEnd itemRgb
    - A compartments: itemRgb = "255,0,0" (red)
    - B compartments: itemRgb = "0,0,255" (blue)

    Examples
    --------
    >>> # Using HiCSCA instance (simplest)
    >>> generate_bed_file(100000, "output.bed", hicsca_inst=hicsca_inst)
    >>>
    >>> # Using HiCSCA instance with chromosome override
    >>> generate_bed_file(100000, "output.bed", hicsca_inst=hicsca_inst, chr_names=['chr1', 'chr2'])
    >>>
    >>> # Without HiCSCA instance (manual parameters)
    >>> generate_bed_file(100000, "output.bed",
    ...                  results_dict=results, chr_names=chrs, chr_length_dict=lengths)
    """
    # Extract parameters from HiCSCA instance if provided
    if hicsca_inst is not None:
        if results_dict is None:
            results_dict = hicsca_inst.results
        if chr_names is None:
            chr_names = hicsca_inst.chr_names
        if chr_length_dict is None:
            chr_length_dict = hicsca_inst.chr_length_dict
    else:
        # If no HiCSCA instance, require all parameters
        if results_dict is None or chr_names is None or chr_length_dict is None:
            raise ValueError(
                "If hicsca_inst is not provided, results_dict, chr_names, and "
                "chr_length_dict must all be provided"
            )
    # Check if any results exist for this resolution
    has_results = False

    for chr_name in chr_names:
        if dataset_id is None:
            # HiCSCA structure: results[resolution][chr_name]
            if resolution in results_dict and chr_name in results_dict[resolution]:
                has_results = True
                break
        else:
            # Multi-dataset structure: results[dataset_id][resolution][chr_name]
            if dataset_id in results_dict and resolution in results_dict[dataset_id]:
                if chr_name in results_dict[dataset_id][resolution]:
                    has_results = True
                    break

    if not has_results:
        raise ValueError(
            f"No results available for resolution: {resolution} bp."
        )

    with open(output_path, 'w') as f:
        # Write BED header with itemRgb enabled for colors
        header = f"track name=AB_Compartments_{resolution}bp "
        header += f"description=\"A-B Compartment Predictions at {resolution}bp resolution"
        if dataset_id:
            header += f" for dataset {dataset_id}"
        header += f"\" itemRgb=\"On\"\n"
        f.write(header)

        for chr_name in chr_names:
            # Get result for this chromosome
            if dataset_id is None:
                if resolution not in results_dict or chr_name not in results_dict[resolution]:
                    continue
                result = results_dict[resolution][chr_name]
            else:
                if (dataset_id not in results_dict or
                    resolution not in results_dict[dataset_id] or
                    chr_name not in results_dict[dataset_id][resolution]):
                    continue
                result = results_dict[dataset_id][resolution][chr_name]

            # Skip if processing failed
            if not result.get('Success', False):
                continue

            compartment_values = result['assigned_AB_compartment']
            chr_length = chr_length_dict[chr_name]
            num_bins = int(np.ceil(chr_length / resolution))

            # Merge consecutive bins of same compartment and write as regions
            current_compartment = None  # 'A' or 'B'
            region_start = None

            for bin_idx in range(num_bins):
                value = compartment_values[bin_idx]

                # Skip zero values (excluded/uncertain regions)
                if value == 0:
                    # Write any open region before skipping
                    if current_compartment is not None:
                        region_end = bin_idx * resolution
                        # BED9 format: chr start end name score strand thickStart thickEnd itemRgb
                        color = "255,0,0" if current_compartment == 'A' else "0,0,255"
                        f.write(f"{chr_name}\t{region_start}\t{region_end}\t"
                               f"{current_compartment}\t0\t.\t{region_start}\t{region_end}\t{color}\n")
                        current_compartment = None
                        region_start = None
                    continue

                # Determine compartment type
                compartment_type = 'A' if value > 0 else 'B'

                if current_compartment == compartment_type:
                    # Continue extending current region
                    continue
                else:
                    # Write previous region if it exists
                    if current_compartment is not None:
                        region_end = bin_idx * resolution
                        color = "255,0,0" if current_compartment == 'A' else "0,0,255"
                        f.write(f"{chr_name}\t{region_start}\t{region_end}\t"
                               f"{current_compartment}\t0\t.\t{region_start}\t{region_end}\t{color}\n")

                    # Start new region
                    current_compartment = compartment_type
                    region_start = bin_idx * resolution

            # Write final region if it exists
            if current_compartment is not None:
                region_end = min(num_bins * resolution, chr_length)
                color = "255,0,0" if current_compartment == 'A' else "0,0,255"
                f.write(f"{chr_name}\t{region_start}\t{region_end}\t"
                       f"{current_compartment}\t0\t.\t{region_start}\t{region_end}\t{color}\n")


def save_to_hdf5(hicsca_inst,
                output_path: str,
                update: bool = False) -> None:
    """
    Save complete HiCSCA instance to HDF5 file.

    Saves all results, background normalizations, and metadata needed to
    reconstruct the HiCSCA instance later using HiCSCA.from_hdf5().

    Parameters
    ----------
    hicsca_inst : HiCSCA
        HiCSCA instance to save
    output_path : str
        Path to output HDF5 file
    update : bool, optional
        If True, update existing file; if False, overwrite (default: False)

    Raises
    ------
    RuntimeError
        If hicsca_inst has no .hic file

    Examples
    --------
    >>> from hicsca import HiCSCA
    >>> from hicsca_formats import save_to_hdf5
    >>>
    >>> # Process data
    >>> hicsca_inst = HiCSCA("data.hic", resolutions=[100000])
    >>> hicsca_inst.process_all_chromosomes()
    >>>
    >>> # Save complete instance
    >>> save_to_hdf5(hicsca_inst, "output.h5")
    """
    # Check if hic_loader is available
    if hicsca_inst.hic_loader is None:
        raise RuntimeError(
            "Cannot save to HDF5: No .hic file available."
        )

    # Lazy import to avoid circular dependency
    from .hicsca import _serialize_background_normalizer

    # Create save dictionary with all components
    save_dict = {
        'results': hicsca_inst.results,
        'metadata': {
            'chr_names': hicsca_inst.chr_names,
            'resolutions': hicsca_inst.resolutions,
            'data_type': hicsca_inst.data_type,
            'norm_type': hicsca_inst.norm_type,
            'smoothing_cutoff': hicsca_inst.smoothing_cutoff,
            'chr_length_dict': hicsca_inst.chr_length_dict
        }
    }

    # Serialize normalizers if they exist
    if hicsca_inst.normalizers:
        serialized_normalizers = {}
        for resolution, normalizer in hicsca_inst.normalizers.items():
            serialized_normalizers[resolution] = _serialize_background_normalizer(normalizer)
        save_dict['normalizers'] = serialized_normalizers
    else:
        save_dict['normalizers'] = None

    h5typer.save_data(output_path, save_dict, update=update)


def from_hdf5(hdf5_path: str, hic_file_path: Optional[str] = None):
    """
    Load HiCSCA instance from HDF5 file.

    This is a convenience wrapper around HiCSCA.from_hdf5() for loading
    previously saved HiCSCA instances.

    Parameters
    ----------
    hdf5_path : str
        Path to saved HDF5 file (e.g., "output.h5")
    hic_file_path : str, optional
        Path to the original .hic file. If None, uses the path saved in the HDF5 file.
        Required if the .hic file was moved since saving.

    Returns
    -------
    HiCSCA
        Reconstructed HiCSCA instance with all results and normalizers loaded

    Examples
    --------
    >>> from hicsca_formats import from_hdf5
    >>>
    >>> # Load using saved .hic path
    >>> hicsca_inst = from_hdf5("output.h5")
    >>>
    >>> # Load with new .hic path (if file was moved)
    >>> hicsca_inst = from_hdf5("output.h5", hic_file_path="new/path/data.hic")
    >>>
    >>> # Access results
    >>> result = hicsca_inst.results[100000]['chr1']
    """
    # Lazy import to avoid circular dependency
    from .hicsca import HiCSCA

    return HiCSCA.from_hdf5(hdf5_path, hic_file_path)


def generate_bedgraph_file(resolution: int,
                           output_path: str,
                           hicsca_inst=None,
                           results_dict: Optional[Dict] = None,
                           chr_names: Optional[List[str]] = None,
                           chr_length_dict: Optional[Dict[str, int]] = None,
                           dataset_id: Optional[str] = None,
                           track_name: Optional[str] = None) -> None:
    """
    Generate a BedGraph file containing compartment scores.

    BedGraph format is more compact than BED and better suited for continuous-valued data.
    Bins with zero values (excluded/uncertain regions) are skipped.

    Parameters
    ----------
    resolution : int
        Resolution in base pairs
    output_path : str
        Path to output BedGraph file
    hicsca_inst : HiCSCA, optional
        HiCSCA instance. If provided, results_dict, chr_names, and chr_length_dict
        will be extracted from this instance (unless explicitly provided as parameters).
    results_dict : Dict, optional
        HiCSCA results dictionary with structure:
        - results_dict[resolution][chr_name] if dataset_id is None
        - results_dict[dataset_id][resolution][chr_name] if dataset_id is provided
        If not provided, will be extracted from hicsca_inst.
    chr_names : List[str], optional
        List of chromosome names to include. If not provided, will be extracted from hicsca_inst.
    chr_length_dict : Dict[str, int], optional
        Dictionary mapping chromosome names to their lengths in base pairs.
        If not provided, will be extracted from hicsca_inst.chr_length_dict.
    dataset_id : str, optional
        Dataset identifier (required if results_dict uses dataset_id structure)
    track_name : str, optional
        Custom track name for genome browser

    Raises
    ------
    ValueError
        If hicsca_inst is not provided and any of results_dict, chr_names, or chr_length_dict
        are missing, or if no results are available for the specified resolution

    Examples
    --------
    >>> # Using HiCSCA instance (simplest)
    >>> generate_bedgraph_file(100000, "output.bedgraph", hicsca_inst=hicsca_inst)
    >>>
    >>> # Using HiCSCA instance with custom track name
    >>> generate_bedgraph_file(100000, "output.bedgraph", hicsca_inst=hicsca_inst,
    ...                        track_name="MyCompartments")
    >>>
    >>> # Without HiCSCA instance (manual parameters)
    >>> generate_bedgraph_file(100000, "output.bedgraph",
    ...                        results_dict=results, chr_names=chrs, chr_length_dict=lengths)
    """
    # Extract parameters from HiCSCA instance if provided
    if hicsca_inst is not None:
        if results_dict is None:
            results_dict = hicsca_inst.results
        if chr_names is None:
            chr_names = hicsca_inst.chr_names
        if chr_length_dict is None:
            chr_length_dict = hicsca_inst.chr_length_dict
    else:
        # If no HiCSCA instance, require all parameters
        if results_dict is None or chr_names is None or chr_length_dict is None:
            raise ValueError(
                "If hicsca_inst is not provided, results_dict, chr_names, and "
                "chr_length_dict must all be provided"
            )
    # Check if any results exist for this resolution
    has_results = False

    for chr_name in chr_names:
        if dataset_id is None:
            if resolution in results_dict and chr_name in results_dict[resolution]:
                has_results = True
                break
        else:
            if dataset_id in results_dict and resolution in results_dict[dataset_id]:
                if chr_name in results_dict[dataset_id][resolution]:
                    has_results = True
                    break

    if not has_results:
        raise ValueError(
            f"No results available for resolution {resolution}. "
            "Ensure the data has been processed first."
        )

    with open(output_path, 'w') as f:
        # Write BedGraph header
        if track_name is None:
            track_name = f"AB_Compartments_{resolution}bp"
            if dataset_id:
                track_name += f"_{dataset_id}"

        f.write(f"track type=bedGraph name=\"{track_name}\" "
               f"description=\"A-B Compartment Scores at {resolution}bp resolution\" "
               f"visibility=full autoScale=on\n")

        for chr_name in chr_names:
            # Get result for this chromosome
            if dataset_id is None:
                if resolution not in results_dict or chr_name not in results_dict[resolution]:
                    continue
                result = results_dict[resolution][chr_name]
            else:
                if (dataset_id not in results_dict or
                    resolution not in results_dict[dataset_id] or
                    chr_name not in results_dict[dataset_id][resolution]):
                    continue
                result = results_dict[dataset_id][resolution][chr_name]

            # Skip if processing failed
            if not result.get('Success', False):
                continue

            compartment_values = result['assigned_AB_compartment']
            chr_length = chr_length_dict[chr_name]
            num_bins = int(np.ceil(chr_length / resolution))

            # Write each bin, skipping zero values (excluded/uncertain regions)
            for bin_idx in range(num_bins):
                start = bin_idx * resolution
                end = min((bin_idx + 1) * resolution, chr_length)
                value = compartment_values[bin_idx]

                # Skip zero values
                if value == 0:
                    continue

                # BedGraph format: chr start end value
                f.write(f"{chr_name}\t{start}\t{end}\t{value:.6f}\n")


def export_compartments_to_dict(results_dict: Dict,
                                chr_names: List[str],
                                resolution: int,
                                dataset_id: Optional[str] = None) -> Dict[str, np.ndarray]:
    """
    Export compartment predictions to a simple dictionary format.

    Useful for downstream analysis or integration with other tools.

    Parameters
    ----------
    results_dict : Dict
        HiCSCA results dictionary
    chr_names : List[str]
        List of chromosome names to extract
    resolution : int
        Resolution in base pairs
    dataset_id : str, optional
        Dataset identifier if using multi-dataset structure

    Returns
    -------
    Dict[str, np.ndarray]
        Dictionary mapping chromosome names to compartment arrays
        Only includes successfully processed chromosomes

    Examples
    --------
    >>> compartments = export_compartments_to_dict(
    ...     hicsca.results, ['chr1', 'chr2'], 100000
    ... )
    >>> chr1_compartments = compartments['chr1']
    """
    exported = {}

    for chr_name in chr_names:
        # Get result for this chromosome
        if dataset_id is None:
            if resolution not in results_dict or chr_name not in results_dict[resolution]:
                continue
            result = results_dict[resolution][chr_name]
        else:
            if (dataset_id not in results_dict or
                resolution not in results_dict[dataset_id] or
                chr_name not in results_dict[dataset_id][resolution]):
                continue
            result = results_dict[dataset_id][resolution][chr_name]

        # Only export successful results
        if result.get('Success', False):
            exported[chr_name] = result['assigned_AB_compartment'].copy()

    return exported


def generate_excel_file(resolution: int,
                        output_path: str,
                        hicsca_inst=None,
                        results_dict: Optional[Dict] = None,
                        chr_names: Optional[List[str]] = None,
                        chr_length_dict: Optional[Dict[str, int]] = None,
                        dataset_id: Optional[str] = None) -> None:
    """
    Generate an Excel file containing A-B compartment predictions.

    Each chromosome is written to a separate worksheet with columns for bin positions
    (1-indexed), compartment values, and A/B assignments.

    Parameters
    ----------
    resolution : int
        Resolution in base pairs
    output_path : str
        Path to output Excel file (.xlsx)
    hicsca_inst : HiCSCA, optional
        HiCSCA instance. If provided, results_dict, chr_names, and chr_length_dict
        will be extracted from this instance (unless explicitly provided as parameters).
    results_dict : Dict, optional
        HiCSCA results dictionary with structure:
        - results_dict[resolution][chr_name] if dataset_id is None
        - results_dict[dataset_id][resolution][chr_name] if dataset_id is provided
        If not provided, will be extracted from hicsca_inst.
    chr_names : List[str], optional
        List of chromosome names to include. If not provided, will be extracted from hicsca_inst.
    chr_length_dict : Dict[str, int], optional
        Dictionary mapping chromosome names to their lengths in base pairs.
        If not provided, will be extracted from hicsca_inst.chr_length_dict.
    dataset_id : str, optional
        Dataset identifier (required if results_dict uses dataset_id structure)

    Raises
    ------
    ValueError
        If hicsca_inst is not provided and any of results_dict, chr_names, or chr_length_dict
        are missing, or if no results are available for the specified resolution

    Notes
    -----
    Excel format:
    - Each chromosome is a separate worksheet with columns:
      - Start (1-indexed), End, Value, Compartment
      - Compartment: "A" for positive values, "B" for negative values, "" for zeros
    - Summary sheet "Inter-AB Scores" with columns:
      - Chromosome, Inter-AB Score, Confidence
      - Inter-AB Score: Numeric value or "N/A" if processing failed
      - Confidence: "High Confidence" if 1.75 ≤ score ≤ 3.20, else "Low Confidence"

    Examples
    --------
    >>> # Using HiCSCA instance (simplest)
    >>> generate_excel_file(100000, "compartments_100kb.xlsx", hicsca_inst=hicsca_inst)
    >>>
    >>> # Using HiCSCA instance with specific chromosomes
    >>> generate_excel_file(100000, "compartments_chr1_2.xlsx", hicsca_inst=hicsca_inst,
    ...                    chr_names=['chr1', 'chr2'])
    >>>
    >>> # Without HiCSCA instance (manual parameters)
    >>> generate_excel_file(100000, "compartments.xlsx",
    ...                    results_dict=results, chr_names=chrs, chr_length_dict=lengths)
    """
    # Extract parameters from HiCSCA instance if provided
    if hicsca_inst is not None:
        if results_dict is None:
            results_dict = hicsca_inst.results
        if chr_names is None:
            chr_names = hicsca_inst.chr_names
        if chr_length_dict is None:
            chr_length_dict = hicsca_inst.chr_length_dict
    else:
        # If no HiCSCA instance, require all parameters
        if results_dict is None or chr_names is None or chr_length_dict is None:
            raise ValueError(
                "If hicsca_inst is not provided, results_dict, chr_names, and "
                "chr_length_dict must all be provided"
            )

    # Check if any results exist for this resolution
    has_results = False

    for chr_name in chr_names:
        if dataset_id is None:
            # HiCSCA structure: results[resolution][chr_name]
            if resolution in results_dict and chr_name in results_dict[resolution]:
                has_results = True
                break
        else:
            # Multi-dataset structure: results[dataset_id][resolution][chr_name]
            if dataset_id in results_dict and resolution in results_dict[dataset_id]:
                if chr_name in results_dict[dataset_id][resolution]:
                    has_results = True
                    break

    if not has_results:
        raise ValueError(
            f"No results available for resolution: {resolution} bp."
        )

    # Create Excel writer
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Lists for summary sheet
        summary_chr_names = []
        summary_scores = []
        summary_confidence = []

        for chr_name in chr_names:
            # Get result for this chromosome
            result = None
            if dataset_id is None:
                if resolution in results_dict and chr_name in results_dict[resolution]:
                    result = results_dict[resolution][chr_name]
            else:
                if (dataset_id in results_dict and
                    resolution in results_dict[dataset_id] and
                    chr_name in results_dict[dataset_id][resolution]):
                    result = results_dict[dataset_id][resolution][chr_name]

            # Collect data for summary sheet (for all chromosomes)
            summary_chr_names.append(chr_name)
            if result is not None and result.get('Success', False):
                score = result['unmodified_inter_AB_score']
                summary_scores.append(score)

                # Classify confidence based on score range
                if 1.75 <= score <= 3.20:
                    summary_confidence.append('High')
                else:
                    summary_confidence.append('Low')
            else:
                summary_scores.append('N/A')
                summary_confidence.append('N/A')

            # Skip compartment sheet if result is missing or processing failed
            if result is None or not result.get('Success', False):
                continue

            # Create summary sheet with Inter-AB scores and confidence classification
            if summary_chr_names:  # Only if we have data
                summary_df = pd.DataFrame({
                    'Chromosome': summary_chr_names,
                    'Inter-AB Score': summary_scores,
                    'Confidence': summary_confidence
                })
                summary_df.to_excel(writer, sheet_name='Inter-AB Scores', index=False)

            compartment_values = result['assigned_AB_compartment']
            chr_length = chr_length_dict[chr_name]
            num_bins = int(np.ceil(chr_length / resolution))

            # Create data for DataFrame
            starts = []
            ends = []
            values = []
            compartments = []

            for bin_idx in range(num_bins):
                # Calculate 1-indexed positions
                start = bin_idx * resolution + 1
                end = min((bin_idx + 1) * resolution, chr_length)
                value = compartment_values[bin_idx]

                # Determine compartment label
                if value > 0:
                    compartment = 'A'
                elif value < 0:
                    compartment = 'B'
                else:
                    compartment = ''  # Excluded/uncertain bins

                starts.append(start)
                ends.append(end)
                values.append(value)
                compartments.append(compartment)

            # Create DataFrame
            df = pd.DataFrame({
                'Start': starts,
                'End': ends,
                'Value': values,
                'Compartment': compartments
            })

            # Write to Excel sheet (sheet name is chromosome name)
            df.to_excel(writer, sheet_name=chr_name, index=False)


def plot_AB_compartment(assigned_AB_compartment: np.ndarray,
                        output_path: Optional[str] = None,
                        chr_name: Optional[str] = None,
                        resolution: Optional[int] = None,
                        dpi: int = 300,
                        figsize: Tuple[float, float] = (3.595, 2),
                        show_legend: bool = True) -> Tuple[plt.Figure, plt.Axes]:
    """
    Plot A-B compartment predictions for a single chromosome.

    Creates a line plot showing A compartment (positive values, red) and
    B compartment (negative values, blue) along the chromosome.

    Parameters
    ----------
    assigned_AB_compartment : np.ndarray
        Compartment prediction array where positive values indicate A compartment,
        negative values indicate B compartment, and zero indicates excluded loci
    output_path : str, optional
        Path to save the output figure. If None, figure is not saved (default: None)
    chr_name : str, optional
        Chromosome name for labeling (e.g., "chr1")
    resolution : int, optional
        Resolution in base pairs for labeling
    dpi : int, optional
        Figure DPI (default: 300)
    figsize : tuple, optional
        Figure size in inches (default: (3.595, 2))
    show_legend : bool, optional
        Whether to display legend for A and B compartments (default: True)

    Returns
    -------
    Tuple[plt.Figure, plt.Axes]
        (fig, ax) - matplotlib Figure and Axes objects

    Examples
    --------
    >>> # Save to file
    >>> result = hicsca.results[100000]['chr1']
    >>> fig, ax = plot_AB_compartment(
    ...     result['assigned_AB_compartment'],
    ...     'chr1_compartments.png',
    ...     chr_name='chr1',
    ...     resolution=100000
    ... )
    >>> plt.close(fig)  # Close to prevent display
    >>>
    >>> # Display in Jupyter without saving
    >>> fig, ax = plot_AB_compartment(
    ...     result['assigned_AB_compartment'],
    ...     chr_name='chr1',
    ...     resolution=100000
    ... )
    >>> # Figure displays automatically in Jupyter
    """
    # Power exponent to unit prefix mapping
    power_exp_to_prefix_map = {0: '', 3: 'K', 6: 'M', 9: 'G', 12: 'T', 15: 'P', 18: 'E', 21: 'Z', 24: 'Y'}
    power_exp_order_list = [0, 3, 6, 9, 12, 15, 18, 21, 24]

    # Calculate resolution power exponent and prefix
    resolution_power_exp = None
    resolution_power_exp_prefix = ''
    if resolution is not None:
        resolution_power_exp = power_exp_order_list[int(np.log10(resolution)) // 3]
        resolution_power_exp_prefix = power_exp_to_prefix_map[resolution_power_exp]

    # Separate A and B compartments
    A_compartment = np.zeros_like(assigned_AB_compartment)
    B_compartment = np.zeros_like(assigned_AB_compartment)

    A_loc_bool = assigned_AB_compartment > 0
    B_loc_bool = assigned_AB_compartment < 0

    A_compartment[A_loc_bool] = assigned_AB_compartment[assigned_AB_compartment > 0]
    B_compartment[B_loc_bool] = assigned_AB_compartment[assigned_AB_compartment < 0]

    # Create figure
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    total_length = assigned_AB_compartment.shape[0]

    # Plot A (red) and B (blue) compartments
    plt.plot(A_compartment, 'r', linewidth=1, label="A")
    plt.plot(B_compartment, 'b', linewidth=1, label="B")
    plt.hlines(0, 0, total_length, 'k', linewidth=1)

    # Add legend if requested
    if show_legend:
        legend_font = matplotlib.font_manager.FontProperties(family="serif", weight="bold")
        legend_font.set_name("DejaVu Sans Mono")
        legend_font.set_size(5)
        plt.legend(frameon=False, loc=(0,0.9), prop=legend_font)

    # Set limits
    plt.xlim(0, total_length)

    # Calculate x-axis ticks and labels with appropriate units
    if resolution is not None:
        # Create 5 evenly-spaced tick positions
        chr_loci_locs = np.linspace(0, total_length * resolution, 5)

        # Determine appropriate power exponent for x-axis labels
        min_exp = int(np.floor(np.log10(chr_loci_locs[1:])).min())
        target_power_exp = power_exp_order_list[min_exp // 3]
        target_power_exp_prefix = power_exp_to_prefix_map[target_power_exp]

        # Set x-axis ticks with formatted labels
        plt.xticks(chr_loci_locs // resolution,
                   (chr_loci_locs // 10**target_power_exp).astype(np.int64),
                   fontsize=6, family="serif", fontname="DejaVu Sans Mono", weight="bold")

        # Set x-axis label with units
        plt.xlabel(f"Chromosomal Position ({target_power_exp_prefix}bp)", fontsize=8,
                   family="serif", fontname="DejaVu Sans Mono", weight="bold")
    else:
        # No resolution provided - use generic label
        plt.xticks([])
        plt.xlabel("Chromosomal Position", fontsize=8, family="serif",
                   fontname="DejaVu Sans Mono", weight="bold")

    # Set y-axis ticks
    plt.yticks([0], [0], fontsize=6, family="serif", fontname="DejaVu Sans Mono", weight="bold")

    # Set y-axis label
    plt.ylabel("Chr Vect Value", fontsize=8, family="serif",
               fontname="DejaVu Sans Mono", weight="bold")

    # Add title if chr_name and resolution provided
    if chr_name and resolution:
        if (resolution % 10**resolution_power_exp) > 0:
            resolution_val_str = f"{resolution/10**resolution_power_exp:.1f}"
        else:
            resolution_val_str = f"{resolution/10**resolution_power_exp:.0f}"

        plt.title(f"{chr_name} - {resolution_val_str}{resolution_power_exp_prefix}bp Resolution",
                 fontsize=9, family="serif", fontname="DejaVu Sans Mono", weight="bold")
    elif chr_name:
        plt.title(f"{chr_name}", fontsize=9, family="serif",
                 fontname="DejaVu Sans Mono", weight="bold")

    # Remove all spins except the bottom visible
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)

    plt.tight_layout()

    # Save figure if output_path provided
    if output_path is not None:
        plt.savefig(output_path, dpi=dpi, bbox_inches='tight')

    # Return figure and axes (caller decides whether to close)
    return fig, ax
