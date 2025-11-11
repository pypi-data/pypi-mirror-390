import argparse
from argparse import ArgumentParser, RawTextHelpFormatter
import textwrap
import os
import logging
import shutil
import glob
import subprocess
from datetime import datetime
from plasmidhub import preprocessing, ani, filtering, abricate
from pathlib import Path
import contextlib

@contextlib.contextmanager
def change_dir(destination: Path):
    # Always resolve to absolute path
    abs_destination = destination.resolve()
    prev_cwd = Path.cwd()
    os.chdir(abs_destination)
    try:
        yield
    finally:
        os.chdir(prev_cwd)

VERSION = "1.0.1"

# Setup logging
def setup_logging(log_file_path):
    """
    Sets up logging to both file and console.

    Args:
        log_file_path (str): The path to the log file.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # File handler with timestamp
    file_formatter = logging.Formatter('%(asctime)s - %(message)s')
    fh = logging.FileHandler(log_file_path)
    fh.setFormatter(file_formatter)
    logger.addHandler(fh)

    # Stream handler (terminal) without timestamp
    stream_formatter = logging.Formatter('%(message)s')
    sh = logging.StreamHandler()
    sh.setFormatter(stream_formatter)
    logger.addHandler(sh)

    return logger

def write_versions_txt(output_dir):
    """
    Writes a `versions.txt` file with tool and package versions to the output directory.

    Includes versions of:
    - Plasmidhub
    - Python
    - FastANI
    - ABRicate
    - Several important Python packages

    Args:
        output_dir (str): Path to the output directory where versions.txt will be saved.
    """
    import sys
    import importlib.metadata
    def get_tool_version(cmd):
        try:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            return result.stdout.strip().split('\n')[0]
        except Exception:
            return "Error retrieving version"

    def get_package_version(pkg_name):
        try:
            return importlib.metadata.version(pkg_name)
        except importlib.metadata.PackageNotFoundError:
            return "not installed"

    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "versions.txt"), "w") as vf:
        vf.write(f"Plasmidhub version: {VERSION}\n")
        vf.write(f"Python version: {sys.version.split()[0]}\n")
        vf.write(f"FastANI version: {get_tool_version(['fastANI', '--version'])}\n")
        vf.write(f"ABRicate version: {get_tool_version(['abricate', '--version'])}\n\n")

        vf.write("Python package versions:\n")
        for pkg in ["biopython", "pandas", "networkx", "matplotlib", "python-louvain", "numpy"]:
            vf.write(f"{pkg}: {get_package_version(pkg)}\n")

def main():
    """
    Main entry point of the Plasmidhub CLI tool.

    Parses command-line arguments, handles plot-only mode or full pipeline mode,
    sets up logging and directories, and orchestrates the preprocessing, ANI computation,
    clustering, and optional ABRicate analysis steps.

    The CLI supports:
    - ANI calculation using FastANI
    - Clustering plasmids
    - Annotating with ABRicate
    - Network visualization and customization
    - Running plot generation separately (--plot_only)
    """
    parser = argparse.ArgumentParser(
        prog="plasmidhub",
        description=(
            "SYNOPSIS\n"
            "  Plasmidhub: Bioinformatic Tool for Plasmid Network Analysis\n\n"
            "  Plasmidhub constructs a similarity-based network from plasmid FASTA files.\n"
            "  It uses FastANI to calculate pairwise ANI with user defined parameters,\n"
            "  clusters the plasmids, and visualizes the network.\n"
            "  Includes optional annotation with ABRicate to identify resistance and virulence genes.\n"
        ),
        epilog=(
            "DOCUMENTATION \n"
            "  https://https://github.com/DEpt-metagenom/plasmidhub \n\n" 
            "Example:\n"
            "  plasmidhub path/to/my/plasmid/FASTA/files --fragLen 1000 --kmer 14 --coverage_threshold 0.5 --ani_threshold 95 --min_cluster_size 4 --plot_k 2.0 3.0 -t 32\n"
            "  plasmidhub --plot_only path/to/my/results  --plot_k 3 3 --plot_node_color white --plot_node_size 500 --plot_node_shape s -t 32\n\n"
            "Version 1.0.1\n"
            "If you are using Plasmidhub, please reference: https://github.com/DEpt-metagenom/plasmidhub"
        ),
        formatter_class=argparse.RawTextHelpFormatter
    )

    # Positional argument
    parser.add_argument("input_dir", nargs="?", help="Path to plasmid FASTA files directory")

    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {VERSION}",
                         help="Show program's version number and exit")

    # ANI
    ani_group = parser.add_argument_group("ANI")
    ani_group.add_argument("--fragLen", type=int, default=1000, help="FastANI fragment length (default: 1000)")
    ani_group.add_argument("--kmer", type=int, default=14, help="FastANI kmer size (default: 14)")
    ani_group.add_argument("--coverage_threshold", type=float, default=0.5, help="Coverage threshold fraction (default: 0.5)")
    ani_group.add_argument("--ani_threshold", type=float, default=95.0, help="ANI threshold (default: 95.0)")

    # CLUSTER
    cluster = parser.add_argument_group("CLUSTER")
    cluster.add_argument("--cluster_off", action="store_true", help="Disable clustering step")
    cluster.add_argument("--min_cluster_size", type=int, default=3,
                         help="Minimum plasmid count for final clusters (default: 3)")

    # ABRicate
    abricate_group = parser.add_argument_group("ABRicate")
    abricate_group.add_argument("--skip_abricate", action="store_true", help="Skip ABRicate analysis step")
    abricate_group.add_argument(
        "--abricate_dbs",
        nargs="+",
        metavar="DB",
        help=(
            "List of ABRicate databases to run (default: plasmidfinder, card, vfdb).\n"
            "Available databases:\n"
            " resfinder\n"
            " megares\n"
            " vfdb\n"
            " card\n"
            " argannot\n"
            " ecoli_vf\n"
            " plasmidfinder\n"
            " ncbi\n"
            " ecoh"
        )
    )

    # PLOT
    plot = parser.add_argument_group("PLOT")
    plot.add_argument("--plot_k", nargs=2, type=float, metavar=('MIN_K', 'MAX_K'),
                      help="Generate network visualizations.\nSpecify minimum and maximum k (e.g.: --plot_k 1.5 3.0)")
    plot.add_argument("--plot_skip", action="store_true", help="Skip network visualization step")
    plot.add_argument("--plot_only", type=str, metavar="DIR",
                      help="Generate plots only from existing files, without running the whole pipeline. Figure parameters can be adjusted:")
    plot.add_argument("--plot_edge_width", nargs=2, type=float, metavar=('MIN_WIDTH', 'MAX_WIDTH'),
                      default=[0.2, 2.0], help="Minimum and maximum edge widths (default: 0.2 2.0)")
    plot.add_argument("--plot_node_size", type=int, default=900, help="Node size (default: 900)")
    plot.add_argument("--plot_node_shape", type=str, default='o', help="Node shape (e.g.: 'o', 's' (square), '>' (triangle) , '^' , '*' ect., default: o)")
    plot.add_argument("--plot_node_color", type=str, help="Node color (e.g.: 'white', 'blue', default: 'grey')")
    plot.add_argument("--plot_figsize", nargs=2, type=int, metavar=('WIDTH', 'HEIGHT'), default=[25, 25], help="Figure size in inches (default: 25 25)")
    plot.add_argument("--plot_iterations", type=int, default=100, help="Number of iterations (spring layout, default: 100)")

    # THREADS
    threads = parser.add_argument_group("THREADS")
    threads.add_argument("-t", "--threads", type=int, default=4, metavar="", help="Number of threads to use (default: 4)")

    args = parser.parse_args()

    if args.plot_only and not args.input_dir:
        args.input_dir = args.plot_only

    input_path = Path(args.input_dir).resolve()
    results_path = input_path / "results"
    results_path.mkdir(exist_ok=True)

    # === Plot-only mode === #

    if args.plot_only:
        import sys
        if not os.path.exists(args.plot_only):
            parser.error("The path provided to --plot_only does not exist.")

        cmd = [sys.executable, os.path.join(os.path.dirname(__file__), "plot_only.py"),
               "--results_dir", args.plot_only]

        if args.plot_k:
            cmd.extend(["--plot_k", str(args.plot_k[0]), str(args.plot_k[1])])
        if args.plot_edge_width:
            cmd += ["--min_edge_width", str(args.plot_edge_width[0]), "--max_edge_width", str(args.plot_edge_width[1])]
        if args.plot_node_size:
            cmd += ["--node_size", str(args.plot_node_size)]
        if args.plot_node_color:
            cmd += ["--node_color", args.plot_node_color]
        if args.plot_node_shape:
            cmd += ["--node_shape", args.plot_node_shape]
        if args.plot_figsize:
            cmd += ["--figsize", str(args.plot_figsize[0]), str(args.plot_figsize[1])]
        if args.plot_iterations:
            cmd += ["--iterations", str(args.plot_iterations)]

        subprocess.run(cmd)
        return

    ## === Full pipeline mode === ##
    if not args.input_dir:
        parser.error("input_dir is required unless --plot_only is used.")

    if not args.plot_only:
        if (
            args.plot_node_size != 900 or
            args.plot_edge_width != [0.2, 2.0] or
            args.plot_node_shape != 'o' or
            args.plot_figsize != [25, 25] or
            args.plot_iterations != 100
        ):
            parser.error(
                "Plot customization options (--plot_node_size, --plot_edge_width, etc.) "
                "can only be used with --plot_only."
            )

    # Create results directory inside input_dir if it doesn't exist
    results_dir = os.path.join(args.input_dir, "results")
    os.makedirs(results_dir, exist_ok=True)

    # Setup logger now that we have results_dir
    log_file = os.path.join(results_dir, "run.log")
    logger = setup_logging(log_file)
    logger.info(f"Starting Plasmidhub v{VERSION}")

    logger.info(f"Input directory: {args.input_dir}")

    write_versions_txt(results_dir)

    # Step 1-4: preprocess (validate, list files, count, size)
    plasmid_list = preprocessing.validate_and_list_plasmids(args.input_dir)
    logger.info(f"Number of plasmids: {len(plasmid_list)}")
    # Write output files inside results_dir
    preprocessing.write_plasmid_list(plasmid_list, output_file=os.path.join(results_dir, "Plasmid_list.txt"))
    preprocessing.write_plasmid_sizes(plasmid_list, output_file=os.path.join(results_dir, "Plasmid_sizes.txt"))

    # Step 5-6: run FastANI - output to results_dir 
    logger.info("Running FastANI...")

    input_path = Path(args.input_dir).resolve()
    results_path = Path(results_dir)

    with change_dir(input_path):
        ani.run_fastani(
            str(results_path / "Plasmid_list.txt"),
            fragLen=args.fragLen,
            minFrag=0.001,  # Hardcoded minimum fraction
            kmer=args.kmer,
            output_dir=str(results_path),
            threads=args.threads
        )

    # Step 6.5: Normalize plasmid names (strip paths)
    filtering.strip_paths_in_fastani(os.path.join(results_dir, "fastani_raw_results.tsv"))
    filtering.strip_paths_in_plasmid_list(os.path.join(results_dir, "Plasmid_list.txt"))

    # Step 7: filter self comparisons
    logger.info("Filtering self comparisons...")
    filtering.filter_self_comparisons(
        os.path.join(results_dir, "fastani_raw_results.tsv"),
        os.path.join(results_dir, "fastani_raw_results_filtered.tsv"),
    )

    # Step 8: add sizes - input and output inside results_dir
    logger.info("Adding plasmid sizes to ANI results...")
    filtering.add_plasmid_sizes(
        os.path.join(results_dir, "fastani_raw_results_filtered.tsv"),
        os.path.join(results_dir, "Plasmid_sizes.txt"),
        os.path.join(results_dir, "ANI_results_with_sizes.tsv"),
    )

    # Step 9-10: apply coverage and ANI threshold filters - input/output inside results_dir
    logger.info("Applying coverage and ANI thresholds...")
    filtering.apply_filters(
        os.path.join(results_dir, "ANI_results_with_sizes.tsv"),
        os.path.join(results_dir, "ANI_results_final.tsv"),
        coverage_threshold=args.coverage_threshold,
        ani_threshold=args.ani_threshold,
        frag_len=args.fragLen,
    )

    # Step 11: build network - inputs inside results_dir
    from plasmidhub import network_builder
    logger.info("Building plasmid network...")
    network_builder.build_network(
        os.path.join(results_dir, "ANI_results_final.tsv"),
        os.path.join(results_dir, "Plasmid_list.txt"),
        results_dir  
    )

    logger.info("Done!")

    # Step 11.5: compute and save node stats
    from plasmidhub import node_stats
    logger.info("Computing node statistics...")
    node_stats.compute_node_stats(results_dir)

    logger.info("Done!")

    # Step 12: clustering
    if not args.cluster_off:
        logger.info("Clustering plasmids...")
        from plasmidhub import clustering
        clustering.main(results_dir, args.min_cluster_size)

        # Generate plasmid-cluster mapping file
        import glob
        def generate_plasmid_cluster_mapping(results_dir):
            mapping_file = os.path.join(results_dir, "plasmid_cluster_mapping.txt")
            with open(mapping_file, 'w') as outfile:
                for filepath in glob.glob(os.path.join(results_dir, "cluster_*.txt")):
                    if os.path.basename(filepath) == "cluster_list.txt":
                        continue  # Skip the summary file
                    cluster_name = os.path.basename(filepath).replace(".txt", "")
                    with open(filepath) as f:
                        for line in f:
                            plasmid = line.strip()
                            if plasmid:
                                outfile.write(f"{plasmid}\t{cluster_name}\n")

        generate_plasmid_cluster_mapping(results_dir)
    else:
        logger.info("Clustering skipped due to --cluster_off")

    logger.info("Done!")

    # Default databases
    default_dbs = ['plasmidfinder', 'card', 'vfdb']

    if not args.skip_abricate:
        logger.info("Running ABRicate annotation...")

        # If user specified databases, use them; otherwise use the default
        abricate_dbs = args.abricate_dbs if args.abricate_dbs else default_dbs

        abricate_results_dir = os.path.join(results_dir, "abricate_results")
        abricate.run_abricate_bulk(
            input_dir=args.input_dir,
            results_dir=abricate_results_dir,
            db_list=abricate_dbs,
            threads=args.threads
        )
    else:
        logger.info("ABRicate skipped due to --skip_abricate")

    #  Network visualization
    if not args.plot_skip:
        logger.info("Generating network visualizations...")
        from plasmidhub import plot
        from plasmidhub.cluster_color import assign_cluster_colors
    
        if not args.cluster_off:
            mapping_file = os.path.join(results_dir, "plasmid_cluster_mapping.txt")
            assign_cluster_colors(results_dir, mapping_file)

        json_file = os.path.join(results_dir, "network.json")
        G = plot.load_network_from_json(json_file)

        if args.plot_k:
            min_k = int(args.plot_k[0])
            max_k = int(args.plot_k[1])
        else:
            min_k = 3
            max_k = 3

        plot.run_visualizations(results_dir, min_k, max_k + 1)

    else:
        logger.info("Network visualization skipped due to --plot_skip")

    move_files_to_subdirs(results_dir)

    logger.info("Done!")


def move_files_to_subdirs(results_dir):
    """
    Organize result files by moving them into specific subdirectories within the given directory.

    Creates two subdirectories inside `results_dir`: "plots" and "statistics".  
    Moves plot files matching the patterns "network_k_*.pdf" and "network_k_*.svg" into the "plots" folder.  
    Moves predefined statistics files (CSV and JSON) into the "statistics" folder if they exist.

    Parameters:
    -----------
    results_dir : str
        The path to the directory containing the result files to organize.

    Returns:
    --------
    None
    """
    # Create subdirectories
    plots_dir = os.path.join(results_dir, "plots")
    stats_dir = os.path.join(results_dir, "statistics")
    os.makedirs(plots_dir, exist_ok=True)
    os.makedirs(stats_dir, exist_ok=True)

    # Move plots
    for plot_file in glob.glob(os.path.join(results_dir, "network_k_*.pdf")) + \
                     glob.glob(os.path.join(results_dir, "network_k_*.svg")):
        shutil.move(plot_file, plots_dir)

    # Move stats files
    stat_files = [
        "degree_centrality.csv",
        "betweenness_centrality.csv",
        "node_degrees.csv",
        "network_metrics.csv",
        "community_partition.json",
        "Node_stats.csv"
    ]
    for fname in stat_files:
        full_path = os.path.join(results_dir, fname)
        if os.path.exists(full_path):
            shutil.move(full_path, stats_dir)

if __name__ == '__main__':
    main()