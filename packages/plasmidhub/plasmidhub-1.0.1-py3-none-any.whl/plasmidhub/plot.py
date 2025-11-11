
"""
This module provides functions to visualize a plasmid network stored as a Cytoscape-compatible JSON file.
It supports both basic visualizations (with grey nodes and edges) and colored visualizations based on
cluster assignments (if clustering is not turned off). Outputs are saved as PDF and SVG files, with and without node labels.

Dependencies:
    - networkx
    - matplotlib
    - json
    - logging
    - os
"""

import json
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os
import logging

logger = logging.getLogger(__name__)

def load_network_from_json(json_file):
    """Load a network graph from a JSON file."""
    with open(json_file, 'r') as f:
        data = json.load(f)
    return nx.cytoscape_graph(data)

def visualize_network_basic(G, k, output_path_no_ext):
    """
    Generate a basic network visualization with grey nodes and edges.
    Saves both labeled and unlabeled versions in PDF and SVG format.

    Args:
        G (networkx.Graph): The network graph.
        k (float): The spring layout "k" parameter (node spacing).
        output_path_no_ext (str): Base path (without extension) for saving outputs.
    """

    min_weight = 5
    max_weight = 100
    min_width = 0.2  # reduced thickness
    max_width = 2.0  # reduced thickness

    edge_weights = nx.get_edge_attributes(G, 'weight')
    for edge in G.edges():
        if edge not in edge_weights:
            edge_weights[edge] = min_weight

    edge_widths = []
    for edge in G.edges():
        weight = edge_weights.get(edge, min_weight)
        weight_clipped = max(min_weight, min(weight, max_weight))
        scaled_width = min_width + (weight_clipped - min_weight) / (max_weight - min_weight) * (max_width - min_width)
        edge_widths.append(scaled_width)

    pos = nx.spring_layout(G, k=k, seed=69420, iterations=100)

    # With labels
    fig, ax = plt.subplots(figsize=(25, 25))
    nx.draw_networkx_nodes(G, pos, node_color='grey', node_size=900, node_shape='o',
                           linewidths=1, edgecolors='black', alpha=0.65, ax=ax)
    nx.draw_networkx_edges(G, pos, width=edge_widths, edge_color='grey', alpha=0.7, ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold', ax=ax)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(output_path_no_ext + ".pdf", format="pdf")
    plt.savefig(output_path_no_ext + ".svg", format="svg")
    plt.close()

    # Without labels
    fig, ax = plt.subplots(figsize=(25, 25))
    nx.draw_networkx_nodes(G, pos, node_color='grey', node_size=900, node_shape='o',
                           linewidths=1, edgecolors='black', alpha=0.65, ax=ax)
    nx.draw_networkx_edges(G, pos, width=edge_widths, edge_color='grey', alpha=0.7, ax=ax)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(output_path_no_ext + "_nolabels.pdf", format="pdf")
    plt.savefig(output_path_no_ext + "_nolabels.svg", format="svg")
    plt.close()

def visualize_network_colored_by_cluster(G, k, output_path_no_ext, cluster_mapping_file, cluster_color_file):
    """
    Visualize the network graph with nodes colored by cluster membership.

    Reads cluster assignments and their corresponding colors from input files.
    Saves both labeled and unlabeled versions in PDF and SVG format.

    Args:
        G (networkx.Graph): The network graph.
        k (float): The spring layout "k" parameter (node spacing).
        output_path_no_ext (str): Base path (without extension) for saving outputs.
        cluster_mapping_file (str): Path to TSV file mapping plasmid IDs to cluster IDs.
        cluster_color_file (str): Path to TSV file mapping cluster IDs to hex color codes.
    """
    # Check if cluster_list.txt contains only the header
    cluster_list_file = os.path.join(os.path.dirname(cluster_mapping_file), "cluster_list.txt")
    if os.path.exists(cluster_list_file):
        with open(cluster_list_file) as f:
            lines = f.readlines()
            if len(lines) <= 1:
                logger.warning("No clusters detected with the given parameters!")

    # Load plasmid-cluster mappings
    cluster_map = {}
    with open(cluster_mapping_file) as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) == 2:
                plasmid, cluster = parts
                cluster_map[plasmid] = cluster

    # Load cluster-color mappings
    color_map = {}
    with open(cluster_color_file) as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) == 2:
                cluster, color = parts
                color_map[cluster] = color

    # Assign colors to nodes
    node_colors = []
    for node in G.nodes():
        cluster = cluster_map.get(node)
        color = color_map.get(cluster, "#cccccc")  # default light grey for unclustered
        node_colors.append(color)

    # Edge weight scaling
    min_weight = 5
    max_weight = 100
    min_width = 0.2
    max_width = 2.0
    edge_weights = nx.get_edge_attributes(G, 'weight')
    edge_widths = []
    for edge in G.edges():
        weight = edge_weights.get(edge, min_weight)
        weight_clipped = max(min_weight, min(weight, max_weight))
        scaled_width = min_width + (weight_clipped - min_weight) / (max_weight - min_weight) * (max_width - min_width)
        edge_widths.append(scaled_width)

    pos = nx.spring_layout(G, k=k, seed=69420, iterations=100)

    # --- Create legend handles ---
    legend_handles = [
        mpatches.Patch(color=color, label=cluster)
        for cluster, color in sorted(color_map.items())
    ]

    # With labels
    fig, ax = plt.subplots(figsize=(25, 25))
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=900, node_shape='o',
                           linewidths=1, edgecolors='black', alpha=0.9, ax=ax)
    nx.draw_networkx_edges(G, pos, width=edge_widths, edge_color='grey', alpha=0.7, ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold', ax=ax)
    plt.axis('off')

    # Add legend
    legend = ax.legend(handles=legend_handles, loc='upper right', fontsize=16, title="Clusters", title_fontsize=18,
                       bbox_to_anchor=(1.02, 1.0))
    plt.tight_layout()
    plt.savefig(output_path_no_ext + "_cluster_colored.pdf", format="pdf")
    plt.savefig(output_path_no_ext + "_cluster_colored.svg", format="svg")
    plt.close()

    # Without labels
    fig, ax = plt.subplots(figsize=(25, 25))
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=900, node_shape='o',
                           linewidths=1, edgecolors='black', alpha=0.9, ax=ax)
    nx.draw_networkx_edges(G, pos, width=edge_widths, edge_color='grey', alpha=0.7, ax=ax)
    plt.axis('off')

    # Add legend
    legend = ax.legend(handles=legend_handles, loc='upper right', fontsize=16, title="Clusters", title_fontsize=18,
                       bbox_to_anchor=(1.02, 1.0))
    plt.tight_layout()
    plt.savefig(output_path_no_ext + "_cluster_colored_nolabels.pdf", format="pdf")
    plt.savefig(output_path_no_ext + "_cluster_colored_nolabels.svg", format="svg")
    plt.close()


def run_visualizations(results_dir, k_min, k_max):
    """
    Run all visualizations over a range of 'k' layout parameters.

    Args:
        results_dir (str): Path to the results directory containing network and cluster files.
        k_min (int): Minimum k value (inclusive).
        k_max (int): Maximum k value (exclusive).
    """

    json_file = os.path.join(results_dir, "network.json")
    G = load_network_from_json(json_file)

    # Add cluster-colored visualizations if cluster color file exists
    cluster_mapping_file = os.path.join(results_dir, "plasmid_cluster_mapping.txt")
    cluster_color_file = os.path.join(results_dir, "cluster_colours.txt")
    if os.path.exists(cluster_mapping_file) and os.path.exists(cluster_color_file):
        logger.info("Generating cluster-colored visualizations...")
        for k in range(k_min, k_max):
            filename_base = os.path.join(results_dir, f"network_k_{k}")
            visualize_network_colored_by_cluster(G, k, filename_base, cluster_mapping_file, cluster_color_file)
    else:
        logger.info("Cluster mapping or color file not found. Skipping cluster-colored plots.")


    for k in range(k_min, k_max):
        filename_base = os.path.join(results_dir, f"network_k_{k}")
        visualize_network_basic(G, k, filename_base)
