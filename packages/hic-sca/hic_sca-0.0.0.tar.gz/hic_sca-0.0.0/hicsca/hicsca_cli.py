#!/usr/bin/env python3
"""
HiC-SCA Command-Line Interface

Command-line tool for running HiC-SCA analysis on Hi-C datasets and
generating output files (HDF5, plots).
"""

import argparse
import os
import sys
from pathlib import Path

from hicsca.hicsca import HiCSCA
from hicsca.evals import CrossResolutionAnalyzer


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="HiC-SCA: Hi-C Spectral Compartment Assignment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process new Hi-C data from .hic file
  hic-sca -f data.hic -r 100000 -p my_sample

  # Process with optional BED and BedGraph output
  hic-sca -f data.hic -r 100000 -p my_sample --bed --bedgraph

  # Process multiple resolutions and chromosomes
  hic-sca -f data.hic -r 100000 50000 25000 -c chr1 chr2 chr3 -p my_sample

  # Load HDF5 for export only (no .hic file needed)
  hic-sca --load-hdf5 results.h5 -p output --bed --bedgraph

  # Load HDF5 with .hic file to process additional data
  hic-sca --load-hdf5 results.h5 -f data.hic -r 100000 -c chr1 chr2 -p sample

  # Process all resolutions with verbose output
  hic-sca -f data.hic -p my_sample -v -o results/

