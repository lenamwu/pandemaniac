import json
import networkx as nx
import time as tm
import random
import numpy as np

time1 = tm.time()

json_file_path = "J.5.1.json"

def read_graph_from_json(json_file_path):
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    graph = nx.Graph(data)
    return graph

def extract_info_from_graph_name(graph_name):
    components = graph_name.split('.')
    competition = components[0]
    num_seeds = int(components[1])
    unique_id = int(components[2])
    return competition, num_seeds, unique_id

graph_name = json_file_path
gph = read_graph_from_json(json_file_path)
competition, num_seeds, unique_id = extract_info_from_graph_name(graph_name)
gph_id = unique_id // 10
components = sorted(nx.connected_components(gph), key=len, reverse=True)
g = gph.subgraph(components[0])
avg_deg = g.number_of_edges() / g.number_of_nodes()
sorted_nodes_by_degree = sorted(g.nodes(), key=lambda x: g.degree(x), reverse=True)

def calculate_betweenness_centrality(g):
    return nx.betweenness_centrality(g)

def select_diverse_seeds(g, num_seeds, strategy='mixed'):
    selected_seeds = []
    if strategy == 'mixed':
        degree_sorted_nodes = sorted(g.nodes(), key=lambda x: g.degree(x), reverse=True)
        betweenness_centrality = calculate_betweenness_centrality(g)
        bc_sorted_nodes = sorted(betweenness_centrality, key=betweenness_centrality.get, reverse=True)
        
        # Mixing top degree and betweenness centrality nodes
        for i in range(num_seeds):
            if i % 2 == 0:
                selected_seeds.append(degree_sorted_nodes[i])
            else:
                selected_seeds.append(bc_sorted_nodes[i])
    return list(set(selected_seeds))  # Ensure uniqueness

def write_list_to_txt(node_list, filename):
    if not filename.endswith(".txt"):
        filename += ".txt"
    with open(filename, 'w') as file:
        for node in node_list:
            file.write(str(node) + '\n')

def prepare_solution(num_seeds, g, strategy):
    sol = []
    for _ in range(50):  # Adjust the loop to generate enough seeds for each round
        seeds = select_diverse_seeds(g, num_seeds, strategy=strategy)
        sol.extend(seeds)
    return sol

# Adjust the strategy based on the graph type or other characteristics
strategy = 'mixed'  # Example strategy
sol = prepare_solution(num_seeds, g, strategy)
write_list_to_txt(sol, json_file_path)

time2 = tm.time()
print("Time taken:", time2 - time1)
