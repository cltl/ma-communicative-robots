"""
Code originally from
https://gitlab.ifi.uzh.ch/DDIS-Public/chimp-mat/-/blob/master/kbci_py/methods/graph_measures.py
Credits to Romana Pernischova
"""

import networkx as nx
import numpy as np
from networkx.algorithms import approximation


def entropy(cent_measure):
    m = np.asarray(cent_measure, float)
    dist = m / m.sum()
    ent = np.nansum(dist * np.log2(1.0 / dist))
    return ent


# Simple Measures
def get_count_nodes(graph: nx.Graph):
    count = nx.number_of_nodes(graph)
    return count


def get_count_edges(graph: nx.Graph):
    count = nx.number_of_edges(graph)
    return count


# Centrality Measures
def get_avg_degree(graph: nx.Graph): # Counts directionality?
    count = np.mean(list(dict(graph.degree()).values()))
    return count


def get_avg_degree_centr(graph: nx.Graph):
    centrality = list(nx.degree_centrality(graph).values())
    count = np.mean(centrality)
    return count


def get_avg_closeness(graph: nx.Graph):
    count = np.mean(list(nx.closeness_centrality(graph).values()))
    return count


def get_avg_betweenness(graph: nx.Graph):
    closeness = list(nx.betweenness_centrality(graph).values())
    count = np.mean(closeness)
    return count


# Connectivity Measures
def get_degree_connectivity(graph: nx.Graph):
    count = np.mean(list(nx.average_neighbor_degree(graph).values()))
    return count


def get_assortativity(graph: nx.Graph):
    try:
        assort = nx.degree_pearson_correlation_coefficient(graph)
    except:
        assort = np.nan
    return assort


def get_node_connectivity(graph: nx.Graph):
    con = approximation.node_connectivity(graph)
    return con


# Clustering Measures
def get_clustering_approx(graph: nx.DiGraph):
    graph_und = graph.to_undirected()
    clust = approximation.average_clustering(graph_und)
    return clust


def get_clustering(graph: nx.DiGraph):
    graph_und = graph.to_undirected()
    clust = nx.average_clustering(graph_und)
    return clust


def get_transitivity(graph: nx.DiGraph):
    trans = nx.transitivity(graph)
    return trans


# Components, Cliques
def get_number_components(graph: nx.Graph):
    g = graph.to_undirected()
    num_components = nx.number_connected_components(g)
    return num_components


def get_number_strong_comp(graph: nx.Graph):
    num_strong_components = nx.number_strongly_connected_components(graph)
    return num_strong_components


# Shortest Path Measures
def get_shortest_path(graph: nx.Graph):
    # shortest Paths --> must be connected
    graph_und = graph.to_undirected()
    if nx.is_connected(graph_und):
        sp_length = nx.average_shortest_path_length(graph_und)
    else:
        sum = 0
        count = 0
        connected_components = list(graph_und.subgraph(c) for c in nx.connected_components(graph_und))
        for component in connected_components:
            sum = sum + nx.average_shortest_path_length(component)
            count = count + 1
        sp_length = sum / count

    return sp_length


# Entropy
def get_entropy_centr(graph: nx.Graph):
    centrality = list(nx.degree_centrality((graph)).values())
    num_entropy = entropy(centrality)
    return num_entropy


def get_entropy_clos(graph: nx.Graph):
    centrality = list(nx.closeness_centrality((graph)).values())
    num_entropy = entropy(centrality)
    return num_entropy


# Sparseness
def get_sparseness(graph: nx.Graph):
    mat = nx.adjacency_matrix((graph)).todense()
    num_num = np.count_nonzero(mat)
    num_val = np.prod(mat.shape)
    sparseness = float(num_num) / num_val
    return sparseness
