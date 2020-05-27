from functions import *
from skimage.color import rgb2gray
from skimage import exposure
import itertools
import networkx as nx
from sklearn.preprocessing import MinMaxScaler

def get_blobs (image,nb_blobs):
    from skimage.feature import blob_log
    #returns list of Y,X coordinates and approximate radii of blobs detected
    #removes blobs that are far away until only nb_blobs are left (x and y are switched!!)
    
    image_gray = rgb2gray(image)

    #preprocessing: contrast stretching
    p2, p98 = np.percentile(image_gray, (2, 98))
    image_gray = exposure.rescale_intensity(image_gray, in_range=(p2, p98))


    #blob detection
    blobs_log = blob_log(image_gray, min_sigma = 15, max_sigma=25, num_sigma=5, threshold=.12)

    # comp approximated radii in the 3rd col
    blobs_log[:, 2] = blobs_log[:, 2] * sqrt(2)

    while len(blobs_log) > nb_blobs:
        distances = np.zeros((len(blobs_log), 2))
        for i, blob in enumerate(blobs_log):
            distances[i][0] = int(i)
            y1,x1,r = blob
            for n in range (i,len(blobs_log)):
                y2,x2, r = blobs_log[n]
                dist = distance((x1,y1),(x2,y2))

                distances[i][1] += dist
                distances[n][1] += dist
        distances = distances[distances[:, 1].argsort()][:len(distances)]
        last = int(distances[len(distances)-1][0])
        blobs_log = np.delete(blobs_log,last, axis=0)
    return blobs_log

def blob_dist(blob1, blob2):
    return distance(blob1[0:2], blob2[0:2])

def blobs_in_range(center, blobs, max_range):
    #check which blobs are inside of range
    blobs_in_range = []
    for i, blob in enumerate(blobs):
        if dist(center,blob)<= max_range:
            blobs_in_range.append(i)
    return blobs_in_range

def blob_angle(blob1, blob2, blob3):
    x1, y1, r = blob1
    x2, y2, r = blob2
    x3, y3, r = blob3    
    v1_x = x2 - x1
    v1_y = y2 - y1
    v2_x = x3 - x2
    v2_y = y3 - y2    
    return angle((v1_x,v1_y),(v2_x,v2_y))

def remove_unconnected(graph):
    #removes subgraphs that have <12 nodes as they cannot be our electrodes
    components_generator = nx.connected_components(graph)
    components = [graph.subgraph(c).copy() for c in components_generator]
    for component in components:
        if len(component)<12:
            graph.remove_nodes_from(component.nodes)
    return graph
    #draw_graph(S[0],pos)

def dist_var_of_path(blobs, path):
    dists = []
    route_edges = [(path[n],path[n+1]) for n in range(len(path)-1)]
    for a,b in route_edges:
        dists.append(blob_dist(blobs[a,:],blobs[b,:]))
    return np.var(dists)  

def path_compactness(blobs, path):
    coordinates = blobs[path,0:2]
    x_mean = np.mean(coordinates[:,0])
    y_mean = np.mean(coordinates[:,1])
    distances = [distance((x_mean,y_mean), node) for node in coordinates]
    return np.sum(distances)

def get_next_possible_neigbours(graph_full, graph_left, path_chosen, blobs):
    #graph_full: the whole graph
    #graph_left: the part of the graph that is still available
    #path_chosen: list of nodes that make up this path: [starting node, ... , end node]
    if len(path_chosen)==12:
        return [path_chosen]
    paths_chosen = []
    CI_upper_border=find_confidence(gt_distances_angles1_and11(image_names_gt())[1], 'angle 1', create_plot=False)[1]
    CI_lower_border=find_confidence(gt_distances_angles1_and11(image_names_gt())[2], 'angle 11', create_plot=False)[0]
    for neighbor in graph_left.neighbors(path_chosen[-1]):
        blob1 = blobs[neighbor,:]
        blob2 = blobs[path_chosen[-1],:]
        blob3 = blobs[path_chosen[-2],:]
        this_angle = blob_angle(blob1, blob2, blob3)
        if CI_lower_border<this_angle < CI_upper_border:
            #we've found a possible neighbor!
            new_graph_full = graph_full.copy()
            new_graph_left = graph_left.copy()
            new_graph_left.remove_node(path_chosen[-1])
            new_path_chosen = path_chosen.copy()
            new_path_chosen.append(neighbor)
            #call the function recursively with the updated path
            recursive_return = get_next_possible_neigbours(new_graph_full, new_graph_left, new_path_chosen, blobs)
            for solution in recursive_return:
                paths_chosen.append(solution)
    return paths_chosen
         

