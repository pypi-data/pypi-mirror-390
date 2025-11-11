import json
import time
import math
from operator import index
import random
import numpy as np
import os

# =============================================================================
# DEBUG CONFIGURATION - Set to True to enable debug prints for this module
# =============================================================================
DEBUG = False

start_time = time.time()
if DEBUG:
    print('Start time is:', time.localtime())

class AntColony:
    def __init__(self, distance_matrix, time_matrix, benefit_matrix, all_keys, all_keys_benefit,info_weight_matrix,all_keys_info_weight,n_ants, n_best, n_iterations, decay, alpha, beta, optimization_objective, time_limit,route_type):
        self.distance_matrix = distance_matrix
        self.time_matrix = time_matrix
        self.benefit_matrix = benefit_matrix
        self.all_keys_benefit = all_keys_benefit
        self.all_keys_info_weight = all_keys_info_weight
        self.info_weight_matrix = info_weight_matrix
        self.all_keys_lookup = all_keys
        self.all_keys_list = list(all_keys)
        self.n_ants = n_ants
        self.n_best = n_best # this
        self.n_iterations = n_iterations
        self.decay = decay
        self.alpha = alpha
        self.beta = beta
        self.time_limit = time_limit
        self.optimization_objective = optimization_objective
        self.pheromone = {key: 1 for key in self.distance_matrix.keys()}
        self.route_type = route_type
        max_value = float('inf')
        min_value = float('-inf')
        #streamline normalizing the pheromone matrix!!!!!!!!!!!!!!!!!!
        if self.optimization_objective=='d': #for distance
            max_distance=max(value for value in self.distance_matrix.values() if value != max_value)
            self.normalized_distance = {key: value / max_distance for key, value in self.distance_matrix.items()}
            self.heuristic_info = {key: 1/value if value!=1 or value!=max_value else 1 for key, value in self.normalized_distance.items() }
        if self.optimization_objective=='t': #for time
            max_time=max(value for value in self.time_matrix.values() if value != max_value)
            self.normalized_time = {key: value / max_time for key, value in self.time_matrix.items()}
            self.heuristic_info = {key: 1/value if value!=1 or value!=max_value else 1 for key, value in self.normalized_time.items() } #for time
        if self.optimization_objective=='i': #for info
            max_info_weight = max(value for value in self.info_weight_matrix.values() if value != max_value)
            self.normalized_info_weight = {key: value / max_info_weight for key, value in self.info_weight_matrix.items()}
            self.heuristic_info = {key: 1/value if value!=1 or value!=max_value else 1 for key, value in self.normalized_info_weight.items() } #for benefits


    def run(self):
        shortest_path = None
        if self.optimization_objective=='d' or self.optimization_objective=='t':   #for distance, time
            all_time_shortest_path = ("placeholder", [float('inf'),float('inf'),float('-inf')])  #for distance, time
        else:
            all_time_shortest_path = ("placeholder", [float('inf'),float('inf'),float('-inf')]) #for benefits - use -inf for benefits to allow maximization
        for i in range(self.n_iterations):
            all_paths = self.gen_all_paths()
            
            # Check if all_paths is empty
            if not all_paths:
                print(f"Warning: No valid paths found in iteration {i}, skipping...")
                continue
                
            self.spread_pheromone(all_paths, shortest_path=shortest_path)
            
            # Initialize short_check
            short_check = False
            
            if self.optimization_objective=='d': #for distance
                shortest_path=min(all_paths,key=lambda x: x[1][0])
                short_check = shortest_path[1][0]<all_time_shortest_path[1][0]
            elif self.optimization_objective=='t': #for time
                shortest_path=min(all_paths,key=lambda x: x[1][1])
                short_check = shortest_path[1][1]<all_time_shortest_path[1][1]
            elif self.optimization_objective=='i': #for benefits
                shortest_path = max(all_paths, key=lambda x: x[1][2]) 
                short_check = shortest_path[1][2]>all_time_shortest_path[1][2]  # Changed < to > for benefits
            
            if short_check:
                all_time_shortest_path = shortest_path
                shortest_path = ([int(item) if isinstance(item, (int, float, np.integer)) else item for item in shortest_path[0]], shortest_path[1])
                if DEBUG:
                    print(i)
                    print(shortest_path)
                # if self.route_type=='b':
                #     if shortest_path[1][0] >=295 and shortest_path[1][0]<=300:
                #         print("break")
                #         break
            self.pheromone = self.evaporate_pheromone()
        return all_time_shortest_path

    def gen_all_paths(self):
        all_paths = []
        for i in range(self.n_ants):
            path = self.gen_path()
            if path[-1] is None:
                i-=1
                continue
            if 0<len(path)<len(self.all_keys_list):
                i-=1
                continue
            all_paths.append((path, self.gen_path_cost(path)))
        return all_paths

    def gen_path(self):
        path = []
        start = random.choice(list(self.all_keys_list))
        path.append(start)
        while len(path) < len(self.all_keys_list):
            next_node = self.pick_next_node(path[-1], path)
            #next_node=int(next_node)
            #print('next_node:', next_node)
            if next_node is None:
                path.append(next_node)
                break
            path.append(next_node)
        return path

    def pick_next_node(self, last_node, path):
        number_of_nodes = len(self.all_keys_list) + 1
        all_nodes = range(1, number_of_nodes)

        visited_nodes = set(path)
        unvisited_nodes = set(all_nodes) - visited_nodes

        if not unvisited_nodes:
            return None

        probabilities = []
        total = 0

        for node in unvisited_nodes:
            pheromone_level = self.pheromone.get((last_node, node), 0) ** self.alpha
            heuristic_level = self.heuristic_info.get((last_node, node), 0) ** self.beta
            prob = pheromone_level * heuristic_level
            probabilities.append((node, prob))
            total += prob

        if total == 0 or math.isnan(total):
            next_node = None
        else:
            probabilities = [(node, prob / total) for node, prob in probabilities]
            next_node = np.random.choice([node for node, prob in probabilities], p=[prob for node, prob in probabilities])
        return next_node

    def gen_path_cost(self, path):
        total_cost = 0
        total_time_cost = 0
        total_info_weight = 0
        max_value = float('inf')
        min_value = float('-inf')
        for i in range(len(path) - 1):
            path_length = len(path)-1
            if self.distance_matrix[path[i], path[i + 1]] != max_value:
                total_cost += self.distance_matrix[path[i], path[i + 1]]
                total_time_cost += self.time_matrix[path[i], path[i + 1]]
                total_info_weight += self.info_weight_matrix[path[i],path[i+1]]
                if total_time_cost>=self.time_limit:
                    total_time_cost-=self.time_matrix[path[i], path[i + 1]]
                    total_cost-=self.distance_matrix[path[i], path[i + 1]]
                    total_info_weight-=self.info_weight_matrix[path[i], path[i + 1]]
                    for j in range(i, path_length):
                        path.pop(-1)
                    break
        # if total_time_cost>self.time_limit:
        #     penalty_rate=0.99
        #     excess_time=total_time_cost-self.time_limit
        #     penalty=penalty_rate*excess_time
        #     if self.optimization_objective=='d': #for distance
        #         total_cost-=2*self.distance_matrix[path[i], path[i + 1]]
        #     if self.optimization_objective=='t': #for time
        #         total_time_cost-=2*self.time_matrix[path[i], path[i + 1]]
        #     if self.optimization_objective=='b': #for benefits
        #         total_benefit-=2*self.benefit_matrix[path[i], path[i + 1]] 
        return total_cost,total_time_cost,total_info_weight

    def spread_pheromone(self, all_paths, shortest_path):
        if not all_paths:
            return  # No paths to spread pheromone on
            
        if self.optimization_objective=='d': #for distance
            sorted_paths = sorted(all_paths, key=lambda x: x[1][0])
        elif self.optimization_objective=='t': #for time
            sorted_paths = sorted(all_paths, key=lambda x: x[1][1])
        elif self.optimization_objective=='i': #for benefits
            sorted_paths = sorted(all_paths, key=lambda x: x[1][2])
        else:
            sorted_paths = all_paths  # fallback
        
        for path, cost in sorted_paths[:self.n_best]:
            for i in range(len(path) - 1):
                if self.optimization_objective=='d': #for distance
                    self.pheromone[path[i], path[i + 1]] += self.normalized_distance[path[i], path[i + 1]]
                if self.optimization_objective=='t': #for time
                    self.pheromone[path[i], path[i + 1]] +=  self.normalized_time[path[i], path[i + 1]]
                if self.optimization_objective=='i': #for benefits
                    self.pheromone[path[i], path[i + 1]] +=  self.normalized_info_weight[path[i], path[i + 1]]
    

    def evaporate_pheromone(self):
        return {key: (1 - self.decay) * pheromone for key, pheromone in self.pheromone.items()}

