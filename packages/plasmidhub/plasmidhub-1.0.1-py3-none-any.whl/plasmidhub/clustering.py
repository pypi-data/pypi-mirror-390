import os
import pandas as pd
from collections import defaultdict
import argparse
import logging
logger = logging.getLogger(__name__)

def find_valid_subclusters(results_dir):
    """
    Identify "valid" subclusters from the results directory.

    A subcluster is considered "valid" if it contains at least 3 plasmids.

    Args:
        results_dir (str): Path to the results directory.

    Returns:
        list of tuple: List of (filename, plasmid_count) for valid subclusters,
                       sorted by plasmid count in descending order.
    """
    valid_subclusters = []

    for filename in sorted(os.listdir(results_dir)):
        if filename.startswith("subcluster_") and filename.endswith("_plasmids.txt"):
            filepath = os.path.join(results_dir, filename)
            with open(filepath, 'r') as f:
                plasmid_count = sum(1 for _ in f)

            if plasmid_count >= 3:  # Hardcoded rule
                valid_subclusters.append((filename, plasmid_count))

    valid_subclusters.sort(key=lambda x: x[1], reverse=True)
    return valid_subclusters

def write_subcluster_list(valid_subclusters, output_path):
    """
    Write a summary of valid subclusters to a file.

    Args:
        valid_subclusters (list of tuple): List of (subcluster filename, plasmid count).
        output_path (str): Path to output file where the list will be written.
    """
    with open(output_path, "w") as f:
        f.write("Subcluster\tPlasmids\n")
        for subcluster, count in valid_subclusters:
            f.write(f"{subcluster}\t{count}\n")

def extract_clusters(valid_subclusters, results_dir, fastani_path, output_dir):
    """
    Extract complete subgraphs (cliques - plasmid clusters) by iteratively removing poorly connected nodes from each subcluster
    until a complete subgraph (clique) is identified.

    Args:
        valid_subclusters (list of tuple): Valid subclusters and plasmid counts.
        results_dir (str): Path to directory containing subcluster files.
        fastani_path (str): Path to the final FastANI results TSV file.
        output_dir (str): Directory where refined clusters will be saved.
    """
    fastani_df = pd.read_csv(fastani_path, sep="\t")

    for subcluster_file, _ in valid_subclusters:
        full_path = os.path.join(results_dir, subcluster_file)
        try:
            with open(full_path, "r") as f:
                original_plasmids = set(line.strip() for line in f)
        except FileNotFoundError:
            logger.warning(f"File {subcluster_file} not found. Skipping.")
            continue

        subcluster_plasmids = original_plasmids.copy()

        connections = defaultdict(set)
        for _, row in fastani_df.iterrows():
            q, r = row["Query"], row["Reference"]
            if q in subcluster_plasmids and r in subcluster_plasmids:
                connections[q].add(r)
                connections[r].add(q)

        # Iteratively remove nodes with the fewest connections until we get a complete subgraph
        while True:
            current_nodes = set(connections.keys())
            if len(current_nodes) < 3:
                subcluster_plasmids = set()
                break

            # Check if the current graph is a complete subgraph (clique)
            complete = all(len(connections[node]) == len(current_nodes) - 1 for node in current_nodes)
            if complete:
                subcluster_plasmids = current_nodes
                break

            # Find the node with the fewest connections (lowest degree)
            min_node = min(current_nodes, key=lambda x: len(connections[x]))

            # Remove that node from the graph
            del connections[min_node]
            for conn in connections.values():
                conn.discard(min_node)

        # Step 7: Save the refined subcluster to a new file with the desired naming format
        cluster_number = subcluster_file.split("_")[1]  # Extract the number from subcluster_XX_plasmids.txt
        output_file = f"cluster_{cluster_number}.txt"

        cluster_path = os.path.join(output_dir, output_file)
        with open(cluster_path, "w") as f:

            for plasmid in subcluster_plasmids:
                f.write(plasmid + "\n")

        
def filter_clusters_by_size(output_dir, min_cluster_size):
    """
    Remove clusters consisting of fewer plasmids than the specified size.

    Args:
        output_dir (str): Directory containing cluster files.
        min_cluster_size (int): Minimum number of plasmids required to keep a cluster.
    """
    for filename in os.listdir(output_dir):
        if filename.startswith("cluster_") and filename.endswith(".txt"):
            path = os.path.join(output_dir, filename)
            with open(path, "r") as f:
                lines = f.readlines()
            if len(lines) < min_cluster_size:
                os.remove(path)

def write_cluster_list(output_dir, output_path):
    """
    Write a list of clusters and their plasmid counts to a file.

    Args:
        output_dir (str): Directory containing cluster files.
        output_path (str): Path to output list file.
    """

    cluster_files = []
    for filename in os.listdir(output_dir):
        if (
            filename.startswith("cluster_") 
            and filename.endswith(".txt") 
            and filename not in {os.path.basename(output_path), "cluster_colours.txt"}  # exclude output file itself and cluster_colours.txt
        ):
            path = os.path.join(output_dir, filename)
            with open(path, "r") as f:
                count = sum(1 for _ in f)
            cluster_files.append((filename, count))
    cluster_files.sort(key=lambda x: x[1], reverse=True)
    with open(output_path, "w") as f:
        f.write("Cluster\tPlasmids\n")
        for filename, count in cluster_files:
            f.write(f"{filename}\t{count}\n")
                
def main(results_dir, min_cluster_size):
    """
    Main function to identify plasmid clusters.

    Steps:
    1. Find valid subclusters.
    2. Write subcluster summary.
    3. Extract plasmid clusters (comnplete subgraphs).
    4. Filter clusters by size.
    5. Write final cluster summary.

    Args:
        results_dir (str): Path to results directory containing subclusters and ANI results.
        min_cluster_size (int): Minimum plasmid count for a cluster to be retained.
    """
    fastani_path = os.path.join(results_dir, "ANI_results_final.tsv")
    subcluster_list_output = os.path.join(results_dir, "subcluster_list.txt")
    cluster_list_output = os.path.join(results_dir, "cluster_list.txt")

    logger.info("Finding valid subclusters (>=3 plasmids)...")
    valid_subclusters = find_valid_subclusters(results_dir)

    write_subcluster_list(valid_subclusters, subcluster_list_output)

    logger.info("Identifying  clusters...")
    extract_clusters(valid_subclusters, results_dir, fastani_path, results_dir)

    logging.info(f"Keep only clusters with >={min_cluster_size} plasmids...")
    filter_clusters_by_size(results_dir, min_cluster_size)

    write_cluster_list(results_dir, cluster_list_output)

    # Check: warn user if cluster_list.txt is empty
    if os.path.exists(cluster_list_output):
        with open(cluster_list_output, "r") as f:
            lines = f.readlines()
            if len(lines) <= 1:
                logger.warning("No clusters detected with the given parameters!")


    # logger.info("Done!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clustering Tool")
    parser.add_argument("results_dir", help="Path to results directory created by main.py")
    parser.add_argument("--min_cluster_size", type=int, default=3, help="Minimum number of plasmids in final cluster (default: 3)")
    args = parser.parse_args()

    main(args.results_dir, args.min_cluster_size)