def angle_difference(path,blobs):
    for n in range(len(path)-2):
        blob1 = blobs[n,:]
        blob2 = blobs[n+1,:]
        blob3 = blobs[n+2,:]
        this_angle = blob_angle(blob1, blob2, blob3)
        print(this_angle)

def path_likelihood(path,blobs,variances,compactness):
    mat = np.zeros((len(variances),2)) 
    mat[:,0]= variances
    mat[:,1]=compactness
    scaler = MinMaxScaler(feature_range = (0,1))
    scaler.fit(mat)    
    mat = scaler.transform(mat)
    variances = mat[:,0]
    compactness = mat[:,1]
    
    # argmin(sqrt(var^2+compactness^2))
    variances_2 = np.square(variances)
    compactness_2 = np.square(compactness)
    combined = np.sqrt(np.add(variances_2,compactness_2))
    best_path = np.argmin(combined)   
    return best_path

def output(blobs, path):
    
    coordinates = blobs[path,0:2]
    y_mean = np.mean(coordinates[:,0])
    x_mean = np.mean(coordinates[:,1])
    
    node_f = distance(blobs[path[0]][0:2],(y_mean,x_mean))
    node_l = distance(blobs[path[-1]][0:2],(y_mean,x_mean))
    
    #electrode 1 is innermost, electrode 12 is outermost
    if node_f > node_l: #if first node is further away from center of mass
        #flip the order of electrodes
        path = np.flip(path)
    output = np.zeros((12,3))
    output[:,0] = range(1,13)
    for i, elect in enumerate(path):
        y,x,sigma=blobs[elect]
        output[i,1] = x
        output[i,2] = y 
    return output
    

def find_electrodes(input_image):
    ### INPUT: AN IMAGE (post scan with electrodes) 
        #e.g
        #allpost, allpre, basenames = load("DATA")
        #find_electrodes(allpost[1])

    ### OUTPUT: A matrix with coordinates and order of electrodes

    blobs = get_blobs(input_image,20)
    graph = nx.Graph()
    graph.add_nodes_from(dict(enumerate(blobs)))

    pos = {}
    for i,blob in enumerate(blobs):
        graph.nodes[i]['pos'] = (blob[0],blob[1])
        pos.update({i:(blob[1],blob[0])})

    pairwise_combinations = list(itertools.combinations(range(len(blobs)), 2))
    CI =find_confidence(gt_distances_angles1_and11(image_names_gt())[0], 'distances',create_plot=False)
    for i, j in pairwise_combinations:
        blob_a = blobs[i]
        blob_b = blobs[j]
        dist = blob_dist(blob_a, blob_b)
        if CI[0] <dist < CI[1]:
            graph.add_edge(i, j, length=dist)

    graph = remove_unconnected(graph)
    paths = []
    for node in graph.nodes():
        for neighbor in graph.neighbors(node):
            start = [node,neighbor]
            graph_new = graph.copy()
            graph_new.remove_node(node)
            solutions = get_next_possible_neigbours(graph, graph_new, start, blobs)
            for solution in solutions:
                    paths.append(solution)

    variances = [dist_var_of_path(blobs, path) for path in paths]
    compactness = [2*path_compactness(blobs, path) for path in paths]

    best_path_ind = path_likelihood(paths,blobs,variances,compactness)
    path = paths[best_path_ind]
    to_return = output(blobs,path)

    return to_return

allpost, allpre = load("DATA")
result = find_electrodes(allpost[1])
print(result)