# Initialize the ant colony

def real_path_generation(shortest_path, path_matrix_index, optimization_objective, maxIter, antNo, time_limit, class_number, segments_number_per_class, benefit_type,route_type):
    real_path = []
    path_segment_values = []  # Will store the segment values for each pair of points

    # Create a dictionary for fast lookup of segment value by (start_coord, end_coord)
    # We round coordinates to ensure consistency in comparison
    # segment_value_map = {}
    # for data in segment_values_data:
    #     # Rounding coordinates to 6 decimal places for consistency in matching
    #     start_coord = tuple(round(c, 6) for c in data['segment_start_coordinate'])
    #     end_coord = tuple(round(c, 6) for c in data['segment_end_coordinate'])
            
    #     # Add the segment values for both directions (start, end) and (end, start)
    #     segment_value_map[(start_coord, end_coord)] = data['segment_value']
    #     segment_value_map[(end_coord, start_coord)] = data['segment_value']  # Also handle reverse order

    # Process the shortest path to generate the real route and track segment values
    for i, node in enumerate(shortest_path[0]):
        if i < len(shortest_path[0]) - 1:
            next_node = shortest_path[0][i + 1]
        else:
            break

        # Check if the node pair exists in the path matrix
        if (node, next_node) in path_matrix_index:
            # Extend the real path with coordinates from the path matrix
            real_path.extend(path_matrix_index[node, next_node][:-1])

            # For each pair of consecutive coordinates in the segment, check the segment value
            for j in range(len(path_matrix_index[node, next_node]) - 1):
                coord_start = path_matrix_index[node, next_node][j]
                coord_end = path_matrix_index[node, next_node][j + 1]

                # Round coordinates to 6 decimal places to ensure consistency in comparison
                start_coord_tuple = tuple(round(c, 6) for c in coord_start)
                end_coord_tuple = tuple(round(c, 6) for c in coord_end)

                # # Look up the segment value for this coordinate pair (considering both directions)
                # segment_value = segment_value_map.get((start_coord_tuple, end_coord_tuple), 1)  # Default to 1 if not found

                # # Append the segment value (2 if the segment value is 2, 1 otherwise)
                # path_segment_values.append(segment_value)

    # Calculate the route's real distance, time, and benefit (if available in shortest_path)
    real_path_distance = shortest_path[1][0] if len(shortest_path) > 1 else None
    real_path_time = shortest_path[1][1] if len(shortest_path) > 1 else None
    real_path_info_weight = shortest_path[1][2] if len(shortest_path) > 1 else None

    # Prepare the final output dictionary with the real path and segment values
    real_route = {
        "Optimization Objective": optimization_objective,
        'Number of Iterations': maxIter,
        'Number of Ants': antNo,
        'Time Limit': time_limit,
        'Class number': class_number,
        'Distance': real_path_distance,
        'Time': real_path_time,
        'Info_weight': real_path_info_weight,
        'Segments number per Class': segments_number_per_class,
        'Benefit Type': benefit_type,
        "Route Type": route_type,
        'Number of Segments': len(real_path),
        'Path': real_path,
        #'Path Segment Values': path_segment_values  # List of segment values for each pair of coordinates
    }

    return real_route

