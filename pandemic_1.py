import json
import networkx as nx
import time as tm
import random

time1=tm.time()

json_file_path = "J.10.20.json"

'''competition: 'J'(tournament) or 'RR' '''

def read_graph_from_json(json_file_path):
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    # Create an undirected graph using NetworkX
    graph = nx.Graph(data)
    return graph

def extract_info_from_graph_name(graph_name):
    # Split the graph name into its components
    components = graph_name.split('.')

    # Extract num_seeds and unique_id
    competition = components[0]
    num_seeds = int(components[1])
    unique_id = int(components[2])

    return competition,num_seeds, unique_id

# Example usage
'''Copy the name of json file here; it should be saved in same lile'''

graph_name = json_file_path  #For txt name

# Read the graph from the JSON file
gph = read_graph_from_json(json_file_path)


# Extract num_seeds and unique_id from the graph name
competition, num_seeds, unique_id = extract_info_from_graph_name(graph_name)
'''
1:erdos renyi, 2:preferential attachment  3: ssbm  4: caltech  5:stanford nap
'''
gph_id=unique_id//10


#We will only consider the largest n components (n=2 ony if num_2 is not so small)else n=1
components = sorted(nx.connected_components(gph), key=len, reverse=True)
'''yet:Add branch: check if len(coponents[1])>>1 '''

g = gph.subgraph(components[0])
# g = nx.erdos_renyi_graph(10000, 0.003)
# num_seeds=35
# num_seeds=6

#average degree
avg_deg=g.number_of_edges()/g.number_of_nodes()


sorted_nodes_by_degree = sorted(g.nodes(), key=lambda x: g.degree(x), reverse=True)

def rank_deg(deg):
    return deg-1
def maxfirst(n,r,delete_node=1,random_draw=None, random_thrs=2):
    '''

    :param n:
    :param r:
    :param delete_node:
    :param random_draw: int, number of random drawn nodes
    :param random_thrs:
    :return:
    '''
    a=[sorted_nodes_by_degree[i]for i in range(r)]
    if n==r:
        return a
    if random_draw==None:
        r_left=n-r
        # nodels=sorted_nodes_by_degree[r:]
        gg=g.copy()
        aa=a[:delete_node]
        subgraph_nodes = aa + list(set.union(*[set(gg.neighbors(node)) for node in aa]))
        nodes_to_remove = list(gg.subgraph(subgraph_nodes).nodes())

        gg.remove_nodes_from(nodes_to_remove)
        # subgraph_aa_and_neighbors = gg.subgraph(aa + list(set.union(*[set(gg.neighbors(node)) for node in aa])))
        # gg.remove_nodes_from(subgraph_aa_and_neighbors.nodes())
        sort2=sorted(gg.nodes(), key=lambda x: gg.degree(x), reverse=True)
        for i in sort2:
            if r_left==0:
                break
            if i not in a:
                a.append(i)
                r_left-=1
        return a
    else:
        r_left=n-r-random_draw
        gg=g.copy()
        aa=a[:delete_node]

        subgraph_nodes = aa + list(set.union(*[set(gg.neighbors(node)) for node in aa]))

        nodes_to_remove = list(gg.subgraph(subgraph_nodes).nodes())

        gg.remove_nodes_from(nodes_to_remove)
        # subgraph_aa_and_neighbors = gg.subgraph(aa + list(set.union(*[set(gg.neighbors(node)) for node in aa])))
        # gg.remove_nodes_from(subgraph_aa_and_neighbors.nodes())
        sort2=sorted(gg.nodes(), key=lambda x: gg.degree(x), reverse=True)
        for i in sort2:
            if r_left==0:
                break
            if i not in a:
                a.append(i)
                r_left-=1
        a=set(a)
        selected_nodes = [node for node in sort2 if g.degree(node) > random_thrs]
        prob={node:rank_deg(g.degree(node))for node in selected_nodes}
        total_prob=sum(prob.values())
        normalized_prob={node:prb/total_prob for node,prb in prob.items()}
        ii=0
        while len(a)<n and ii<10:
            rr=n-len(a)
            random_selected_nodes = random.choices(list(normalized_prob.keys()), weights=list(normalized_prob.values()), k=min(rr, len(selected_nodes)))
            a.update(random_selected_nodes)
            ii+=1
        if len(a)<n:
            g_a=gg.subgraph(a)
            gg.remove_nodes_from(g_a.nodes())
            sort2=sorted(gg.nodes(), key=lambda x: gg.degree(x), reverse=True)
            rr=n-len(a)
            a.update(sort2[:rr])
        return list(a)




def write_list_to_txt(a, b):
    # Ensure b ends with ".txt"
    if not b.endswith(".txt"):
        b += ".txt"

    # Open the file in write mode
    with open(b, 'w') as file:
        # Write each element of the list to a new line in the file
        for element in a:
            for i in element:
                file.write(str(i) + '\n')

# Example usage

sol=[]
# for i in range(50):
#     sol.append(maxfirst(num_seeds,num_seeds//5,random_draw=1))

if gph_id==1 or gph_id==2 or gph_id==3:
    for i in range(17):
        sol.append(maxfirst(n=num_seeds,r=2,delete_node=1,random_draw=int(0.4*num_seeds)))
    for i in range(26):
        sol.append(maxfirst(n=num_seeds,r=1,delete_node=1,random_draw=num_seeds-3))
    for i in range(7):
        sol.append(maxfirst(n=num_seeds, r=2, delete_node=1,random_draw=2))
    random.shuffle(sol)
elif gph_id==4:
    for i in range(50):
        # sol.append(maxfirst(n=num_seeds,r=num_seeds))
        #
        sol.append(maxfirst(n=num_seeds,r=int(0.4*num_seeds),delete_node=2))
    for i in range(10):
        sol.append(maxfirst(n=num_seeds,r=num_seeds-2,delete_node=3))
    for i in range(7):
        sol.append(maxfirst(n=num_seeds, r=3, delete_node=1,random_draw=2))
    random.shuffle(sol)
else:
    for i in range(33):
        sol.append(maxfirst(n=num_seeds,r=int(0.4*num_seeds),delete_node=2))
    for i in range(10):
        sol.append(maxfirst(n=num_seeds,r=num_seeds-2,delete_node=3))
    for i in range(7):
        sol.append(maxfirst(n=num_seeds, r=3, delete_node=1,random_draw=3))
    random.shuffle(sol)

write_list_to_txt(sol, json_file_path)

time2=tm.time()
print("time:",time2-time1)