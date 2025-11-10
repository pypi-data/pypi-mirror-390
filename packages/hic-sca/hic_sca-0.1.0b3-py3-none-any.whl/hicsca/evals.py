"""
HiC-SCA Evaluation Module

Provides tools for evaluating A-B compartment predictions across:
- Multiple resolutions within the same dataset (cross-resolution analysis)
- Multiple datasets at the same resolution (cross-dataset analysis)

Includes Matthews Correlation Coefficient (MCC) calculation and visualization.
"""

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.cm import ScalarMappable
import os
from typing import Dict, List, Tuple, Optional, Union


class MCCCalculator:
    """
    Computes Matthews Correlation Coefficient (MCC) between A-B compartment predictions.

    MCC measures the agreement between two binary classifications (A vs B compartments),
    handling cases where predictions may have opposite orientations or be incomplete.
    """

    @staticmethod
    def compute_AB_MCC(ref_AB_compartment: np.ndarray,
                       pred_AB_compartment: np.ndarray,
                       auto_flip: bool = True) -> Tuple[float, int, int, int, int, bool, bool]:
        """
        Compute MCC between reference and predicted A-B compartments.

        Parameters
        ----------
        ref_AB_compartment : np.ndarray
            Reference compartment assignments (positive=A, negative=B, zero=excluded)
        pred_AB_compartment : np.ndarray
            Predicted compartment assignments (positive=A, negative=B, zero=excluded)
        auto_flip : bool, optional
            If True, automatically flip prediction orientation if MCC is negative (default: True)

        Returns
        -------
        MCC : float
            Matthews Correlation Coefficient (0 if undefined)
        TP : int
            True positives (A predicted as A)
        FP : int
            False positives (A predicted as B)
        TN : int
            True negatives (B predicted as B)
        FN : int
            False negatives (B predicted as A)
        zeroed_MCC_status : bool
            True if MCC was zeroed due to undefined denominator
        reversed_orient_status : bool
            True if prediction was flipped, False otherwise, None if MCC was zeroed
        """
        zeroed_MCC_status = False
        reversed_orient_status = False

        # Find loci present in both predictions (non-zero)
        pred_non_zero_bool = pred_AB_compartment != 0
        ref_non_zero_bool = ref_AB_compartment != 0
        include_MCC = pred_non_zero_bool & ref_non_zero_bool

        # Binary classification: A (positive) vs B (negative)
        pred_A_compartment = pred_AB_compartment[include_MCC] > 0
        pred_B_compartment = pred_AB_compartment[include_MCC] < 0

        ref_A_compartment = ref_AB_compartment[include_MCC] > 0
        ref_B_compartment = ref_AB_compartment[include_MCC] < 0

        # Compute confusion matrix
        TP = (pred_A_compartment & ref_A_compartment).sum()
        FN = (pred_B_compartment & ref_A_compartment).sum()
        TN = (pred_B_compartment & ref_B_compartment).sum()
        FP = (pred_A_compartment & ref_B_compartment).sum()

        MCC_denominator = np.sqrt(TP+FP) * np.sqrt(TP+FN) * np.sqrt(TN+FP) * np.sqrt(TN+FN)

        # Check if denominator is zero
        if MCC_denominator == 0:
            zeroed_MCC_status = True

        else:
            MCC = (TP * TN - FP * FN) / MCC_denominator

            # If MCC is negative and auto_flip is enabled, try flipping the prediction
            if auto_flip and MCC < 0:
                # Flip and recompute
                pred_A_compartment = pred_AB_compartment[include_MCC] < 0
                pred_B_compartment = pred_AB_compartment[include_MCC] > 0

                TP = (pred_A_compartment & ref_A_compartment).sum()
                FN = (pred_B_compartment & ref_A_compartment).sum()
                TN = (pred_B_compartment & ref_B_compartment).sum()
                FP = (pred_A_compartment & ref_B_compartment).sum()

                MCC = (TP * TN - FP * FN) / MCC_denominator
                reversed_orient_status = True

        # Zero-out everything if MCC is undefined
        if zeroed_MCC_status:
            MCC = 0
            TP = FN = TN = FP = 0
            reversed_orient_status = None

        return MCC, TP, FP, TN, FN, zeroed_MCC_status, reversed_orient_status