def data_preprocessing(network_file_path, number_of_classes):
    with open(network_file_path, "r") as f:
        network_data = json.load(f)
    distance_matrix = {}
    benefit_matrix = {}
    info_weight_matrix = {}
    info_value_matrix = {}
    time_matrix = {}
    path_matrix = {}
    path_class_id = {}
    all_keys = {}
    distance_matrix_index = {}
    time_matrix_index = {}
    benefit_matrix_index = {}
    info_weight_matrix_index = {}
    info_value_matrix_index = {}
    all_keys_benefit_index = {}
    path_matrix_index = {}
    node_count = {}
    path_count = {}
    path_classes = []
    segments_in_class_number = {}
    first_segment_class={}
    second_segment_class={}
    segments_by_benefit = {}
    all_keys_count = 0
    all_keys_benefit = {}
    all_keys_info_weight = {}
    all_keys_info_weight_index = {}
    all_keys_info_value = {}
    all_keys_info_value_index = {}
    for data in network_data:
        start_road_id = data['start_road_id']
        start_segment_id = data['start_segment_id']
        actual_start= data['actual_segment_start_id']
        end_road_id = data['end_road_id']
        end_segment_id = data['end_segment_id']
        actual_end= data['actual_segment_end_id']
        key1 = actual_start
        key2 = actual_end
        class_count = 0
        segments_by_benefit[actual_start, actual_end] = {}
        for class_id in range(1, number_of_classes+1):
            segments_in_class_number[class_id] = 0
        for key, value in data['benefit'].items():
            segments_by_benefit[actual_start, actual_end][int(key)] = value
            if value!=0:
                path_classes.append(int(key))
                segments_in_class_number[int(key)] += 1
                if class_count == 0:
                    first_segment_class[actual_start, actual_end] = int(key)
                    class_count += 1
                else:
                    second_segment_class[actual_start, actual_end] = int(key)
        check_key1 = key1 in  all_keys.values()
        check_key2 = key2 in all_keys.values()
        if (check_key1==False or check_key2==False):
            #node_count[class_id] += 1
            all_keys_count += 1
            if check_key1==False and check_key2==True:
                all_keys[all_keys_count] = key1
            elif check_key1==True and check_key2==False:
                all_keys[all_keys_count] = key2
            else:
                all_keys[all_keys_count] = key1
                #node_count[class_id] += 1
                all_keys_count += 1
                all_keys[all_keys_count] = key2
        # else:   
        #     if class_id in desired_class:
        #         path_count[class_id] += 1
            #continue
        distance = data['distance']
        time_cost = data['time']
        benefit = 0
        info_weight = data['information_weight']
        info_value = data['information_value']
        info_weight_matrix[key1, key2] = info_weight
        info_value_matrix[key1, key2] = info_value
        
        for _,value in data['benefit'].items():
            benefit+=value
        start_segment_benefit=data['start_segment_benefit']
        end_segment_benefit=data['end_segment_benefit']
        #path_class_id[key1, key2] = data['path_class_id']
        start_segment_info_weight=data['start_segment_info_weight']
        end_segment_info_weight=data['end_segment_info_weight']
        start_segment_info_value=data['start_segment_info_value']
        end_segment_info_value=data['end_segment_info_value']
        path= data['path']
        path_matrix[key1, key2] = path
        distance_matrix[key1, key2] = distance
        benefit_matrix[key1, key2] = benefit
        time_matrix[key1, key2] = time_cost
        all_keys_benefit[key1]=start_segment_benefit
        all_keys_benefit[key2]=end_segment_benefit
        all_keys_info_weight[key1]=start_segment_info_weight
        all_keys_info_weight[key2]=end_segment_info_weight
        all_keys_info_value[key1]=start_segment_info_value
        all_keys_info_value[key2]=end_segment_info_value
    # sum_path = 0
    # sum_node = 0
    # sum_path = len(path_class_id)
    # for class_id in desired_class:
    #     #path_count[class_id] += node_count[class_id]
    #     sum_path += path_count[class_id]
    #     sum_node += node_count[class_id]
    inverse_all_keys = {v: k for k, v in all_keys.items()}
    for data in network_data:
        # class_id = data['path_class_id']
        # if class_id not in desired_class:
        #     continue
        start_road_id = data['start_road_id']
        start_segment_id = data['start_segment_id']
        actual_start= data['actual_segment_start_id']
        end_road_id = data['end_road_id']
        end_segment_id = data['end_segment_id']
        actual_end= data['actual_segment_end_id']
        key1 = actual_start
        key2 = actual_end
        if key1 in inverse_all_keys and key2 in inverse_all_keys:
            index1 = inverse_all_keys[key1]
            index2 = inverse_all_keys[key2]
            distance_matrix_index[index1, index2] = distance_matrix[key1, key2]
            time_matrix_index[index1, index2] = time_matrix[key1, key2]
            benefit_matrix_index[index1, index2] = benefit_matrix[key1, key2]
            info_weight_matrix_index[index1, index2] = info_weight_matrix[key1, key2]
            info_value_matrix_index[index1, index2] = info_value_matrix[key1, key2]
            path_matrix_index[index1, index2] = path_matrix[key1, key2]
            all_keys_benefit_index[index1]=all_keys_benefit[key1]
            all_keys_benefit_index[index2]=all_keys_benefit[key2]
            all_keys_info_weight_index[index1]=all_keys_info_weight[key1]
            all_keys_info_weight_index[index2]=all_keys_info_weight[key2]
            all_keys_info_value_index[index1]=all_keys_info_value[key1]
            all_keys_info_value_index[index2]=all_keys_info_value[key2]
    matrix_size = len(inverse_all_keys) + 1
    max_value = float('inf')
    min_value = float('-inf')
    for i in range(1, matrix_size):
        for j in range(1, matrix_size):
            if (i, j) not in distance_matrix_index or distance_matrix_index[i, j] == 1e+20:
                distance_matrix_index[i, j]=max_value
            if (i, j) not in time_matrix_index or time_matrix_index[i, j] == 1e+20:
                time_matrix_index[i, j]=max_value
            if (i, j) not in benefit_matrix_index or benefit_matrix_index[i, j] == -6e+20:
                benefit_matrix_index[i, j]=min_value
            if (i, j) not in info_weight_matrix_index or info_weight_matrix_index[i, j] == 1e+20:
                info_weight_matrix_index[i, j]=max_value
            if (i, j) not in info_value_matrix_index or info_value_matrix_index[i, j] == 1e+20:
                info_value_matrix_index[i, j]=min_value
            if (i, j) not in path_matrix_index:
                path_matrix_index[i, j] = []
    #print('All keys:', all_keys)
    # graph becomes disconnected using one way streets
    incidence_matrix = np.zeros((matrix_size, matrix_size))
    for i in range(1, matrix_size):
        for j in range(1, matrix_size):
            if distance_matrix_index[i, j] != max_value:
                incidence_matrix[i, j] = 1
    return distance_matrix_index, time_matrix_index, benefit_matrix_index, path_matrix_index, all_keys, all_keys_benefit_index, matrix_size, max_value, min_value,info_weight_matrix_index,all_keys_info_weight_index
    
