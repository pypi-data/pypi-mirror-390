"""
Cluster Color Assignment Script

This script assigns a unique color to each cluster based on the provided
cluster list and writes the cluster-to-color mapping to a text file. It ensures
distinct coloring using a mix of the `tab20` matplotlib colormap and random
color generation when necessary.

Intended for use in visualizing plasmid networks with cluster-specific node colors.
"""

import os
import matplotlib.pyplot as plt
import random
import logging

logger = logging.getLogger(__name__)

def assign_cluster_colors(results_dir, mapping_file):
    cluster_list_path = os.path.join(results_dir, "cluster_list.txt")
    color_file = os.path.join(results_dir, "cluster_colours.txt")
    
    clusters = []
    with open(cluster_list_path) as f:
        next(f)  # Skip header
        for line in f:
            if line.strip():
                cluster_file, _ = line.strip().split('\t')
                cluster = cluster_file.replace('.txt', '')
                clusters.append(cluster)

    n_clusters = len(clusters)

    # Start with base colors from tab20
    cmap = plt.get_cmap('tab20')
    base_colors = [
        '#{:02x}{:02x}{:02x}'.format(int(r * 255), int(g * 255), int(b * 255))
        for r, g, b in cmap.colors
    ]

    used_colors = set(base_colors[:min(n_clusters, len(base_colors))])
    full_color_list = base_colors[:min(n_clusters, len(base_colors))]

    # Generate additional distinct random colors if needed
    while len(full_color_list) < n_clusters:
        while True:
            color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
            if color not in used_colors:
                used_colors.add(color)
                full_color_list.append(color)
                break

    color_map = dict(zip(clusters, full_color_list))

    with open(color_file, 'w') as out:
        for cluster, color in color_map.items():
            out.write(f"{cluster}\t{color}\n")

    logger.info(f"Cluster colors saved to: {color_file}")