Note: Either -f or --load-hdf5 (or both) must be provided.
        """
    )

    parser.add_argument(
        '-f', '--hic-file',
        type=str,
        required=False,
        default=None,
        help='Path to input .hic file. Required unless --load-hdf5 is used. '
             'Can be combined with --load-hdf5 to enable processing additional data.'
    )

    parser.add_argument(
        '-r', '--resolutions',
        type=int,
        nargs='+',
        default=None,
        help='Space-separated list of resolutions in base pairs '
             '(default: auto-detect all available resolutions)'
    )

    parser.add_argument(
        '-p', '--output-prefix',
        type=str,
        required=True,
        help='Prefix for output files (required)'
    )

    parser.add_argument(
        '-o', '--output-dir',
        type=str,
        default='.',
        help='Output directory (default: current directory)'
    )

    parser.add_argument(
        '-c', '--chromosomes',
        type=str,
        nargs='+',
        default=None,
        help='Space-separated list of chromosome names '
             '(default: all autosomal chromosomes)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    parser.add_argument(
        '--load-hdf5',
        type=str,
        default=None,
        help='Load existing HDF5 results file. Use alone for export only, '
             'or combine with -f to enable processing additional chromosomes/resolutions.'
    )

    parser.add_argument(
        '--bed',
        action='store_true',
        help='Generate BED files for each resolution (optional)'
    )

    parser.add_argument(
        '--bedgraph',
        action='store_true',
        help='Generate BedGraph files for each resolution (optional)'
    )

    return parser.parse_args()


def main():
    """Main CLI entry point."""
    args = parse_arguments()

    # Validate input arguments
    if args.load_hdf5 is None and args.hic_file is None:
        print("Error: Must provide either --load-hdf5 or -f/--hic-file", file=sys.stderr)
        sys.exit(1)

    # Validate HDF5 file exists if provided
    if args.load_hdf5 and not os.path.exists(args.load_hdf5):
        print(f"Error: HDF5 file not found: {args.load_hdf5}", file=sys.stderr)
        sys.exit(1)

    # Validate .hic file exists if provided
    if args.hic_file and not os.path.exists(args.hic_file):
        print(f"Error: Hi-C file not found: {args.hic_file}", file=sys.stderr)
        sys.exit(1)

    # Create output directory if it doesn't exist
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Print configuration
    print("=" * 70)
    print("HiC-SCA: Hi-C Spectral Compartment Assignment")
    print("=" * 70)
    if args.load_hdf5:
        print(f"Load HDF5:        {args.load_hdf5}")
        if args.hic_file:
            print(f"Update .hic path: {args.hic_file}")
    else:
        print(f"Input file:       {args.hic_file}")
    print(f"Resolutions:      {args.resolutions if args.resolutions else 'auto-detect'}")
    print(f"Chromosomes:      {args.chromosomes if args.chromosomes else 'all autosomal'}")
    print(f"Output prefix:    {args.output_prefix}")
    print(f"Output directory: {output_dir.absolute()}")
    print(f"Verbose:          {args.verbose}")
    print(f"Generate BED:     {args.bed}")
    print(f"Generate BedGraph: {args.bedgraph}")
    print("=" * 70)
    print()

    # Initialize or load HiCSCA
    if args.load_hdf5:
        print(f"Loading HiC-SCA results from {args.load_hdf5}...")
        try:
            hicsca_inst = HiCSCA.from_hdf5(
                args.load_hdf5,
                hic_file_path=args.hic_file
            )
        except Exception as e:
            print(f"Error loading HDF5: {e}", file=sys.stderr)
            sys.exit(1)

        # Apply resolution filter if provided
        if args.resolutions:
            # Filter to only requested resolutions
            available_resolutions = [r for r in args.resolutions if r in hicsca_inst.resolutions]
            if not available_resolutions:
                print(f"Error: None of the requested resolutions {args.resolutions} found in HDF5 file", file=sys.stderr)
                sys.exit(1)
            hicsca_inst.resolutions = available_resolutions

        # Apply chromosome filter if provided
        if args.chromosomes:
            # Filter to only requested chromosomes
            available_chromosomes = [c for c in args.chromosomes if c in hicsca_inst.chr_names]
            if not available_chromosomes:
                print(f"Error: None of the requested chromosomes {args.chromosomes} found in HDF5 file", file=sys.stderr)
                sys.exit(1)
            hicsca_inst.chr_names = available_chromosomes
    else:
        print("Initializing HiC-SCA pipeline...")
        try:
            hicsca_inst = HiCSCA(
                hic_file_path=args.hic_file,
                chr_names=args.chromosomes,
                resolutions=args.resolutions,
                norm_type="NONE",
                smoothing_cutoff=400
            )
        except Exception as e:
            print(f"Error initializing HiC-SCA: {e}", file=sys.stderr)
            sys.exit(1)

    print(f"Resolutions: {hicsca_inst.resolutions}")
    print(f"Chromosomes: {hicsca_inst.chr_names}")
    print()

    # Process all chromosomes (only if hic_loader available)
    if hicsca_inst.hic_loader is not None:
        print("Processing all chromosomes...")
        try:
            hicsca_inst.process_all_chromosomes(verbose=args.verbose)
        except Exception as e:
            print(f"Error processing chromosomes: {e}", file=sys.stderr)
            sys.exit(1)

        print()
        print("=" * 70)
        print("Processing complete!")
        print("=" * 70)
        print()
    else:
        print("Skipping processing (loaded from HDF5 without .hic file)")
        print()

    # Save HDF5 results (only if hic_loader available)
    if hicsca_inst.hic_loader is not None:
        hdf5_path = output_dir / f"{args.output_prefix}_results.h5"
        print(f"Saving results to HDF5: {hdf5_path}")
        try:
            hicsca_inst.to_hdf5(str(hdf5_path))
            print(f"  ✓ Saved: {hdf5_path}")
        except Exception as e:
            print(f"  ✗ Error saving HDF5: {e}", file=sys.stderr)

        print()

    # Generate Excel files (mandatory)
    print("Generating Excel files...")
    excel_files = []
    for resolution in hicsca_inst.resolutions:
        excel_path = output_dir / f"{args.output_prefix}_{resolution}bp.xlsx"
        try:
            hicsca_inst.to_excel(resolution, str(excel_path))
            print(f"  ✓ Saved: {excel_path}")
            excel_files.append(excel_path)
        except Exception as e:
            print(f"  ✗ Error generating Excel for {resolution}bp: {e}", file=sys.stderr)

    print()

    # Generate BED files (optional)
    bed_files = []
    if args.bed:
        print("Generating BED files...")
        for resolution in hicsca_inst.resolutions:
            bed_path = output_dir / f"{args.output_prefix}_{resolution}bp.bed"
            try:
                hicsca_inst.to_bed(resolution, str(bed_path))
                print(f"  ✓ Saved: {bed_path}")
                bed_files.append(bed_path)
            except Exception as e:
                print(f"  ✗ Error generating BED for {resolution}bp: {e}", file=sys.stderr)
        print()

    # Generate BedGraph files (optional)
    bedgraph_files = []
    if args.bedgraph:
        print("Generating BedGraph files...")
        for resolution in hicsca_inst.resolutions:
            bedgraph_path = output_dir / f"{args.output_prefix}_{resolution}bp.bedgraph"
            try:
                hicsca_inst.to_bedgraph(resolution, str(bedgraph_path))
                print(f"  ✓ Saved: {bedgraph_path}")
                bedgraph_files.append(bedgraph_path)
            except Exception as e:
                print(f"  ✗ Error generating BedGraph for {resolution}bp: {e}", file=sys.stderr)
        print()

    # Generate cross-resolution MCC plot if multiple resolutions
    if len(hicsca_inst.resolutions) > 1:
        print("Generating cross-resolution MCC analysis plot...")
        try:
            analyzer = CrossResolutionAnalyzer(
                results_dict=hicsca_inst.results,
                resolutions=hicsca_inst.resolutions,
                chr_names=hicsca_inst.chr_names
            )
            analyzer.analyze()

            cross_res_plot_path = output_dir / f"{args.output_prefix}_cross_resolution_mcc.png"
            fig, ax, colorbar_fig, colorbar_ax = analyzer.plot_cross_resolution_mcc(
                chr_name='all',
                save_path=str(cross_res_plot_path)
            )
            print(f"  ✓ Saved: {cross_res_plot_path}")
            if colorbar_fig is not None:
                colorbar_path = output_dir / f"{args.output_prefix}_cross_resolution_mcc_colorbar.png"
                print(f"  ✓ Saved: {colorbar_path}")
        except Exception as e:
            print(f"  ✗ Error generating cross-resolution plot: {e}", file=sys.stderr)
        print()

    # Generate A-B compartment plots
    print("Generating A-B compartment plots...")
    total_plots = 0

    for resolution in hicsca_inst.resolutions:
        try:
            hicsca_inst.plot_compartments(
                resolution=resolution,
                output_dir=str(output_dir),
                output_prefix=args.output_prefix,
                display=False  # Save only, don't display
            )
            # Count successful plots for this resolution
            successful_chrs = sum(
                1 for chr_name in hicsca_inst.chr_names
                if hicsca_inst.results[resolution][chr_name].get('Success', False)
            )
            total_plots += successful_chrs

            if args.verbose:
                for chr_name in hicsca_inst.chr_names:
                    result = hicsca_inst.results[resolution][chr_name]
                    plot_filename = f"{args.output_prefix}_{chr_name}_{resolution}bp.png"
                    if result.get('Success', False):
                        print(f"  ✓ {plot_filename}")
                    else:
                        print(f"  ⊘ Skipped {chr_name} at {resolution}bp (processing failed)")
        except Exception as e:
            print(f"  ✗ Error plotting resolution {resolution}bp: {e}", file=sys.stderr)

    print(f"  Generated {total_plots} plots")
    print()

    # Print summary
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"Resolutions processed: {len(hicsca_inst.resolutions)}")
    print(f"Chromosomes processed: {len(hicsca_inst.chr_names)}")
    print()
    print("Output files:")
    if hicsca_inst.hic_loader is not None:
        hdf5_path = output_dir / f"{args.output_prefix}_results.h5"
        print(f"  HDF5 results:")
        print(f"    - {hdf5_path}")
        print()
    print(f"  Excel files: {len(excel_files)}")
    for excel_file in excel_files:
        print(f"    - {excel_file}")
    if args.bed:
        print()
        print(f"  BED files: {len(bed_files)}")
        for bed_file in bed_files:
            print(f"    - {bed_file}")
    if args.bedgraph:
        print()
        print(f"  BedGraph files: {len(bedgraph_files)}")
        for bedgraph_file in bedgraph_files:
            print(f"    - {bedgraph_file}")
    print()
    print(f"  A-B compartment plots: {total_plots}")
    if total_plots > 0:
        print(f"    (in {output_dir}/)")
    if len(hicsca_inst.resolutions) > 1:
        cross_res_plot_path = output_dir / f"{args.output_prefix}_cross_resolution_mcc.png"
        cross_res_colorbar_path = output_dir / f"{args.output_prefix}_cross_resolution_mcc_colorbar.png"
        print()
        print(f"  Cross-resolution analysis:")
        print(f"    - {cross_res_plot_path}")
        print(f"    - {cross_res_colorbar_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()
