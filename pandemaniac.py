import json
import networkx as nx
import time as tm
import random
import numpy as np

time1=tm.time()

json_file_path = "RR.5.1.json"

def read_graph_from_json(json_file_path):
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    # Create an undirected graph using NetworkX
    graph = nx.Graph(data)
    return graph

''' competition: 'J'(tournament) or 'RR'(individuals) '''
def extract_info_from_graph_name(graph_name):
    components = graph_name.split('.')
    competition = components[0]
    num_seeds = int(components[1])
    unique_id = int(components[2])
    return competition, num_seeds, unique_id

graph_name = json_file_path  
gph = read_graph_from_json(json_file_path)
competition, num_seeds, unique_id = extract_info_from_graph_name(graph_name)

'''
1:erdos renyi, 2:preferential attachment  3: ssbm  4: caltech  5:stanford 
'''
if competition == 'RR':
    gph_id=unique_id//10
    # print("Graph ID:", gph_id)
if competition == 'J':
    gph_id=unique_id//10 + 2
    # print("Graph ID:", gph_id)

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
    return (deg-2)**1.5

#strategies based on max degree nodes
def maxfirst(n,r,delete_node=1,random_draw=None, random_thrs=2):
    '''
    :param n:
    :param r:
    :param delete_node:
    :param random_draw: int, number of random drawn nodes
    :param random_thrs:
    :return:
    '''
    #a=[sorted_nodes_by_degree[i]for i in range(r)]
    #incorporate centrality
    combined_scores = combined_centrality_score(g)  # Calculate combined centrality scores
    a = select_seed_nodes(g, r, combined_scores)
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

def trapmax(n,r=0,max_nb=[2,3],jungle=False,max_thrd=0.4,delete_node=1,random_draw=0, random_thrs=2):
    centrality_scores = combined_centrality_score(g)
    
    # Sort nodes by combined centrality score
    sorted_by_centrality = sorted(g.nodes(), key=lambda x: centrality_scores[x], reverse=True)
    
    # Use the top nodes based on the centrality score
    maxlist = sorted_by_centrality[:int(max_thrd * n)]
    a = [maxlist[0]]
    if g.has_edge(sorted_nodes_by_degree[0],sorted_nodes_by_degree[1]):
        temp=list(set.union(set(g.neighbors(sorted_nodes_by_degree[0])),set(g.neighbors(sorted_nodes_by_degree[1]))))
        if len(temp)<max_nb[1]:
            a.extend(temp)
        else:
            sort_temp=sorted(temp, key=lambda x: g.degree(x), reverse=True)
            if jungle:
                for i in range(len(sort_temp)):
                    if sort_temp[i] in maxlist:
                        continue
                    if len(a)==max_nb[1]:
                        break
                    a.append(sort_temp[i])

            a.extend(sort_temp[:max_nb[1]])
    else:
        temp=list(g.neighbors(sorted_nodes_by_degree[0]))
        if len(temp)<max_nb[0]:
            a.extend(temp)
        else:
            sort_temp=sorted(temp, key=lambda x: g.degree(x), reverse=True)
            if jungle:
                for i in range(len(sort_temp)):
                    if sort_temp[i] in maxlist:
                        continue
                    if len(a)==max_nb[0]:
                        break
                    a.append(sort_temp[i])

            a.extend(sort_temp[:max_nb[0]])
    a=set(a)
    a.union(set(sorted_nodes_by_degree[:r]))

    ###
    r_left = n -len(a)
    if r_left==0:
        return list(a)
    if random_draw>=r_left:

        random_draw=r_left
        r_left=0
    else:
        r_left-=random_draw
    gg = g.copy()
    aa = sorted_nodes_by_degree[:delete_node]

    subgraph_nodes = aa + list(set.union(*[set(gg.neighbors(node)) for node in aa]))

    nodes_to_remove = list(gg.subgraph(subgraph_nodes).nodes())

    gg.remove_nodes_from(nodes_to_remove)
    # subgraph_aa_and_neighbors = gg.subgraph(aa + list(set.union(*[set(gg.neighbors(node)) for node in aa])))
    # gg.remove_nodes_from(subgraph_aa_and_neighbors.nodes())
    sort2 = sorted(gg.nodes(), key=lambda x: gg.degree(x), reverse=True)
    for i in sort2:
        if r_left == 0:
            break
        if i not in a:
            a.add(i)
            r_left -= 1
    # a = set(a)
    selected_nodes = [node for node in sort2 if g.degree(node) > random_thrs]
    prob = {node: rank_deg(g.degree(node)) for node in selected_nodes}
    total_prob = sum(prob.values())
    normalized_prob = {node: prb / total_prob for node, prb in prob.items()}
    ii = 0
    while len(a) < n and ii < 10:
        rr = n - len(a)
        random_selected_nodes = random.choices(list(normalized_prob.keys()), weights=list(normalized_prob.values()),
                                               k=min(rr, len(selected_nodes)))
        a.update(random_selected_nodes)
        ii += 1
    if len(a) < n:
        g_a = gg.subgraph(a)
        gg.remove_nodes_from(g_a.nodes())
        sort2 = sorted(gg.nodes(), key=lambda x: gg.degree(x), reverse=True)
        rr = n - len(a)
        a.update(sort2[:rr])
    return list(a)

#centrality measures
betweenness = nx.betweenness_centrality(g)
closeness = nx.closeness_centrality(g)
eigenvector = nx.eigenvector_centrality(g, max_iter=1000)

