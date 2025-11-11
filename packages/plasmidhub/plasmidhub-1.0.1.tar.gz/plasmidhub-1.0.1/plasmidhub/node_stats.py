import networkx as nx
import pandas as pd
import os
import logging
logger = logging.getLogger(__name__)

def compute_node_stats(results_dir):
    """
    Compute and save network node statistics for a plasmid network.

    This function reads a GML network file, calculates various centrality 
    and connectivity measures for each node, and outputs the results 
    as a CSV file.

    Metrics computed:
        - Betweenness centrality (unweighted and weighted)
        - Closeness centrality (unweighted and weighted)
        - Degree centrality
        - Weighted degree centrality
        - Nested contribution (normalized degree)
        - Weighted nested contribution
        - Normalized degree (degree relative to total number of nodes)

    Args:
        results_dir (str): Directory containing the "network.gml" file.
                           The output CSV file will also be saved here.

    Returns:
        None

    Input File:
        - network.gml

    Output File:
        - Node_stats.csv: CSV file with columns:
            Node, Betweenness, Weighted_Betweenness, Closeness, 
            Weighted_Closeness, Degree_Centrality, 
            Weighted_Degree_Centrality, Nested_Contribution, 
            Weighted_Nested_Contribution, Normalised_Degree

    Logs:
        - Error if the GML network file is missing.
        - Info message when the node statistics file is successfully saved.
    """

    gml_path = os.path.join(results_dir, "network.gml")
    if not os.path.exists(gml_path):
        logger.error(f"Could not find network file at: {gml_path}")
    
    G = nx.read_gml(gml_path)

    # Compute stats
    betweenness = nx.betweenness_centrality(G, normalized=True)
    weighted_betweenness = nx.betweenness_centrality(G, weight="weight", normalized=True)

    closeness = nx.closeness_centrality(G)
    weighted_closeness = nx.closeness_centrality(G, distance="weight")

    degree_centrality = nx.degree_centrality(G)
    weighted_degree_centrality = {
        node: sum(data["weight"] for _, _, data in G.edges(node, data=True))
        for node in G.nodes()
    }

    degree = dict(G.degree())
    weighted_degree = {
        node: sum(data["weight"] for _, _, data in G.edges(node, data=True))
        for node in G.nodes()
    }

    max_degree = max(degree.values()) if degree else 1
    nested_contribution = {
        node: deg / max_degree
        for node, deg in degree.items()
    }

    max_weighted_degree = max(weighted_degree.values()) if weighted_degree else 1
    weighted_nested_contribution = {
        node: wdeg / max_weighted_degree
        for node, wdeg in weighted_degree.items()
    }

    num_nodes = len(G.nodes())
    normalized_degree = {
        node: deg / (num_nodes - 1)
        for node, deg in degree.items()
    }

    # Combine into DataFrame
    df = pd.DataFrame({
        "Node": list(G.nodes()),
        "Betweenness": pd.Series(betweenness),
        "Weighted_Betweenness": pd.Series(weighted_betweenness),
        "Closeness": pd.Series(closeness),
        "Weighted_Closeness": pd.Series(weighted_closeness),
        "Degree_Centrality": pd.Series(degree_centrality),
        "Weighted_Degree_Centrality": pd.Series(weighted_degree_centrality),
        "Nested_Contribution": pd.Series(nested_contribution),
        "Weighted_Nested_Contribution": pd.Series(weighted_nested_contribution),
        "Normalised_Degree": pd.Series(normalized_degree),
    })

    # Save
    output_path = os.path.join(results_dir, "Node_stats.csv")
    df.to_csv(output_path, index=False)

    logger.info(f"Node statistics saved.")