class CrossResolutionAnalyzer:
    """
    Analyzes agreement between compartment predictions at different resolutions
    within the same Hi-C dataset.
    """

    def __init__(self, results_dict: Dict,
                 resolutions: Optional[List[int]] = None,
                 chr_names: Optional[List[str]] = None):
        """
        Initialize cross-resolution analyzer.

        Parameters
        ----------
        results_dict : Dict
            HiCSCA results dictionary with structure: results_dict[resolution][chr_name]
        resolutions : List[int], optional
            List of resolutions to analyze (in bp). If None, uses all available resolutions.
        chr_names : List[str], optional
            List of chromosome names to analyze. If None, uses all available chromosomes.
        """
        self.results_dict = results_dict

        # Auto-detect resolutions if not provided
        if resolutions is None:
            self.resolutions = sorted(results_dict.keys(), reverse=True)
        else:
            self.resolutions = sorted(resolutions, reverse=True)

        # Auto-detect chr_names if not provided
        if chr_names is None:
            # Get chr_names from first resolution
            first_res = self.resolutions[0]
            self.chr_names = list(results_dict[first_res].keys())
        else:
            self.chr_names = chr_names

        self.num_resolutions = len(self.resolutions)
        self.num_chrs = len(self.chr_names)

        # Initialize storage for results
        self.mcc_matrices = {}  # Per-chromosome MCC matrices, includes 'all' key
        self.orientation_matrices = {}  # Per-chromosome orientation tracking, includes 'all' key
        self._analyzed = False  # Track if analyze() has been called

    @staticmethod
    def predict_AB_compartment_from_high_to_low_res(high_res_AB_compartment: np.ndarray,
                                                     res_multiple: int) -> np.ndarray:
        """
        Downsample high-resolution compartment predictions to lower resolution.

        Uses weighted averaging where each low-res bin is computed as:
        sum(x_i * x_i^2) / sum(x_i^2) for high-res values x_i in that bin

        Parameters
        ----------
        high_res_AB_compartment : np.ndarray
            High-resolution compartment assignments
        res_multiple : int
            Resolution multiplier (low_res / high_res)

        Returns
        -------
        np.ndarray
            Low-resolution compartment predictions
        """
        high_res_length = high_res_AB_compartment.shape[0]
        reshape_length = high_res_length // res_multiple
        remainder = high_res_length % res_multiple

        # Reshape into blocks
        reshaped_array = high_res_AB_compartment[:reshape_length * res_multiple].reshape((-1, res_multiple))

        # Handle remainder
        if remainder > 0:
            reshaped_array = np.append(reshaped_array, np.zeros((1, res_multiple)), axis=0)
            reshaped_array[-1, :remainder] = high_res_AB_compartment[reshape_length * res_multiple:]

        # Weighted averaging: sum(sign(x)*x^2) / sum(x^2)
        squared_array = reshaped_array ** 2
        sum_squared_array = squared_array.sum(axis=1)

        return np.divide((squared_array * reshaped_array).sum(axis=1),
                        sum_squared_array,
                        where=sum_squared_array!=0)

    def analyze(self) -> None:
        """
        Perform cross-resolution analysis on HiCSCA results.

        Results are stored internally in self.mcc_matrices and self.orientation_matrices.
        Each dictionary contains per-chromosome results plus an 'all' key for genome-wide results.

        If analyze() has already been called, returns immediately without recomputing.
        """
        # Check if already analyzed
        if self._analyzed:
            return

        # Initialize result matrices
        mcc_all = -np.ones((self.num_resolutions, self.num_resolutions), dtype=np.float64)
        np.fill_diagonal(mcc_all, 1.0)
        orient_all = -np.ones((self.num_resolutions, self.num_resolutions), dtype=np.int8)
        np.fill_diagonal(orient_all, self.num_chrs)  # Diagonal = number of chromosomes

        for chr_name in self.chr_names:
            self.mcc_matrices[chr_name] = -np.ones((self.num_resolutions, self.num_resolutions), dtype=np.float64)
            np.fill_diagonal(self.mcc_matrices[chr_name], 1.0)
            self.orientation_matrices[chr_name] = -np.ones((self.num_resolutions, self.num_resolutions), dtype=np.int8)
            np.fill_diagonal(self.orientation_matrices[chr_name], self.num_chrs)

        # Compare each resolution pair
        for res_idx_low, res_low in enumerate(self.resolutions):
            for res_idx_high in range(res_idx_low + 1, self.num_resolutions):
                res_high = self.resolutions[res_idx_high]

                # Check if resolutions are compatible
                if (res_low % res_high) != 0:
                    continue

                res_multiple = res_low // res_high

                # Accumulate genome-wide statistics
                penalty = TP = TN = FP = FN = 0

                for chr_name in self.chr_names:

                    # Get results for both resolutions
                    low_res_result = self.results_dict[res_low][chr_name]
                    high_res_result = self.results_dict[res_high][chr_name]

                    if (low_res_result['Success'] is False) or (high_res_result['Success'] is False):
                        # Handle missing data with penalty
                        if (low_res_result['Success'] is False) and (high_res_result['Success'] is False):
                            penalty += low_res_result['deg'].shape[0]
                        elif low_res_result['Success'] is False:
                            penalty += (low_res_result['assigned_AB_compartment'] != 0).sum()
                        else:
                            penalty += (high_res_result['assigned_AB_compartment'] != 0).sum()

                        continue

                    # Get compartment predictions
                    low_res_AB = low_res_result['assigned_AB_compartment'].copy()
                    high_res_AB = high_res_result['assigned_AB_compartment'].copy()

                    # Downsample high-res to low-res
                    predicted_low_res_AB = self.predict_AB_compartment_from_high_to_low_res(
                        high_res_AB, res_multiple
                    )

                    # Compute MCC
                    current_MCC, current_TP, current_FP, current_TN, current_FN, \
                        zeroed_MCC_status, reversed_orient_status = \
                        MCCCalculator.compute_AB_MCC(low_res_AB, predicted_low_res_AB)

                    if zeroed_MCC_status:
                        # Compute penalty for undefined MCC
                        intersec_loci = (low_res_AB != 0) & (predicted_low_res_AB != 0)
                        intersec_loci_num = intersec_loci.sum()

                        if intersec_loci_num > 0:
                            penalty += intersec_loci_num
                        else:
                            penalty += low_res_AB.shape[0]
                    else:
                        # Accumulate confusion matrix
                        TP += current_TP
                        FN += current_FN
                        TN += current_TN
                        FP += current_FP

                        # Store per-chromosome results
                        self.mcc_matrices[chr_name][res_idx_low, res_idx_high] = current_MCC
                        self.orientation_matrices[chr_name][res_idx_low, res_idx_high] = int(reversed_orient_status)
                        orient_all[res_idx_low, res_idx_high] += (not reversed_orient_status)

                # Compute genome-wide MCC with penalty
                FN += penalty / 2
                FP += penalty / 2

                MCC_denominator = np.sqrt(TP+FP) * np.sqrt(TP+FN) * np.sqrt(TN+FP) * np.sqrt(TN+FN)

                if MCC_denominator == 0:
                    MCC = 0.0
                else:
                    MCC = (TP * TN - FP * FN) / MCC_denominator

                mcc_all[res_idx_low, res_idx_high] = MCC

        # Store genome-wide results with 'all' key
        self.mcc_matrices['all'] = mcc_all
        self.orientation_matrices['all'] = orient_all

        # Mark as analyzed
        self._analyzed = True

    def plot_cross_resolution_mcc(self,
                                   chr_name: str = 'all',
                                   figsize: Tuple[float, float] = (2.8, 2.8),
                                   dpi: int = 300,
                                   background_alpha: float = 1,
                                   plot_colorbar: bool = True,
                                   save_path: Optional[str] = None) -> Tuple[plt.Figure, plt.Axes, Optional[plt.Figure], Optional[plt.Axes]]:
        """
        Plot cross-resolution MCC matrix as a heatmap with optional separate colorbar figure.

        Parameters
        ----------
        chr_name : str, optional
            Chromosome name to plot (default: 'all' for genome-wide)
        figsize : Tuple[float, float], optional
            Figure size in inches
        dpi : int, optional
            Figure DPI
        background_alpha : float, optional
            Alpha value for figure backgrounds (0=transparent, 1=opaque). Default: 1
        plot_colorbar : bool, optional
            Whether to generate colorbar figure. Default: True
        save_path : str, optional
            Path to save figure (PNG/JPEG). If None, figure is not saved.
            If provided and plot_colorbar=True, colorbar is automatically saved as '{filename}_colorbar.{ext}'.

        Returns
        -------
        fig : plt.Figure
            Main heatmap figure object
        ax : plt.Axes
            Main heatmap axes object
        colorbar_fig : Optional[plt.Figure]
            Colorbar figure object (None if plot_colorbar=False)
        colorbar_ax : Optional[plt.Axes]
            Colorbar axes object (None if plot_colorbar=False)
        """
        # Ensure analyze() has been called
        if not self._analyzed:
            self.analyze()

        # Get the MCC matrix for this chromosome
        mcc_matrix = self.mcc_matrices[chr_name]

        # Auto-generate title
        if chr_name == 'all':
            title = "Cross-Res MCC (Genome-wide)"
        else:
            title = f"Cross-Res MCC ({chr_name})"

        # Create mask for -1 values (N/A pairs)
        mask = mcc_matrix == -1
        NA_masked_data = np.ma.masked_where(~mask, mcc_matrix)
        value_masked_data = np.ma.masked_where(mask, mcc_matrix)

        # Format resolution labels with automatic unit selection
        power_exp_to_prefix_map = {0: '', 3: 'K', 6: 'M', 9: 'G', 12: 'T', 15: 'P', 18: 'E', 21: 'Z', 24: 'Y'}
        power_exp_order_list = [0, 3, 6, 9, 12, 15, 18, 21, 24]

        resolution_ticks = []
        for res in self.resolutions:
            # Calculate power exponent and prefix
            resolution_power_exp = power_exp_order_list[int(np.log10(res)) // 3]
            resolution_power_exp_prefix = power_exp_to_prefix_map[resolution_power_exp]

            # Format value with appropriate decimal places
            if (res % 10**resolution_power_exp) > 0:
                resolution_val_str = f"{res/10**resolution_power_exp:.1f}"
            else:
                resolution_val_str = f"{res/10**resolution_power_exp:.0f}"

            resolution_ticks.append(f"{resolution_val_str}{resolution_power_exp_prefix}bp")

        # Create figure
        fig, ax = plt.subplots(1, 1, figsize=figsize, dpi=dpi)
        fig.patch.set_alpha(background_alpha)

        # Plot with two colormaps: gray for N/A, bwr for values
        ax.imshow(NA_masked_data, cmap="Grays", vmin=-1.5, vmax=-0.8, aspect='equal')
        ax.imshow(value_masked_data, cmap="bwr", vmin=0, vmax=1, aspect='equal')

        # Set labels
        ax.set_xticks(np.arange(self.num_resolutions), resolution_ticks,
                     rotation=90, fontsize=6, fontname="DejaVu Sans Mono", weight="bold")
        ax.set_yticks(np.arange(self.num_resolutions), resolution_ticks,
                     fontsize=6, fontname="DejaVu Sans Mono", weight="bold")

        ax.set_ylabel("Lower/Target Resolution", fontsize=7,
                     fontname="DejaVu Sans Mono", weight="bold")
        ax.set_xlabel("Higher/Source Resolution", fontsize=7,
                     fontname="DejaVu Sans Mono", weight="bold")
        ax.set_title(title, fontsize=8, fontname="DejaVu Sans Mono", weight="bold")

        plt.tight_layout()

        # Create colorbar figure if requested
        if plot_colorbar:
            colorbar_fig = plt.figure(figsize=(2.562, 0.376), dpi=dpi)
            colorbar_fig.patch.set_alpha(background_alpha)

            # Add axes for horizontal colorbar
            colorbar_ax = colorbar_fig.add_axes([0.05, 0.03, 1.2, 0.3])

            # Create colorbar with bwr colormap
            matplotlib.colorbar.ColorbarBase(
                colorbar_ax,
                mappable=ScalarMappable(norm=Normalize(vmin=0, vmax=1), cmap='bwr'),
                orientation='horizontal'
            )

            # Set colorbar ticks and labels
            colorbar_ax.set_xticks(
                np.arange(0, 1.1, 0.2),
                [f"{x:.1f}" for x in np.arange(0, 1.1, 0.2)],
                fontsize=6,
                fontname="DejaVu Sans Mono",
                weight="bold"
            )

            # Set colorbar title
            colorbar_ax.set_title("MCC Corr", fontsize=7, fontname="DejaVu Sans Mono", weight="bold")
        else:
            colorbar_fig = None
            colorbar_ax = None

        # Save figures if path provided
        if save_path is not None:
            # Save main figure
            fig.savefig(save_path, dpi=dpi, bbox_inches='tight')

            # Save colorbar if it was generated
            if plot_colorbar:
                filename, ext = os.path.splitext(save_path)
                colorbar_save_path = f"{filename}_colorbar{ext}"
                colorbar_fig.savefig(colorbar_save_path, dpi=dpi, bbox_inches='tight')

        return fig, ax, colorbar_fig, colorbar_ax


class CrossDatasetAnalyzer:
    """
    Analyzes agreement between compartment predictions from different Hi-C datasets
    at the same resolution.

    Includes both MCC correlation analysis and orientation agreement tracking.
    """

    def __init__(self, dataset_dict: Dict[str, Dict],
                 resolutions: Optional[List[int]] = None,
                 dataset_ids: Optional[List[str]] = None,
                 chr_names: Optional[List[str]] = None):
        """
        Initialize cross-dataset analyzer.

        Parameters
        ----------
        dataset_dict : Dict[str, Dict]
            Dictionary mapping dataset_id to HiCSCA results_dict.
            Each results_dict has structure: results_dict[resolution][chr_name]
        resolutions : List[int], optional
            List of resolutions to analyze (in bp). If None, auto-detects from first dataset.
        dataset_ids : List[str], optional
            List of dataset identifiers to use (in order). If None, uses keys from dataset_dict.
        chr_names : List[str], optional
            List of chromosome names to analyze. If None, auto-detects from first dataset.
        """
        self.dataset_dict = dataset_dict

        # Set dataset_ids
        if dataset_ids is None:
            self.dataset_ids = list(dataset_dict.keys())
        else:
            self.dataset_ids = dataset_ids

        self.num_datasets = len(self.dataset_ids)

        # Get first dataset for auto-detection
        first_dataset_id = self.dataset_ids[0]
        first_results = dataset_dict[first_dataset_id]

        # Auto-detect resolutions if not provided
        if resolutions is None:
            self.resolutions = sorted(first_results.keys())
        else:
            self.resolutions = sorted(resolutions)

        # Auto-detect chr_names if not provided
        if chr_names is None:
            # Get chr_names from first resolution of first dataset
            first_res = self.resolutions[0]
            self.chr_names = sorted(first_results[first_res].keys())
        else:
            self.chr_names = chr_names

        self.num_chrs = len(self.chr_names)

        # Initialize storage for each resolution
        self.mcc_matrices = {}  # {resolution: {chr_name: matrix, 'all': matrix}}
        self.orientation_matrices = {}  # {resolution: {chr_name: matrix, 'all': matrix}}
        self._analyzed_resolutions = set()  # Track which resolutions have been analyzed

    def analyze(self) -> None:
        """
        Perform cross-dataset MCC correlation analysis for all configured resolutions.

        Results are stored internally in self.mcc_matrices[resolution] and
        self.orientation_matrices[resolution]. Each contains per-chromosome results
        plus an 'all' key for genome-wide results.

        Only analyzes resolutions that haven't been analyzed yet (caching).
        """
        # Analyze each resolution
        for resolution in self.resolutions:
            # Check if already analyzed
            if resolution in self._analyzed_resolutions:
                continue

            # Initialize storage for this resolution
            mcc_matrices_res = {}
            orientation_matrices_res = {}

            # Initialize result matrices
            mcc_all = np.zeros((self.num_datasets, self.num_datasets), dtype=np.float64)
            np.fill_diagonal(mcc_all, 1.0)

            orient_all = np.zeros((self.num_datasets, self.num_datasets), dtype=np.int8)
            np.fill_diagonal(orient_all, self.num_chrs)  # Diagonal = number of chromosomes

            for chr_name in self.chr_names:
                mcc_matrices_res[chr_name] = np.zeros((self.num_datasets, self.num_datasets), dtype=np.float64)
                np.fill_diagonal(mcc_matrices_res[chr_name], 1.0)

                orientation_matrices_res[chr_name] = np.zeros((self.num_datasets, self.num_datasets), dtype=bool)
                np.fill_diagonal(orientation_matrices_res[chr_name], True)

            # Compare each dataset pair
            for dataset_idx_ref, dataset_id_ref in enumerate(self.dataset_ids):
                for dataset_idx_pred, dataset_id_pred in enumerate(self.dataset_ids):

                    if dataset_idx_ref == dataset_idx_pred:
                        continue

                    # Accumulate genome-wide statistics
                    penalty = TP = TN = FP = FN = 0

                    for chr_name in self.chr_names:
                        # Get results for both datasets
                        ref_result = self.dataset_dict[dataset_id_ref][resolution][chr_name]
                        pred_result = self.dataset_dict[dataset_id_pred][resolution][chr_name]

                        if (ref_result['Success'] is False) or (pred_result['Success'] is False):
                            # Handle missing data with penalty
                            if (ref_result['Success'] is False) and (pred_result['Success'] is False):
                                penalty += ref_result['deg'].shape[0]
                            elif ref_result['Success'] is False:
                                penalty += (ref_result['assigned_AB_compartment'] != 0).sum()
                            else:
                                penalty += (pred_result['assigned_AB_compartment'] != 0).sum()

                            continue

                        # Get compartment predictions
                        ref_AB = ref_result['assigned_AB_compartment'].copy()
                        pred_AB = pred_result['assigned_AB_compartment'].copy()

                        # Compute MCC
                        current_MCC, current_TP, current_FP, current_TN, current_FN, \
                            zeroed_MCC_status, reversed_orient_status = \
                            MCCCalculator.compute_AB_MCC(ref_AB, pred_AB)

                        if zeroed_MCC_status:
                            # Compute penalty for undefined MCC
                            include_MCC = (ref_AB != 0) & (pred_AB != 0)
                            include_MCC_num = include_MCC.sum()

                            if include_MCC_num > 0:
                                penalty += include_MCC_num
                            else:
                                penalty += ref_AB.shape[0]
                        else:
                            # Accumulate confusion matrix
                            TP += current_TP
                            FN += current_FN
                            TN += current_TN
                            FP += current_FP

                            # Store per-chromosome results
                            mcc_matrices_res[chr_name][dataset_idx_ref, dataset_idx_pred] = current_MCC
                            orientation_matrices_res[chr_name][dataset_idx_ref, dataset_idx_pred] = not reversed_orient_status
                            orient_all[dataset_idx_ref, dataset_idx_pred] += (not reversed_orient_status)

                    # Compute genome-wide MCC with penalty
                    FN += penalty / 2
                    FP += penalty / 2

                    MCC_denominator = np.sqrt(TP+FP) * np.sqrt(TP+FN) * np.sqrt(TN+FP) * np.sqrt(TN+FN)

                    if MCC_denominator == 0:
                        MCC = 0.0
                    else:
                        MCC = (TP * TN - FP * FN) / MCC_denominator

                    mcc_all[dataset_idx_ref, dataset_idx_pred] = MCC

            # Store genome-wide results with 'all' key
            mcc_matrices_res['all'] = mcc_all
            orientation_matrices_res['all'] = orient_all

            # Store results for this resolution
            self.mcc_matrices[resolution] = mcc_matrices_res
            self.orientation_matrices[resolution] = orientation_matrices_res

            # Mark as analyzed
            self._analyzed_resolutions.add(resolution)

    def _plot_heatmap(self, data_matrix: np.ndarray,
                      tick_labels: List[str],
                      title: str = "",
                      vmin: float = 0,
                      vmax: float = 1,
                      cmap: str = "bwr",
                      figsize: Tuple[float, float] = (2.9, 2.9),
                      dpi: int = 300) -> Tuple[plt.Figure, plt.Axes]:
        """
        Internal method to plot a heatmap (shared between MCC and orientation plots).

        Parameters
        ----------
        data_matrix : np.ndarray
            Matrix to plot
        tick_labels : List[str]
            Labels for both axes
        title : str, optional
            Plot title
        vmin : float, optional
            Minimum value for colormap
        vmax : float, optional
            Maximum value for colormap
        cmap : str, optional
            Colormap name
        figsize : Tuple[float, float], optional
            Figure size in inches
        dpi : int, optional
            Figure DPI

        Returns
        -------
        fig : plt.Figure
            Figure object
        ax : plt.Axes
            Axes object
        """
        num_datasets = len(tick_labels)

        # Create figure
        fig, ax = plt.subplots(1, 1, figsize=figsize, dpi=dpi)
        fig.patch.set_alpha(0)

        # Plot heatmap
        im = ax.imshow(data_matrix, cmap=cmap, vmin=vmin, vmax=vmax, aspect='equal')

        # Set labels
        ax.set_xticks(np.arange(num_datasets), tick_labels,
                     fontsize=6, fontname="DejaVu Sans Mono", weight="bold")
        ax.set_yticks(np.arange(num_datasets), tick_labels,
                     fontsize=6, fontname="DejaVu Sans Mono", weight="bold")

        if title:
            ax.set_title(title, fontsize=8, fontname="DejaVu Sans Mono", weight="bold")

        # Adjust tick label alignment if needed
        ytick_labels_list = ax.get_yticklabels()
        for idx, label in enumerate(ax.get_xticklabels()):
            label.set_verticalalignment("center")
            label.set_position((0, -0.01))

        plt.tight_layout()

        return fig, ax

    def plot_mcc_correlation(self,
                            resolution: int,
                            chr_name: str = 'all',
                            tick_labels: Optional[List[str]] = None,
                            title: Optional[str] = None,
                            figsize: Tuple[float, float] = (2.9, 2.9),
                            dpi: int = 300,
                            background_alpha: float = 1,
                            plot_colorbar: bool = True,
                            save_path: Optional[str] = None) -> Tuple[plt.Figure, plt.Axes, Optional[plt.Figure], Optional[plt.Axes]]:
        """
        Plot cross-dataset MCC correlation matrix as a heatmap with optional separate colorbar figure.

        Parameters
        ----------
        resolution : int
            Resolution to plot (in bp)
        chr_name : str, optional
            Chromosome name to plot (default: 'all' for genome-wide)
        tick_labels : List[str], optional
            Custom labels for datasets (default: dataset_ids)
        title : str, optional
            Plot title (default: auto-generated)
        figsize : Tuple[float, float], optional
            Figure size in inches
        dpi : int, optional
            Figure DPI
        background_alpha : float, optional
            Alpha value for figure backgrounds (0=transparent, 1=opaque). Default: 1
        plot_colorbar : bool, optional
            Whether to generate colorbar figure. Default: True
        save_path : str, optional
            Path to save figure (PNG/JPEG). If None, figure is not saved.
            If provided and plot_colorbar=True, colorbar is automatically saved as '{filename}_colorbar.{ext}'.

        Returns
        -------
        fig : plt.Figure
            Main heatmap figure object
        ax : plt.Axes
            Main heatmap axes object
        colorbar_fig : Optional[plt.Figure]
            Colorbar figure object (None if plot_colorbar=False)
        colorbar_ax : Optional[plt.Axes]
            Colorbar axes object (None if plot_colorbar=False)
        """
        # Ensure analyze() has been called
        if resolution not in self._analyzed_resolutions:
            self.analyze()

        # Get the MCC matrix
        mcc_matrix = self.mcc_matrices[resolution][chr_name]

        # Set default tick labels
        if tick_labels is None:
            tick_labels = self.dataset_ids

        # Auto-generate title if not provided
        if title is None:
            res_kb = int(resolution / 1000)
            if chr_name == 'all':
                title = f"Cross-Dataset MCC ({res_kb}kb, Genome-wide)"
            else:
                title = f"Cross-Dataset MCC ({res_kb}kb, {chr_name})"

        fig, ax = self._plot_heatmap(mcc_matrix, tick_labels, title=title,
                                     vmin=0, vmax=1, cmap="bwr",
                                     figsize=figsize, dpi=dpi)

        # Set background alpha
        fig.patch.set_alpha(background_alpha)

        # Create colorbar figure if requested
        if plot_colorbar:
            colorbar_fig = plt.figure(figsize=(2.562, 0.376), dpi=dpi)
            colorbar_fig.patch.set_alpha(background_alpha)

            # Add axes for horizontal colorbar
            colorbar_ax = colorbar_fig.add_axes([0.05, 0.03, 1.2, 0.3])

            # Create colorbar with bwr colormap
            matplotlib.colorbar.ColorbarBase(
                colorbar_ax,
                mappable=ScalarMappable(norm=Normalize(vmin=0, vmax=1), cmap='bwr'),
                orientation='horizontal'
            )

            # Set colorbar ticks and labels
            colorbar_ax.set_xticks(
                np.arange(0, 1.1, 0.2),
                [f"{x:.1f}" for x in np.arange(0, 1.1, 0.2)],
                fontsize=6,
                fontname="DejaVu Sans Mono",
                weight="bold"
            )

            # Set colorbar title
            colorbar_ax.set_title("MCC Corr", fontsize=7, fontname="DejaVu Sans Mono", weight="bold")
        else:
            colorbar_fig = None
            colorbar_ax = None

        # Save figures if path provided
        if save_path is not None:
            # Save main figure
            fig.savefig(save_path, dpi=dpi, bbox_inches='tight')

            # Save colorbar if it was generated
            if plot_colorbar:
                filename, ext = os.path.splitext(save_path)
                colorbar_save_path = f"{filename}_colorbar{ext}"
                colorbar_fig.savefig(colorbar_save_path, dpi=dpi, bbox_inches='tight')

        return fig, ax, colorbar_fig, colorbar_ax

    def plot_orientation_agreement(self,
                                   resolution: int,
                                   chr_name: str = 'all',
                                   tick_labels: Optional[List[str]] = None,
                                   title: Optional[str] = None,
                                   figsize: Tuple[float, float] = (2.9, 2.9),
                                   dpi: int = 300,
                                   background_alpha: float = 1,
                                   plot_colorbar: bool = True,
                                   save_path: Optional[str] = None) -> Tuple[plt.Figure, plt.Axes, Optional[plt.Figure], Optional[plt.Axes]]:
        """
        Plot cross-dataset orientation agreement matrix as a heatmap with optional separate colorbar figure.

        The orientation matrix shows how many chromosomes have the same orientation
        between two datasets.

        Parameters
        ----------
        resolution : int
            Resolution to plot (in bp)
        chr_name : str, optional
            Chromosome name to plot (default: 'all' for genome-wide)
        tick_labels : List[str], optional
            Custom labels for datasets (default: dataset_ids)
        title : str, optional
            Plot title (default: auto-generated)
        figsize : Tuple[float, float], optional
            Figure size in inches
        dpi : int, optional
            Figure DPI
        background_alpha : float, optional
            Alpha value for figure backgrounds (0=transparent, 1=opaque). Default: 1
        plot_colorbar : bool, optional
            Whether to generate colorbar figure. Default: True
        save_path : str, optional
            Path to save figure (PNG/JPEG). If None, figure is not saved.
            If provided and plot_colorbar=True, colorbar is automatically saved as '{filename}_colorbar.{ext}'.

        Returns
        -------
        fig : plt.Figure
            Main heatmap figure object
        ax : plt.Axes
            Main heatmap axes object
        colorbar_fig : Optional[plt.Figure]
            Colorbar figure object (None if plot_colorbar=False)
        colorbar_ax : Optional[plt.Axes]
            Colorbar axes object (None if plot_colorbar=False)
        """
        # Ensure analyze() has been called
        if resolution not in self._analyzed_resolutions:
            self.analyze()

        # Get the orientation matrix
        orientation_matrix = self.orientation_matrices[resolution][chr_name]

        # Set default tick labels
        if tick_labels is None:
            tick_labels = self.dataset_ids

        # Auto-generate title if not provided
        if title is None:
            res_kb = int(resolution / 1000)
            if chr_name == 'all':
                title = f"Cross-Dataset Orientation Agreement ({res_kb}kb, Genome-wide)"
            else:
                title = f"Cross-Dataset Orientation Agreement ({res_kb}kb, {chr_name})"

        fig, ax = self._plot_heatmap(orientation_matrix, tick_labels, title=title,
                                     vmin=0, vmax=self.num_chrs, cmap="bwr",
                                     figsize=figsize, dpi=dpi)

        # Set background alpha
        fig.patch.set_alpha(background_alpha)

        # Create colorbar figure if requested
        if plot_colorbar:
            colorbar_fig = plt.figure(figsize=(2.562, 0.376), dpi=dpi)
            colorbar_fig.patch.set_alpha(background_alpha)

            # Add axes for horizontal colorbar
            colorbar_ax = colorbar_fig.add_axes([0.05, 0.03, 1.2, 0.3])

            # Create colorbar with bwr colormap
            matplotlib.colorbar.ColorbarBase(
                colorbar_ax,
                mappable=ScalarMappable(norm=Normalize(vmin=0, vmax=self.num_chrs), cmap='bwr'),
                orientation='horizontal'
            )

            # Calculate tick spacing (aim for ~5 ticks)
            tick_step = max(1, self.num_chrs // 5)
            tick_values = np.arange(0, self.num_chrs + 1, tick_step)

            # Set colorbar ticks and labels
            colorbar_ax.set_xticks(
                tick_values,
                [f"{int(x)}" for x in tick_values],
                fontsize=6,
                fontname="DejaVu Sans Mono",
                weight="bold"
            )

            # Set colorbar title
            colorbar_ax.set_title("Num Chr", fontsize=7, fontname="DejaVu Sans Mono", weight="bold")
        else:
            colorbar_fig = None
            colorbar_ax = None

        # Save figures if path provided
        if save_path is not None:
            # Save main figure
            fig.savefig(save_path, dpi=dpi, bbox_inches='tight')

            # Save colorbar if it was generated
            if plot_colorbar:
                filename, ext = os.path.splitext(save_path)
                colorbar_save_path = f"{filename}_colorbar{ext}"
                colorbar_fig.savefig(colorbar_save_path, dpi=dpi, bbox_inches='tight')

        return fig, ax, colorbar_fig, colorbar_ax