def combined_centrality_score(g, bet_weight=1.0, close_weight=1.0, eig_weight=1.0):
    bet = nx.betweenness_centrality(g)
    close = nx.closeness_centrality(g)
    eig = nx.eigenvector_centrality(g, max_iter=1000)
    
    combined_scores = {}
    for node in g.nodes():
        combined_scores[node] = (bet_weight * bet[node] +
                                 close_weight * close[node] +
                                 eig_weight * eig[node])
    return combined_scores

def select_seed_nodes(g, num_seeds, combined_scores):
    sorted_nodes = sorted(combined_scores, key=combined_scores.get, reverse=True)
    seed_nodes = sorted_nodes[:num_seeds]
    return seed_nodes

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
if competition=='RR':
    if gph_id==1 or gph_id==2:
        for i in range(16):
            sol.append((trapmax(n=num_seeds,r=1,delete_node=1,max_nb=[2,3],jungle=False,random_draw=0)))
        for i in range(16):
            sol.append((trapmax(n=num_seeds,r=0,delete_node=1,max_nb=[2,3],jungle=False,random_draw=1)))

        for i in range(10):
            sol.append(maxfirst(n=num_seeds,r=2,delete_node=1,random_draw=int(0.4*num_seeds)))
        for i in range(8):
            sol.append(maxfirst(n=num_seeds,r=1,delete_node=1,random_draw=num_seeds-3))
        # for i in range(7):
        #     sol.append(maxfirst(n=num_seeds, r=2, delete_node=1,random_draw=2))
        random.shuffle(sol)
    elif gph_id==3:
        for i in range(20):
            sol.append((trapmax(n=num_seeds, r=3, delete_node=1, max_nb=[2, 3], jungle=False, random_draw=2)))
        for i in range(15):
            sol.append((trapmax(n=num_seeds, r=0, delete_node=1, max_nb=[3, 4], jungle=False, random_draw=int(0.2*num_seeds))))

        for i in range(10):
            sol.append(maxfirst(n=num_seeds, r=3, delete_node=1, random_draw=int(0.4 * num_seeds)))
        for i in range(5):
            sol.append(maxfirst(n=num_seeds, r=1, delete_node=1, random_draw=num_seeds - 3))
        random.shuffle(sol)
    elif gph_id==4:
        for i in range(32):
            # sol.append(maxfirst(n=num_seeds,r=num_seeds))
            #
            sol.append(maxfirst(n=num_seeds,r=int(0.4*num_seeds),delete_node=2))
        for i in range(8):
            sol.append(maxfirst(n=num_seeds,r=int(0.6*num_seeds),delete_node=3))
        for i in range(10):
            sol.append(maxfirst(n=num_seeds, r=3, delete_node=1,random_draw=2))
        random.shuffle(sol)
    else:
        for i in range(33):
            sol.append(maxfirst(n=num_seeds,r=int(0.4*num_seeds),delete_node=2))
        for i in range(10):
            sol.append(maxfirst(n=num_seeds,r=int(0.6*num_seeds),delete_node=3))
        for i in range(7):
            sol.append(maxfirst(n=num_seeds, r=3, delete_node=1,random_draw=3))
        random.shuffle(sol)
else:
    if gph_id==1:
        for i in range(18):
            sol.append((trapmax(n=num_seeds,r=0,delete_node=1,max_nb=[3,4],jungle=True,random_draw=1)))
        for i in range(16):
            sol.append((trapmax(n=num_seeds,r=0,delete_node=1,max_nb=[3,4],jungle=True,random_draw=0)))
        for i in range(16):
            sol.append((trapmax(n=num_seeds,r=0,delete_node=1,max_nb=[3,4],jungle=True,random_draw=int(0.3*num_seeds))))

        random.shuffle(sol)
    elif gph_id==2:
        for i in range(20):
            sol.append((trapmax(n=num_seeds,r=0,delete_node=1,max_nb=[3,4],jungle=True,random_draw=int(0.2*num_seeds))))
        for i in range(25):
            sol.append((trapmax(n=num_seeds,r=0,delete_node=2,max_nb=[4,5],jungle=True,random_draw=int(0.5*num_seeds))))
        for i in range(5):
            sol.append((trapmax(n=num_seeds,r=0,delete_node=1,max_nb=[3,4],jungle=True,random_draw=int(0.3*num_seeds))))

        random.shuffle(sol)
    elif gph_id==3:
        for i in range(20):
            sol.append((trapmax(n=num_seeds, r=0, delete_node=1, max_nb=[3, 4], jungle=True,
                                random_draw=int(0.2 * num_seeds))))
        for i in range(25):
            sol.append((trapmax(n=num_seeds, r=0, delete_node=2, max_nb=[4, 5], jungle=True,
                                random_draw=int(0.5 * num_seeds))))
        for i in range(5):
            sol.append((trapmax(n=num_seeds, r=0, delete_node=1, max_nb=[3, 4], jungle=True,
                                random_draw=int(0.3 * num_seeds))))
        random.shuffle(sol)
    else:
        for i in range(33):
            sol.append(maxfirst(n=num_seeds,r=int(0.4*num_seeds),delete_node=2))
        for i in range(10):
            sol.append(maxfirst(n=num_seeds,r=int(0.6*num_seeds),delete_node=3))
        for i in range(7):
            sol.append(maxfirst(n=num_seeds, r=3, delete_node=1,random_draw=3))
        random.shuffle(sol)

write_list_to_txt(sol, json_file_path)

time2=tm.time()
print("time:",time2-time1)