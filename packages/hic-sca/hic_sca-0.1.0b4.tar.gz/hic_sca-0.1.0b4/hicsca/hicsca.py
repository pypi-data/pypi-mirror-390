"""
A-B Compartment Prediction from Hi-C Data

This module provides tools for analyzing Hi-C (chromosome conformation capture) data
to assign A-B chromosomal compartments using spectral clustering
"""

import numpy as np
import scipy.sparse as sp
import hicstraw
import warnings
import gc
import re
from typing import Dict, Tuple, List, Optional
import h5typer


def _natural_sort_key(text: str) -> List:
    """
    Generate a key for natural (human) sorting of strings with numbers.

    Converts strings like 'chr10' to ['chr', 10] for proper numeric sorting.
    This ensures chr1, chr2, ..., chr10, chr11 sort in the expected order
    rather than chr1, chr10, chr11, chr2, etc.

    Parameters
    ----------
    text : str
        String to generate sort key for (e.g., 'chr1', 'chr10')

    Returns
    -------
    List
        List of alternating strings and integers for sorting

    Examples
    --------
    >>> _natural_sort_key('chr1')
    ['chr', 1]
    >>> _natural_sort_key('chr10')
    ['chr', 10]
    >>> sorted(['chr1', 'chr10', 'chr2'], key=_natural_sort_key)
    ['chr1', 'chr2', 'chr10']
    """
    return [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', text)]


class HiCDataLoader:
    """Handles loading and parsing of Hi-C data files."""

    def __init__(self, hic_file_path: str):
        """
        Initialize the HiC data loader.

        Parameters
        ----------
        hic_file_path : str
            Path to the .hic file
        """
        self.hic_file_path = hic_file_path
        self.hic_file = hicstraw.HiCFile(hic_file_path)
        self.chr_length_dict = {}
        self.max_bp_length = 0
        self.autosomal_chr_names = []
        self.resolutions = []

        self._load_chromosome_info()

    def _load_chromosome_info(self) -> None:
        """Extract chromosome information from the HiC file."""
        for chr_obj in self.hic_file.getChromosomes():
            self.chr_length_dict[chr_obj.name] = chr_obj.length

            if chr_obj.length > self.max_bp_length:
                self.max_bp_length = chr_obj.length

        # Filter to autosomal chromosomes
        for chr_name in self.chr_length_dict.keys():
            # Exclude mitochondrial chromosome
            if "m" in chr_name.lower():
                continue
            # Exclude combination of all chromosomes
            elif "all" in chr_name.lower():
                continue
            else:
                self.autosomal_chr_names.append(chr_name)

        # Sort chromosomes using natural sorting (chr1, chr2, ..., chr10, chr11)
        self.autosomal_chr_names.sort(key=_natural_sort_key)

        self.resolutions = self.hic_file.getResolutions()

    def load_contact_map(self,
                        chr_name: str,
                        resolution: int,
                        data_type: str = "observed",
                        norm_type: str = "NONE") -> sp.csr_matrix:
        """
        Load a sparse contact map for a specific chromosome at a given resolution.

        Parameters
        ----------
        chr_name : str
            Chromosome name (e.g., 'chr1')
        resolution : int
            Resolution in base pairs
        data_type : str, optional
            Type of data to retrieve (default: "observed")
        norm_type : str, optional
            Normalization type (default: "NONE")

        Returns
        -------
        sp.csr_matrix
            Sparse contact map matrix
        """
        mzd = self.hic_file.getMatrixZoomData(
            chr_name, chr_name, data_type, norm_type, "BP", resolution
        )
        chr_length = self.chr_length_dict[chr_name]
        num_bins = int(np.ceil(chr_length / resolution))

        records = mzd.getRecords(1, chr_length, 1, chr_length)
        num_records = len(records)

        x_coords = np.zeros(num_records, dtype=np.int64)
        y_coords = np.zeros(num_records, dtype=np.int64)
        values = np.zeros(num_records, dtype=np.float64)

        for records_idx in range(num_records):
            x_coords[records_idx] = records[records_idx].binX
            y_coords[records_idx] = records[records_idx].binY
            values[records_idx] = records[records_idx].counts

        x_coords = x_coords // resolution
        y_coords = y_coords // resolution

        return sp.csr_matrix(
            (values, (x_coords, y_coords)),
            (num_bins, num_bins),
            dtype=np.float64
        )


class BackgroundNormalizer:
    """
    Handles background normalization for a specific Hi-C dataset at a given resolution.

    Each instance is specific to one dataset and one resolution.
    """

    def __init__(self, hic_loader: HiCDataLoader, resolution: int, chr_names: List[str],
                 data_type: str = "observed", norm_type: str = "NONE", smoothing_cutoff: int = 400):
        """
        Initialize the background normalizer for a specific dataset and resolution.

        Parameters
        ----------
        hic_loader : HiCDataLoader
            HiC data loader instance
        resolution : int
            Resolution in base pairs for this analysis
        chr_names : list of str
            List of chromosome names to process
        data_type : str, optional
            Type of data to retrieve from hic_loader (default: "observed").
            The hic_loader can return O/E contact matrices, but not available for
            "NONE" norm_type
        norm_type : str, optional
            Normalization type for hic_loader (default: "NONE").
            Set to "NONE" to retrieve un-normalized contact matrices
        smoothing_cutoff : int, optional
            Cutoff threshold for smoothing background contacts (default: 400)
        """
        self.hic_loader = hic_loader
        self.resolution = resolution
        self.chr_names = chr_names
        self.data_type = data_type
        self.norm_type = norm_type
        self.smoothing_cutoff = smoothing_cutoff
        self.background_contact_dict = {}
        self.distance_counts_dict = {}
        self.complete_background_contact = None
        self.complete_distance_counts = None
        self.avg_background_dist = None
        self.chr_norm_factors_dict = {}

    @staticmethod
    def _cum_background_contacts(input_contact_map: sp.csr_matrix,
                                 background_contact: Optional[np.ndarray] = None,
                                 distance_counts: Optional[np.ndarray] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate cumulative background contacts from a contact map.

        Parameters
        ----------
        input_contact_map : sp.csr_matrix
            Input sparse contact matrix
        background_contact : np.ndarray, optional
            Existing background contact array to update
        distance_counts : np.ndarray, optional
            Count of matrix elements at each genomic distance

        Returns
        -------
        tuple of (np.ndarray, np.ndarray)
            Updated background contacts and distance counts
        """
        max_distance = input_contact_map.shape[0]

        if background_contact is None:
            background_contact = np.zeros(max_distance, dtype=np.float64)
        elif background_contact.shape[0] < max_distance:
            dist_diff = max_distance - background_contact.shape[0]
            background_contact = np.concatenate([
                background_contact,
                np.zeros(dist_diff, dtype=np.float64)
            ])

        if distance_counts is None:
            distance_counts = np.zeros(max_distance, dtype=np.int64)
        elif distance_counts.shape[0] < max_distance:
            dist_diff = max_distance - distance_counts.shape[0]
            distance_counts = np.concatenate([
                distance_counts,
                np.zeros(dist_diff, dtype=np.int64)
            ])

        for idx in range(max_distance):
            current_max_distance = max_distance - idx
            background_contact[:current_max_distance] += input_contact_map[idx, idx:]
            distance_counts[:current_max_distance] += 1

        return background_contact, distance_counts

    def calculate_genome_background(self) -> None:
        """
        Calculate and smooth genome-wide background contact frequencies.

        This method computes background contact frequencies across all chromosomes
        specified during initialization, applies smoothing to low-count regions,
        and calculates chromosome-specific normalization factors.
        """
        max_dist_bins = np.int64(np.ceil(self.hic_loader.max_bp_length / self.resolution))
        self.complete_background_contact = np.zeros(max_dist_bins, dtype=np.float64)
        self.complete_distance_counts = np.zeros(max_dist_bins, dtype=np.float64)

        for chr_name in self.chr_names:
            raw_contact_map = self.hic_loader.load_contact_map(
                chr_name, self.resolution, data_type=self.data_type, norm_type=self.norm_type
            )

            current_background_contact, current_distance_counts = \
                self._cum_background_contacts(raw_contact_map)

            self.background_contact_dict[chr_name] = current_background_contact
            self.distance_counts_dict[chr_name] = current_distance_counts

            current_max_dist_bins = current_background_contact.shape[0]
            self.complete_background_contact[:current_max_dist_bins] += current_background_contact
            self.complete_distance_counts[:current_max_dist_bins] += current_distance_counts

            del raw_contact_map
            gc.collect()

        # Smooth the background distribution
        below_cutoff_idx = np.where(
            self.complete_background_contact < self.smoothing_cutoff
        )[0]
        max_bin_dist = self.complete_background_contact.shape[0]

        smoothed_background_contact = self.complete_background_contact.copy()
        smoothed_distance_counts = self.complete_distance_counts.copy()

        for current_idx in below_cutoff_idx:
            bin_size = 1

            while True:
                start_idx = current_idx
                stop_idx = current_idx + bin_size + 1
                start_stop_slice = slice(start_idx, stop_idx)

                if stop_idx > max_bin_dist:
                    break

                total_reads = self.complete_background_contact[start_stop_slice].sum()

                if total_reads < self.smoothing_cutoff:
                    # Deal with the end of the distribution
                    if stop_idx == max_bin_dist:
                        smoothed_background_contact[current_idx] = total_reads
                        smoothed_distance_counts[current_idx] = \
                            self.complete_distance_counts[start_stop_slice].sum()
                        break
                    else:
                        bin_size += 1
                else:
                    smoothed_background_contact[current_idx] = total_reads
                    smoothed_distance_counts[current_idx] = \
                        self.complete_distance_counts[start_stop_slice].sum()
                    break

        self.avg_background_dist = smoothed_background_contact / smoothed_distance_counts

        # Calculate chromosome normalization factors
        self.calculate_chr_norm_factors()

    def calculate_chr_norm_factors(self) -> None:
        """
        Calculate normalization factors for each chromosome.

        Uses the chromosomes specified during initialization to compute
        chromosome-specific normalization factors based on observed vs expected contacts.
        """
        for chr_name in self.chr_names:
            current_obs_total = self.background_contact_dict[chr_name].sum()
            current_max_dist_bins = self.background_contact_dict[chr_name].shape[0]

            current_exp_total = self.avg_background_dist[:current_max_dist_bins].dot(
                self.distance_counts_dict[chr_name]
            )

            self.chr_norm_factors_dict[chr_name] = np.array(
                current_exp_total / current_obs_total
            )

    def apply_OE_normalization(self, chr_name: str) -> sp.csr_array:
        """
        Apply observed/expected (O/E) normalization to a contact map.

        Loads the raw contact map for the specified chromosome from the HiC loader
        and applies O/E normalization using the computed background distribution.

        Parameters
        ----------
        chr_name : str
            Chromosome name (e.g., 'chr1')

        Returns
        -------
        sp.csr_array
            O/E normalized sparse matrix

        Raises
        ------
        ValueError
            If chr_name is not in the list of chromosomes used during initialization
        """
        if chr_name not in self.chr_names:
            raise ValueError(f"Chromosome '{chr_name}' not in initialized chromosome list: {self.chr_names}")

        # Load raw contact map
        raw_contact_map = self.hic_loader.load_contact_map(
            chr_name, self.resolution, data_type=self.data_type, norm_type=self.norm_type
        )

        OE_normed_mat = sp.csr_array(raw_contact_map)
        max_dist = raw_contact_map.shape[0]
        avg_background_dist_nonzero_bool = self.avg_background_dist != 0

        for idx in range(max_dist):
            current_max_dist = max_dist - idx
            current_avg_background_dist_nonzero_bool = \
                avg_background_dist_nonzero_bool[:current_max_dist]

            # All the nonzero avg background distances within the current max distance
            current_avg_background_nonzero_dist = np.nonzero(
                current_avg_background_dist_nonzero_bool
            )[0]

            current_row_to_next_sparse_idx = OE_normed_mat.indptr[idx:idx+2]
            current_row_to_next_sparse_slice = slice(*current_row_to_next_sparse_idx)

            # Convert column indices to distance from diagonal (upper triangular)
            col_dist = OE_normed_mat.indices[current_row_to_next_sparse_slice] - idx

            # Identify distances in both sparse row and avg background distribution
            _, comm_idx_1, comm_idx_2 = np.intersect1d(
                col_dist,
                current_avg_background_nonzero_dist,
                assume_unique=True,
                return_indices=True
            )

            row_values = OE_normed_mat.data[current_row_to_next_sparse_slice]
            row_values[comm_idx_1] /= self.avg_background_dist[:current_max_dist][comm_idx_2]

            # Zero out remaining sparse row elements
            zero_col_bool = np.zeros_like(col_dist, dtype=bool)
            zero_col_bool[comm_idx_1] = True
            zero_col_bool = ~zero_col_bool
            row_values[zero_col_bool] = 0

            # Replace the values in the sparse matrix
            OE_normed_mat.data[current_row_to_next_sparse_slice] = row_values

        # Symmetrize the matrix
        diag = OE_normed_mat.diagonal()
        OE_normed_mat += OE_normed_mat.T
        OE_normed_mat.setdiag(diag)

        OE_normed_mat *= self.chr_norm_factors_dict[chr_name]
        OE_normed_mat.eliminate_zeros()

        return OE_normed_mat


def _serialize_background_normalizer(normalizer: BackgroundNormalizer) -> Dict:
    """
    Serialize a BackgroundNormalizer to a dictionary for HDF5 storage.

    Parameters
    ----------
    normalizer : BackgroundNormalizer
        Background normalizer instance to serialize

    Returns
    -------
    Dict
        Dictionary containing all computed normalization data and parameters
    """
    return {
        'resolution': normalizer.resolution,
        'chr_names': normalizer.chr_names,
        'data_type': normalizer.data_type,
        'norm_type': normalizer.norm_type,
        'smoothing_cutoff': normalizer.smoothing_cutoff,
        'background_contact_dict': normalizer.background_contact_dict,
        'distance_counts_dict': normalizer.distance_counts_dict,
        'complete_background_contact': normalizer.complete_background_contact,
        'complete_distance_counts': normalizer.complete_distance_counts,
        'avg_background_dist': normalizer.avg_background_dist,
        'chr_norm_factors_dict': normalizer.chr_norm_factors_dict
    }


def _deserialize_background_normalizer(normalizer_dict: Dict, hic_loader: HiCDataLoader) -> BackgroundNormalizer:
    """
    Reconstruct a BackgroundNormalizer from serialized dictionary.

    Parameters
    ----------
    normalizer_dict : Dict
        Serialized normalizer data from HDF5 file
    hic_loader : HiCDataLoader
        HiCDataLoader instance to attach to the normalizer

    Returns
    -------
    BackgroundNormalizer
        Reconstructed BackgroundNormalizer instance with all data restored
    """
    # Create new normalizer instance (does not compute background yet)
    normalizer = BackgroundNormalizer(
        hic_loader=hic_loader,
        resolution=normalizer_dict['resolution'],
        chr_names=normalizer_dict['chr_names'],
        data_type=normalizer_dict['data_type'],
        norm_type=normalizer_dict['norm_type'],
        smoothing_cutoff=normalizer_dict['smoothing_cutoff']
    )

    # Restore all computed data
    normalizer.background_contact_dict = normalizer_dict['background_contact_dict']
    normalizer.distance_counts_dict = normalizer_dict['distance_counts_dict']
    normalizer.complete_background_contact = normalizer_dict['complete_background_contact']
    normalizer.complete_distance_counts = normalizer_dict['complete_distance_counts']
    normalizer.avg_background_dist = normalizer_dict['avg_background_dist']
    normalizer.chr_norm_factors_dict = normalizer_dict['chr_norm_factors_dict']

    return normalizer


class LowCoverageFilter:
    """Filters low-coverage loci from contact matrices."""

    @staticmethod
    def filter_low_coverage(input_mat: sp.csr_matrix,
                           include_bool: Optional[np.ndarray] = None,
                           cutoff: Optional[float] = None) -> Tuple:
        """
        Filter low-coverage loci from O/E normalized contact matrix.

        Parameters
        ----------
        input_mat : sp.csr_matrix
            Input O/E normalized contact matrix
        include_bool : np.ndarray, optional
            Boolean array indicating which loci to include
        cutoff : float, optional
            Cutoff threshold for filtering

        Returns
        -------
        tuple
            (cutoff, filtered_matrix, include_bool, include_idx)
        """
        # Compute average O/E for each locus
        current_mean_contacts = input_mat.mean(axis=0)

        # First run - calculate cutoff
        if cutoff is None:
            # Bin between 0 to 3
            counts, bin_edges = np.histogram(
                current_mean_contacts,
                bins=np.linspace(0, 3, 51)
            )
            bin_centers = (bin_edges[1:] + bin_edges[:-1]) / 2

            # Limit histogram to <2 avg O/E
            temp_counts = np.append([0], counts[bin_centers < 2])

            # Calculate gradient sign
            grad_sign = np.sign(temp_counts[1:] - temp_counts[:-1])

            # Compute change in sign between 3 consecutive bins
            grad_sign_switch = grad_sign[1:] - grad_sign[:-1]

            # Find peaks (slope upward then downward)
            peak_idxes = np.where(grad_sign_switch == -2)[0]

            # Set minimum peak height to 1% of total loci
            peak_idxes = peak_idxes[
                counts[peak_idxes] > int(np.ceil(current_mean_contacts.shape[0] * 0.01))
            ]

            # Single peak case
            if peak_idxes.shape[0] < 2:
                cutoff_idx = np.argmin(counts[0:peak_idxes[0]+1])
            # Multiple peaks case
            else:
                cutoff_idx = np.argmin(
                    counts[peak_idxes[0]:peak_idxes[1:][np.argmax(counts[peak_idxes[1:]])]+1]
                ) + peak_idxes[0]

            cutoff = bin_centers[cutoff_idx]

        if cutoff > 0.5:
            cutoff = 0.5

        current_include_bool = current_mean_contacts > cutoff
        current_include_idx = np.nonzero(current_include_bool)[0]
        current_include_slice = np.ix_(current_include_bool, current_include_bool)

        # Initial O/E matrix
        if include_bool is None:
            include_bool = current_include_bool.copy()
            include_idx = current_include_idx.copy()
        # Update existing include_bool and include_idx
        else:
            include_idx = np.nonzero(include_bool)[0]
            include_bool[include_idx[~current_include_bool]] = False
            include_idx = np.nonzero(include_bool)[0]

        return cutoff, input_mat[current_include_slice].copy(), include_bool, include_idx


class EigenDecomposer:
    """
    Performs robust eigenvalue decomposition with automatic error recovery.

    This class handles spectral decomposition of normalized contact matrices
    with adaptive tolerance adjustment and convergence checking.
    """

    def __init__(self, laplacian_mat: sp.csr_matrix, sqrt_deg: np.ndarray, verbose: bool = False):
        """
        Initialize the eigen decomposer.

        Parameters
        ----------
        laplacian_mat : sp.csr_matrix
            Laplacian matrix for decomposition
        sqrt_deg : np.ndarray
            Square root of the degree of the OE matrix
        verbose : bool, optional
            Enable verbose output for decomposition progress (default: False)
        """
        self.res_errors = None
        self.decompose_fail = False
        self.laplacian_mat = laplacian_mat
        self.sqrt_deg = sqrt_deg
        self.sqrt_deg /= np.linalg.norm(self.sqrt_deg)
        self.min_tol = 10 ** np.floor(
            np.log10(np.finfo(laplacian_mat.dtype).eps * 100)
        )
        self.results = None
        self.verbose = verbose

    def _warning_callback(self, *args) -> None:
        """Callback to capture eigendecomposition warnings."""
        if "Exited postprocessing with accuracies" in args[0].args[0]:
            self.res_errors = np.array(
                args[0].args[0].strip().split('[')[1].split(']')[0].split(),
                dtype=np.float64
            )
            self.decompose_fail = True

    def decompose(self,
                 tol: float = 1e-5,
                 max_retry: int = 6,
                 init_max_iter: int = 20,
                 init_eigvects: Optional[np.ndarray] = None) -> Tuple:
        """
        Perform eigenvalue decomposition with retry logic.

        Parameters
        ----------
        tol : float, optional
            Tolerance for convergence (default: 1e-5)
        max_retry : int, optional
            Maximum number of retry attempts (default: 6)
        init_max_iter : int, optional
            Initial maximum iterations (default: 20)
        init_eigvects : np.ndarray, optional
            Initial eigenvector guess

        Returns
        -------
        tuple
            (results, converged_status)
            results: (eigenvalues, eigenvectors, lambda_history, residual_norms_history)
            converged_status: bool indicating convergence success
        """
        restarted_status = False
        max_iter = init_max_iter
        init_tol = tol

        with warnings.catch_warnings():
            warnings.showwarning = self._warning_callback

            while True:
                self.decompose_fail = False

                if init_eigvects is None:
                    init_eigvects = (np.random.rand(self.laplacian_mat.shape[0], 11) - 0.5) * 2
                    init_eigvects[:, 0] = self.sqrt_deg
                    init_eigvects /= np.linalg.norm(init_eigvects, axis=0)

                self.results = sp.linalg.lobpcg(
                    self.laplacian_mat,
                    init_eigvects,
                    tol=tol,
                    maxiter=max_iter,
                    retLambdaHistory=True,
                    retResidualNormsHistory=True,
                    largest=False
                )

                if self.decompose_fail:
                    target_tols = 10 ** np.floor(
                        np.log10(np.abs(self.results[0][1:] - self.results[0][:-1]) * 0.1)
                    )
                    target_tols[target_tols < self.min_tol] = self.min_tol

                    tol_status = self.res_errors[1:] < target_tols

                    if tol_status.all():
                        return self.results, True

                    target_tol = target_tols[~tol_status].min()

                    if max_retry == 1:
                        if (target_tol > 1e-10) and not restarted_status:
                            restarted_status = True
                            max_retry = 6
                            max_iter = init_max_iter
                            init_eigvects = None
                            if self.verbose:
                                print("Reset and rerun")
                            continue
                        else:
                            if self.verbose:
                                print("Eigenvalues not converged")
                            return self.results, False

                    if target_tol > init_tol:
                        target_tol = init_tol

                    init_eigvects = self.results[1].copy()
                    init_eigvects[:, 0] = self.sqrt_deg
                    random_perturb = (np.random.rand(
                        self.laplacian_mat.shape[0],
                        tol_status.sum()
                    ) - 0.5) * 2 * 10 ** np.floor(
                        np.log10(np.abs(self.results[1][:, 1:][:, tol_status]) * 0.1)
                    )
                    init_eigvects[:, 1:][:, tol_status] = \
                        random_perturb + self.results[1][:, 1:][:, tol_status]
                    init_eigvects /= np.linalg.norm(init_eigvects, axis=0)

                    max_retry -= 1
                    max_iter *= 2
                    tol = target_tol

                    if self.verbose:
                        print(f"Eigen-decomposition: Remaining Tries: {max_retry} - "
                              f"New Target Tol: {target_tol:.0E} - New Max iter: {max_iter}")

                else:
                    return self.results, True


class InterABScoreCalculator:
    """Calculates inter-AB compartment contact scores."""

    @staticmethod
    def calculate_inter_AB_score(eigvect: np.ndarray,
                                eigval: float,
                                OE_normed_mat: sp.csr_matrix) -> float:
        """
        Calculate the inter-AB compartment contact score.

        Parameters
        ----------
        eigvect : np.ndarray
            Eigenvector (will be normalized internally)
        eigval : float
            Eigenvalue corresponding to the eigenvector
        OE_normed_mat : sp.csr_matrix
            O/E normalized contact matrix

        Returns
        -------
        float
            Inter-AB score normalized by eigenvalue
        """
        # Normalize eigenvector by column sums
        deg = np.asarray(OE_normed_mat.sum(axis=0)).flatten()
        normed_eigvect = eigvect / np.sqrt(deg)

        # Normalize eigenvalue by matrix sum
        normed_eigval = eigval / OE_normed_mat.sum()

        compartment_bools = [
            normed_eigvect > 0,
            normed_eigvect < 0
        ]

        # Return 0 if either compartment is empty
        if (compartment_bools[0].sum() == 0) or (compartment_bools[1].sum() == 0):
            return 0.0

        compartments = [
            normed_eigvect[compartment_bools[0]],
            normed_eigvect[compartment_bools[1]]
        ]

        # Calculate inter-compartment contact score
        edge_weights_coo = OE_normed_mat[
            compartment_bools[0], :
        ][:, compartment_bools[1]].tocoo()

        inter_AB_abs = (
            (compartments[0][edge_weights_coo.row] -
             compartments[1][edge_weights_coo.col]) ** 2 *
            edge_weights_coo.data
        ).sum() / 2

        raw_inter_AB_score = inter_AB_abs / edge_weights_coo.data.sum()

        # Normalize by eigenvalue
        inter_AB_score = raw_inter_AB_score / normed_eigval

        return inter_AB_score


class CompartmentAssigner:
    """Assigns A-B chromosomal compartments from Hi-C data using spectral analysis."""

    def __init__(self):
        """Initialize the compartment assigner."""
        pass

    @staticmethod
    def set_AB_orientation(eigenvect: np.ndarray,
                          OE_normed_diag: np.ndarray,
                          assigned_AB_compartment: np.ndarray,
                          non_zero_not_included_bool: np.ndarray) -> np.ndarray:
        """
        Set the orientation of A-B compartments based on diagonal enrichment.

        Parameters
        ----------
        eigenvect : np.ndarray
            Selected eigenvector
        OE_normed_diag : np.ndarray
            Diagonal of O/E normalized matrix
        assigned_AB_compartment : np.ndarray
            Predicted A-B compartment vector
        non_zero_not_included_bool : np.ndarray
            Boolean array for excluded loci

        Returns
        -------
        np.ndarray
            Oriented and normalized A-B compartment prediction
        """
        temp_pred_A = eigenvect > 0
        temp_pred_B = eigenvect < 0

        if OE_normed_diag[temp_pred_A].mean() < OE_normed_diag[temp_pred_B].mean():
            assigned_AB_compartment *= -1

        min_B_compartment = -np.abs(assigned_AB_compartment[assigned_AB_compartment < 0]).min()

        assigned_AB_compartment[non_zero_not_included_bool] = min_B_compartment
        assigned_AB_compartment /= np.linalg.norm(assigned_AB_compartment)

        return assigned_AB_compartment

    @staticmethod
    def select_eigenvector(OE_normed_mat_nonzero: sp.csr_matrix,
                          eigvals: np.ndarray,
                          eigenvects: np.ndarray,
                          num_components: int = 10) -> Tuple[int, float, float]:
        """
        Select the best eigenvector for compartment prediction.

        Uses eigenvector selection algorithm v6 that evaluates inter-compartment contacts
        weighted by eigenvalue significance.

        Parameters
        ----------
        OE_normed_mat_nonzero : sp.csr_matrix
            Filtered O/E normalized contact matrix
        eigvals : np.ndarray
            Eigenvalues from decomposition
        eigenvects : np.ndarray
            Eigenvectors from decomposition (as rows)
        num_components : int, optional
            Number of eigenvectors to evaluate (default: 10)

        Returns
        -------
        tuple
            (selected_eigenvector_index, modified_inter_eigval_score, unmodified_inter_AB_score)
        """
        rel_eigvals = eigvals / eigvals[1]

        final_modified_score = 0
        final_unmodified_score = 0
        final_pc_idx = None

        # Evaluate the 2nd eigenvectors through num_components+1 (0-indexed)
        for idx in range(1, num_components + 1):
            # Calculate inter-AB score using InterABScoreCalculator
            inter_AB_score = InterABScoreCalculator.calculate_inter_AB_score(
                eigenvects[idx], eigvals[idx], OE_normed_mat_nonzero
            )

            # Skip if score is 0 (indicates empty compartment)
            if inter_AB_score == 0.0:
                continue

            # Further weight by relative eigenvalue significance (modified score)
            modified_score = inter_AB_score / rel_eigvals[idx]

            if modified_score > final_modified_score:
                final_modified_score = modified_score
                final_unmodified_score = inter_AB_score
                final_pc_idx = idx

        return final_pc_idx, final_modified_score, final_unmodified_score


class HiCSCA:
    """
    Complete pipeline for A-B compartment prediction from Hi-C data.

    This class orchestrates the entire workflow from loading Hi-C data
    to producing compartment predictions.
    """

    def __init__(self, hic_file_path: Optional[str] = None,
                 chr_names: Optional[List[str]] = None,
                 resolutions: Optional[List[int]] = None,
                 chr_length_dict: Optional[Dict[str, int]] = None,
                 data_type: str = "observed",
                 norm_type: str = "NONE",
                 smoothing_cutoff: int = 400):
        """
        Initialize the HiC-SCA pipeline.

        Parameters
        ----------
        hic_file_path : str, optional
            Path to the .hic file. If None, chr_names, resolutions, and chr_length_dict
            must be provided.
        chr_names : list of str, optional
            List of chromosome names to process. If None and hic_file_path is provided,
            uses autosomal chromosomes from .hic file. Required if hic_file_path is None.
        resolutions : list of int, optional
            List of resolutions to compute. If None and hic_file_path is provided,
            uses all available resolutions in the .hic file. Required if hic_file_path is None.
        chr_length_dict : dict, optional
            Dictionary mapping chromosome names to lengths in bp. If None and hic_file_path
            is provided, extracted from .hic file. Required if hic_file_path is None.
        data_type : str, optional
            Type of data to retrieve from hic_loader. Must be "observed" or "oe" (default: "observed").
            If "oe", the data is already O/E normalized and background normalization is skipped.
        norm_type : str, optional
            Normalization type for hic_loader (default: "NONE")
        smoothing_cutoff : int, optional
            Cutoff threshold for smoothing background contacts (default: 400).
            Only used when data_type is "observed".

        Raises
        ------
        ValueError
            If data_type is not "observed" or "oe", or if required parameters are missing
            when hic_file_path is None
        """
        # Validate data_type
        if data_type not in ["observed", "oe"]:
            raise ValueError(
                f"data_type must be 'observed' or 'oe', got '{data_type}'"
            )

        # Handle initialization with or without .hic file
        if hic_file_path is not None:
            # Initialize with .hic file
            self.hic_loader = HiCDataLoader(hic_file_path)

            if chr_names is None:
                self.chr_names = self.hic_loader.autosomal_chr_names
            else:
                self.chr_names = chr_names

            if resolutions is None:
                self.resolutions = self.hic_loader.resolutions
            else:
                # Validate that requested resolutions are available
                available_resolutions = set(self.hic_loader.resolutions)
                for res in resolutions:
                    if res not in available_resolutions:
                        raise ValueError(
                            f"Resolution {res} not available in .hic file. "
                            f"Available resolutions: {self.hic_loader.resolutions}"
                        )
                self.resolutions = resolutions

            # Copy chr_length_dict from hic_loader
            self.chr_length_dict = self.hic_loader.chr_length_dict
        else:
            # Initialize without .hic file (e.g., from HDF5)
            if chr_names is None or resolutions is None or chr_length_dict is None:
                raise ValueError(
                    "When hic_file_path is None, chr_names, resolutions, and "
                    "chr_length_dict must all be provided"
                )

            self.hic_loader = None
            self.chr_names = chr_names
            self.resolutions = resolutions
            self.chr_length_dict = chr_length_dict

        self.data_type = data_type
        self.norm_type = norm_type
        self.smoothing_cutoff = smoothing_cutoff
        self.normalizers = {}  # Resolution -> BackgroundNormalizer
        self._background_computed = set()  # Track which resolutions have background computed
        self.results = {}  # Store all results: {resolution: {chr_name: result_dict}}

    @classmethod
    def from_hdf5(cls, hdf5_path: str, hic_file_path: Optional[str] = None) -> 'HiCSCA':
        """
        Reconstruct HiCSCA instance from saved HDF5 file.

        This method loads a previously saved HiCSCA analysis and reconstructs the
        complete instance with all results and background normalizations.

        Parameters
        ----------
        hdf5_path : str
            Path to saved HDF5 file
        hic_file_path : str, optional
            Path to .hic file. If provided, enables processing of additional chromosomes
            or resolutions. If None, can only export existing results.

        Returns
        -------
        HiCSCA
            Reconstructed HiCSCA instance with all results and normalizers loaded

        Examples
        --------
        >>> from hicsca import HiCSCA
        >>> from hicsca.formats import generate_bed_file
        >>>
        >>> # Load from HDF5 for export only (no .hic file)
        >>> hicsca_inst = HiCSCA.from_hdf5("output.h5")
        >>> generate_bed_file(100000, "compartments.bed", hicsca_inst=hicsca_inst)
        >>>
        >>> # Load from HDF5 with .hic file (can process more data)
        >>> hicsca_inst = HiCSCA.from_hdf5("output.h5", hic_file_path="data.hic")
        >>> hicsca_inst.process_chromosome("chr1")  # Can process additional data
        >>>
        >>> # Access loaded results immediately
        >>> result = hicsca_inst.results[100000]['chr1']
        """
        # Load data from HDF5
        loaded_data = h5typer.load_data(hdf5_path)
        results = loaded_data['results']
        normalizers_data = loaded_data['normalizers']
        metadata = loaded_data['metadata']

        # Extract metadata
        chr_names = metadata['chr_names']
        resolutions = metadata['resolutions']
        chr_length_dict = metadata['chr_length_dict']
        data_type = metadata['data_type']
        norm_type = metadata['norm_type']
        smoothing_cutoff = metadata['smoothing_cutoff']

        # Create new HiCSCA instance
        instance = cls(
            hic_file_path=hic_file_path,
            chr_names=chr_names,
            resolutions=resolutions,
            chr_length_dict=chr_length_dict,
            data_type=data_type,
            norm_type=norm_type,
            smoothing_cutoff=smoothing_cutoff
        )

        # Restore results
        instance.results = results

        # Restore normalizers if present
        if normalizers_data is not None:
            for resolution, normalizer_dict in normalizers_data.items():
                instance.normalizers[resolution] = _deserialize_background_normalizer(
                    normalizer_dict, instance.hic_loader
                )
                instance._background_computed.add(resolution)

        return instance

    def compute_background_normalization(self, resolutions: Optional[List[int]] = None) -> None:
        """
        Compute genome-wide background normalization for specified resolutions.

        Skipped if data_type is "oe" (data already O/E normalized).

        Parameters
        ----------
        resolutions : list of int, optional
            List of resolutions to compute background for. If None, computes for
            all configured resolutions (default: None)
        """
        # Skip background normalization if data is already O/E normalized
        if self.data_type == "oe":
            return

        # Use all configured resolutions if not specified
        if resolutions is None:
            resolutions = self.resolutions

        for resolution in resolutions:
            if resolution not in self._background_computed:
                normalizer = BackgroundNormalizer(
                    self.hic_loader, resolution, self.chr_names,
                    data_type=self.data_type, norm_type=self.norm_type,
                    smoothing_cutoff=self.smoothing_cutoff
                )
                normalizer.calculate_genome_background()
                self.normalizers[resolution] = normalizer
                self._background_computed.add(resolution)

    def process_chromosome(self, chr_name: str, resolutions: Optional[List[int]] = None,
                          verbose: bool = True) -> None:
        """
        Process a single chromosome to predict A-B compartments at specified resolutions.

        Results are stored in self.results[resolution][chr_name].
        Automatically computes background normalization if not already done
        (unless data_type is "oe").

        Skips processing if a chromosome-resolution pair has already been processed
        (determined by the presence of 'Success' key in results).

        Parameters
        ----------
        chr_name : str
            Chromosome name (e.g., 'chr1')
        resolutions : list of int, optional
            List of resolutions in base pairs to process. If None, processes all
            configured resolutions (default: None)
        verbose : bool, optional
            Print progress messages (default: True)

        Raises
        ------
        RuntimeError
            If no .hic file is available

        Examples
        --------
        >>> # Process all configured resolutions for chr1
        >>> hicsca_inst.process_chromosome('chr1')
        >>>
        >>> # Process specific resolutions for chr1
        >>> hicsca_inst.process_chromosome('chr1', resolutions=[100000, 50000])
        >>>
        >>> # Process single resolution for chr1
        >>> hicsca_inst.process_chromosome('chr1', resolutions=[100000])
        """
        # Check if hic_loader is available
        if self.hic_loader is None:
            raise RuntimeError(
                "Cannot process chromosomes: No .hic file available."
            )

        # Use all configured resolutions if not specified
        if resolutions is None:
            resolutions = self.resolutions

        # Ensure background normalization is computed for needed resolutions
        if self.data_type == "observed":
            # Determine which resolutions need background normalization
            resolutions_to_compute = [r for r in resolutions if r not in self._background_computed]
            if resolutions_to_compute:
                if verbose:
                    print("Computing background normalization...")
                self.compute_background_normalization(resolutions=resolutions_to_compute)

        for resolution in resolutions:
            # Initialize resolution dict if needed
            if resolution not in self.results:
                self.results[resolution] = {}

            # Skip if already processed (Success key exists, regardless of True/False)
            if (chr_name in self.results[resolution] and
                'Success' in self.results[resolution][chr_name]):
                if verbose:
                    print(f"Skipping: {resolution} - {chr_name} (already processed)")
                continue

            # Process this chromosome-resolution pair
            if verbose:
                print(f"Processing: {resolution} - {chr_name}")

            result_dict = {}

            # Load contact map (with or without O/E normalization depending on data_type)
            if self.data_type == "oe":
                # Data is already O/E normalized, load directly
                OE_normed_mat = self.hic_loader.load_contact_map(
                    chr_name, resolution, data_type=self.data_type, norm_type=self.norm_type
                )
            else:
                # data_type is "observed", apply O/E normalization
                normalizer = self.normalizers[resolution]
                OE_normed_mat = normalizer.apply_OE_normalization(chr_name)

            # Initial filtering
            cutoff, OE_normed_mat_nonzero, include_bool, include_idx = \
                LowCoverageFilter.filter_low_coverage(OE_normed_mat, include_bool=None, cutoff=None)

            mean_contacts = OE_normed_mat.mean(axis=0)
            OE_normed_diag = OE_normed_mat.diagonal()
            del OE_normed_mat

            result_dict['cutoff'] = cutoff

            # Iterative filtering (up to 3 iterations)
            filter_iter = 1
            while filter_iter < 3:
                current_mean_contacts = OE_normed_mat_nonzero.mean(axis=0)

                if (current_mean_contacts <= cutoff).sum() > 0:
                    _, OE_normed_mat_nonzero, include_bool, include_idx = \
                        LowCoverageFilter.filter_low_coverage(
                            OE_normed_mat_nonzero, include_bool=include_bool, cutoff=cutoff
                        )
                    filter_iter += 1
                    if verbose:
                        print(f"Low-Coverage Filter: {resolution} - {chr_name} - Iter: {filter_iter}")
                else:
                    break

            # Create boolean for excluded non-zero loci
            non_zero_not_included_bool = mean_contacts > 0
            non_zero_not_included_bool[include_idx] = False

            # Prepare the laplacian matrix
            deg = np.asarray(OE_normed_mat_nonzero.sum(axis=0)).flatten()
            sqrt_deg = np.sqrt(deg)
            inv_sqrt_deg = 1.0 / sqrt_deg

            laplacian_mat = -inv_sqrt_deg[:,None] * OE_normed_mat_nonzero * inv_sqrt_deg[None,:]
            diag = laplacian_mat.diagonal()
            laplacian_mat.setdiag(diag + 1)

            # Perform eigendecomposition
            decomposer = EigenDecomposer(laplacian_mat, sqrt_deg, verbose=verbose)
            results, converged = decomposer.decompose(tol=1e-5, max_retry=6, init_max_iter=20)

            result_dict['Eig Converged'] = converged

            if not converged:
                result_dict['Success'] = False
                if verbose:
                    print(f"Failed: {resolution} - {chr_name} - Eigendecomposition did not converge")
                self.results[resolution][chr_name] = result_dict
                gc.collect()
                continue

            # Extract eigenvalues and eigenvectors
            eigvals = results[0]
            eigenvects_cols = results[1]

            # Convert eigenvectors to row-major format for easier indexing
            eigenvects = eigenvects_cols.T

            result_dict['eigvals'] = eigvals
            result_dict['eigenvects'] = eigenvects
            result_dict['OE_normed_diag'] = OE_normed_diag[include_bool]
            result_dict['non_zero_not_included_bool'] = non_zero_not_included_bool
            result_dict['include_bool'] = include_bool

            # Select best eigenvector
            assigner = CompartmentAssigner()
            selected_eig_idx, modified_inter_eigval_score, unmodified_inter_AB_score = assigner.select_eigenvector(
                OE_normed_mat_nonzero, eigvals, eigenvects, num_components=10
            )

            del OE_normed_mat_nonzero
            gc.collect()

            if selected_eig_idx is None:
                result_dict['Success'] = False
                if verbose:
                    print(f"Failed: {resolution} - {chr_name} - No valid eigenvector found")
                self.results[resolution][chr_name] = result_dict
                gc.collect()
                continue

            # Create full compartment prediction vector
            assigned_AB_compartment = np.zeros(include_bool.shape[0], dtype=np.float64)
            assigned_AB_compartment[include_idx] = eigenvects[selected_eig_idx]

            # Set A-B orientation
            assigned_AB_compartment = assigner.set_AB_orientation(
                eigenvects[selected_eig_idx],
                OE_normed_diag[include_bool],
                assigned_AB_compartment,
                non_zero_not_included_bool
            )

            result_dict['assigned_AB_compartment'] = assigned_AB_compartment
            result_dict['selected_eig_idx'] = selected_eig_idx
            result_dict['modified_inter_eigval_score'] = modified_inter_eigval_score
            result_dict['unmodified_inter_AB_score'] = unmodified_inter_AB_score
            result_dict['deg'] = deg
            result_dict['Success'] = True

            if verbose:
                print(f"Success: {resolution} - {chr_name} - Eig{selected_eig_idx} - "
                      f"Score: {modified_inter_eigval_score:.4f}")

            self.results[resolution][chr_name] = result_dict
            gc.collect()

    def process_all_chromosomes(self, resolutions: Optional[List[int]] = None,
                               verbose: bool = True) -> None:
        """
        Process all chromosomes at specified resolutions.

        Results are stored in self.results[resolution][chr_name].
        Automatically computes background normalization if not already done
        (unless data_type is "oe").

        Skips processing if a chromosome-resolution pair has already been processed
        (determined by the presence of 'Success' key in results).

        Parameters
        ----------
        resolutions : list of int, optional
            List of resolutions in base pairs to process. If None, processes all
            configured resolutions (default: None)
        verbose : bool, optional
            Print progress messages (default: True)

        Raises
        ------
        RuntimeError
            If no .hic file is available

        Examples
        --------
        >>> # Process all chromosomes at all configured resolutions
        >>> hicsca_inst.process_all_chromosomes()
        >>>
        >>> # Process all chromosomes at specific resolutions
        >>> hicsca_inst.process_all_chromosomes(resolutions=[100000, 50000])
        >>>
        >>> # Process all chromosomes at single resolution
        >>> hicsca_inst.process_all_chromosomes(resolutions=[100000])
        """
        # Check if hic_loader is available
        if self.hic_loader is None:
            raise RuntimeError(
                "Cannot process chromosomes: No .hic file available."
            )

        # Process each chromosome using process_chromosome method
        for chr_name in self.chr_names:
            self.process_chromosome(chr_name, resolutions=resolutions, verbose=verbose)

    def to_hdf5(self, output_path: str, update: bool = False):
        """
        Save HiCSCA instance to HDF5 file.

        Convenience wrapper for hicsca_formats.save_to_hdf5().

        Parameters
        ----------
        output_path : str
            Path to output HDF5 file
        update : bool, optional
            If True, update existing file. If False, overwrite (default: False)
        """
        from . import formats
        formats.save_to_hdf5(hicsca_inst=self, output_path=output_path, update=update)

    def to_bed(
        self,
        resolution: int,
        output_path: str,
        chr_names: Optional[list] = None,
        dataset_id: Optional[str] = None
    ):
        """
        Generate BED file for A-B compartments at specified resolution.

        Convenience wrapper for hicsca_formats.generate_bed_file().

        Parameters
        ----------
        resolution : int
            Resolution in base pairs
        output_path : str
            Path to output BED file
        chr_names : list, optional
            List of chromosome names to include. If None, uses all chromosomes
            from this HiCSCA instance
        dataset_id : str, optional
            Dataset identifier for multi-sample results
        """
        from . import formats
        formats.generate_bed_file(
            resolution,
            output_path,
            hicsca_inst=self,
            chr_names=chr_names,
            dataset_id=dataset_id
        )

    def to_bedgraph(
        self,
        resolution: int,
        output_path: str,
        chr_names: Optional[list] = None,
        dataset_id: Optional[str] = None,
        track_name: Optional[str] = None
    ):
        """
        Generate BedGraph file for A-B compartments at specified resolution.

        Convenience wrapper for hicsca_formats.generate_bedgraph_file().

        Parameters
        ----------
        resolution : int
            Resolution in base pairs
        output_path : str
            Path to output BedGraph file
        chr_names : list, optional
            List of chromosome names to include. If None, uses all chromosomes
            from this HiCSCA instance
        dataset_id : str, optional
            Dataset identifier for multi-sample results
        track_name : str, optional
            Custom track name for BedGraph header
        """
        from . import formats
        formats.generate_bedgraph_file(
            resolution,
            output_path,
            hicsca_inst=self,
            chr_names=chr_names,
            dataset_id=dataset_id,
            track_name=track_name
        )

    def to_excel(
        self,
        resolution: int,
        output_path: str,
        chr_names: Optional[list] = None,
    ):
        """
        Generate Excel file for A-B compartments at specified resolution.

        Convenience wrapper for hicsca_formats.generate_excel_file().

        Parameters
        ----------
        resolution : int
            Resolution in base pairs
        output_path : str
            Path to output Excel (.xlsx) file
        chr_names : list, optional
            List of chromosome names to include. If None, uses all chromosomes
            from this HiCSCA instance
        dataset_id : str, optional
            Dataset identifier for multi-sample results
        """
        from . import formats
        formats.generate_excel_file(
            resolution,
            output_path,
            hicsca_inst=self,
            chr_names=chr_names,
        )

    def plot_compartments(
        self,
        resolution: int,
        chr_names: Optional[list] = None,
        output_dir: Optional[str] = None,
        output_prefix: Optional[str] = None,
        display: bool = True,
        dpi: int = 300,
        figsize: tuple = (3.595, 2),
        show_legend: bool = True
    ) -> None:
        """
        Plot A-B compartment predictions for chromosomes at specified resolution.

        Supports both saving to files and displaying in Jupyter notebooks.

        Parameters
        ----------
        resolution : int
            Resolution in base pairs
        chr_names : list, optional
            List of chromosome names to plot. If None, plots all chromosomes
            from this HiCSCA instance (default: None)
        output_dir : str, optional
            Directory to save plot files. If None, plots are not saved (default: None)
        output_prefix : str, optional
            Prefix for output filenames. Pattern: {prefix}_{chr}_{resolution}bp.png
            If None, pattern is: {chr}_{resolution}bp.png (default: None)
        display : bool, optional
            Display plots inline in Jupyter notebooks (default: True).
            Set to False to save without displaying.
        dpi : int, optional
            Figure DPI (default: 300)
        figsize : tuple, optional
            Figure size in inches (width, height) (default: (3.595, 2))
        show_legend : bool, optional
            Whether to display legend for A and B compartments (default: True)

        Examples
        --------
        >>> # Display only (Jupyter notebook)
        >>> hicsca_inst.plot_compartments(100000)
        >>>
        >>> # Save and display
        >>> hicsca_inst.plot_compartments(100000, output_dir="plots",
        ...                               output_prefix="sample1")
        >>>
        >>> # Save only (no display)
        >>> hicsca_inst.plot_compartments(100000, output_dir="plots",
        ...                               output_prefix="sample1", display=False)
        >>>
        >>> # Specific chromosomes with custom settings
        >>> hicsca_inst.plot_compartments(100000, chr_names=['chr1', 'chr2'],
        ...                               dpi=600, figsize=(7.19, 4))
        """
        from . import formats
        import matplotlib.pyplot as plt
        import os

        # Use all chromosomes if not specified
        if chr_names is None:
            chr_names = self.chr_names

        # Check if resolution exists in results
        if resolution not in self.results:
            raise ValueError(f"No results available for resolution: {resolution} bp")

        for chr_name in chr_names:
            # Check if chromosome was processed
            if chr_name not in self.results[resolution]:
                continue

            result = self.results[resolution][chr_name]

            # Skip failed results
            if not result.get('Success', False):
                continue

            # Generate filename
            if output_prefix:
                filename = f"{output_prefix}_{chr_name}_{resolution}bp.png"
            else:
                filename = f"{chr_name}_{resolution}bp.png"

            # Determine save path
            save_path = None
            if output_dir is not None:
                save_path = os.path.join(output_dir, filename)

            # Plot compartment
            fig, _ = formats.plot_AB_compartment(
                result['assigned_AB_compartment'],
                output_path=save_path,
                chr_name=chr_name,
                resolution=resolution,
                dpi=dpi,
                figsize=figsize,
                show_legend=show_legend
            )

            # Close figure if display is disabled
            if not display:
                plt.close(fig)

    def plot_cross_resolution_mcc(
        self,
        chr_name: str = 'all',
        resolutions: Optional[List[int]] = None,
        chr_names: Optional[List[str]] = None,
        figsize: Tuple[float, float] = (2.8, 2.8),
        dpi: int = 300,
        background_alpha: float = 1,
        plot_colorbar: bool = True,
        save_path: Optional[str] = None
    ) -> Tuple:
        """
        Plot cross-resolution MCC correlation heatmap.

        This convenience method creates a CrossResolutionAnalyzer internally,
        performs the analysis, and generates the MCC correlation plot.

        Parameters
        ----------
        chr_name : str, optional
            Chromosome name to plot (default: 'all' for genome-wide)
        resolutions : List[int], optional
            List of resolutions to analyze (in bp). If None, uses all resolutions
            from this HiCSCA instance (default: None)
        chr_names : List[str], optional
            List of chromosome names to analyze. If None, uses all chromosomes
            from this HiCSCA instance (default: None)
        figsize : Tuple[float, float], optional
            Figure size in inches (default: (2.8, 2.8))
        dpi : int, optional
            Figure DPI (default: 300)
        background_alpha : float, optional
            Alpha value for figure backgrounds (0=transparent, 1=opaque) (default: 1)
        plot_colorbar : bool, optional
            Whether to generate colorbar figure (default: True)
        save_path : str, optional
            Path to save main figure (PNG/JPEG). If None, figure is not saved.
            If provided and plot_colorbar=True, colorbar is automatically saved
            as '{filename}_colorbar.{ext}'

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

        Examples
        --------
        >>> # Plot genome-wide cross-resolution MCC
        >>> fig, ax, cbar_fig, cbar_ax = hicsca_inst.plot_cross_resolution_mcc()
        >>>
        >>> # Plot specific chromosome
        >>> fig, ax, cbar_fig, cbar_ax = hicsca_inst.plot_cross_resolution_mcc(
        ...     chr_name='chr1'
        ... )
        >>>
        >>> # Save to file
        >>> fig, ax, cbar_fig, cbar_ax = hicsca_inst.plot_cross_resolution_mcc(
        ...     save_path='cross_res_mcc.png'
        ... )
        >>>
        >>> # Analyze specific resolutions only
        >>> fig, ax, cbar_fig, cbar_ax = hicsca_inst.plot_cross_resolution_mcc(
        ...     resolutions=[500000, 100000, 50000]
        ... )
        >>>
        >>> # Without colorbar and transparent background
        >>> fig, ax, _, _ = hicsca_inst.plot_cross_resolution_mcc(
        ...     plot_colorbar=False,
        ...     background_alpha=0
        ... )
        """
        from . import evals

        # Use instance defaults if not specified
        if resolutions is None:
            resolutions = self.resolutions
        if chr_names is None:
            chr_names = self.chr_names

        # Create and analyze
        analyzer = evals.CrossResolutionAnalyzer(
            results_dict=self.results,
            resolutions=resolutions,
            chr_names=chr_names
        )
        analyzer.analyze()

        # Generate plot
        return analyzer.plot_cross_resolution_mcc(
            chr_name=chr_name,
            figsize=figsize,
            dpi=dpi,
            background_alpha=background_alpha,
            plot_colorbar=plot_colorbar,
            save_path=save_path
        )