def route_finding(working_directory, number_of_classes, time_limit, optimization_objective, max_iter, ant_no,segments_number_per_class, benefit_type, route_type):
    optimization_objective = 'd'  # 'd' for distance, 't' for time, 'i' for info
    workdir = os.path.join(os.getcwd(), working_directory)
    transient_dir=os.path.join(workdir, "transient")
    output_dir=os.path.join(workdir, "input")
    network_file_path = os.path.join(transient_dir, "pf_output.json")
    hull_file_path = os.path.join(transient_dir, "updated_point_hull.json")
    write_file_path = os.path.join(output_dir, "initial_route.json")
    
    maxIter = max_iter
    antNo = ant_no
    rho = 0.5  # Evaporation rate, [0, 1), default=0.5, best so far=0.5
    alpha = 0.35 # Pheromone factor, >=0, default=1, best so far=0.35
    beta = 5  # Attractiveness factor, >0, default=1, best so far>=1
    # beta>>alpha for best results

    distance_matrix, time_matrix, benefit_matrix, path_matrix, all_keys, all_keys_benefit, matrix_size, max_value, min_value,info_weight_matrix,all_keys_info_weight = data_preprocessing(network_file_path, number_of_classes)
    colony = AntColony(distance_matrix, time_matrix, benefit_matrix,all_keys,all_keys_benefit,info_weight_matrix,all_keys_info_weight, n_ants=antNo, n_best=5, n_iterations=maxIter, decay=rho, alpha=alpha, beta=beta, optimization_objective=optimization_objective, time_limit=time_limit,route_type=route_type)
    # Run the optimization
    shortest_path = colony.run()
    # with open(hull_file_path, "r") as f:
    #     hull_data = json.load(f)
    real_route = real_path_generation(shortest_path, path_matrix, optimization_objective, maxIter, antNo, time_limit, number_of_classes,segments_number_per_class, benefit_type,route_type)
    # with open(write_file_path, "w") as f:
    #     json.dump(real_route, f, indent=4)
    # debug_path=os.path.join(transient_dir, "debug")
    with open(write_file_path, "w") as f:
        json.dump(real_route, f, indent=4)
    end_time = time.time()
    execution_time = end_time - start_time
    if DEBUG:
        print("Execution time:", execution_time, "seconds")
        execution_time_minutes = execution_time / 60
        print("Execution time:", execution_time_minutes, "minutes")
        print("done")
    return shortest_path


if __name__ == "__main__":
    route_finding(
        working_directory='work_dir/minimal_test',
        number_of_classes=15,
        time_limit=80,
        optimization_objective='d',
        max_iter=150,
        ant_no=500,
        segments_number_per_class=1,
        benefit_type='t',
        route_type='g'
    )