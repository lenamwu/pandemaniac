import sim
import json
#this program should ideally run different strategies against one another 
def read_graph_from_json(json_file_path):
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    return data

# Example usage
graph = read_graph_from_json("J.5.1.json")

nodes = {
    "new": ["2", "10", "88", "133", "37"],  # Example nodes, adjust based on your graph
    # Add more strategies as needed
}
results = sim.run(graph, nodes)
print("Simulation Results:", results)
