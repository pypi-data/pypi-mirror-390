import networkx as nx
import json
import time
import math
from collections import defaultdict
import copy
import os
import glob

# =============================================================================
# DEBUG CONFIGURATION - Set to True to enable debug prints for this module
# =============================================================================
DEBUG = False

# Constants
# MAX_DISTANCE = 50

start_time = time.time()
if DEBUG:
    print("path finding started")
# Load network and benefits data
def load_data(path):
    with open(path, "r") as f:
        data = json.load(f)
    return data

# def load_data(network_file_path, benefits_file_path, hull_file_path):
#     with open(network_file_path, "r") as b:
#         roads_data = json.load(b)
#     with open(benefits_file_path, "r") as f:
#         benefits_data = json.load(f)
#     benefits_data = benefits_data[1:]
#     with open(hull_file_path, "r") as f:
#         hull_data = json.load(f)   
#     return roads_data, benefits_data, hull_data

# Calculate distance between two coordinates
def calculate_distance(point1, point2):
    dx = point2[0] - point1[0]
    dy = point2[1] - point1[1]
    return math.sqrt(dx ** 2 + dy ** 2)

def distance_heuristic(point1, point2):
    dx = point2[0] - point1[0]
    dy = point2[1] - point1[1]
    return math.sqrt(dx ** 2 + dy ** 2)/1000  # Convert to km

import math

def build_information_grid(structured_data,route_type, cell_size=250):
    # Initialize an empty dictionary to store grid information
    grid = {}
    start_time = time.time()
    # Loop through structured data to extract segment information
    for road_id, road_data in structured_data.items():
        for segment_id, segment_data in road_data['segments'].items():
            # Extract the segment start coordinates and information value
            x, y = segment_data['segment_start_coordinate']
            
            if route_type == 'b':
                info_weight = segment_data['information_value']
            else:
                info_weight = segment_data['information_weight']
            # Convert coordinates to grid cell indices
            cell_x = math.floor(x / cell_size)
            cell_y = math.floor(y / cell_size)

            # Update grid with information value for the corresponding cell
            if (cell_x, cell_y) not in grid:
                grid[(cell_x, cell_y)] = []
            if info_weight == math.inf:
                info_weight = 1
            grid[(cell_x, cell_y)].append(info_weight)

    # Optionally calculate the average information value per cell
    for cell, values in grid.items():
        # summ = sum(value for value in values if value != 1)
        # lenn = len([value for value in values if value != 1])
        # if summ == 0 or lenn == 0:
        #     grid[cell] = 1
        # else:
        #     grid[cell] = summ/lenn
        grid[cell] = sum(values) / len(values) if values else 1  # Avoid division by zero
    
    if DEBUG:
        print("Grid built in", time.time() - start_time, "seconds")
    return grid





# def information_heuristic(current_node_coord, goal_node_coord, info_grid, cell_size=10, use_euclidean=True):
#     # Convert current and goal coordinates to grid cells
#     cx, cy = math.floor(current_node_coord[0] / cell_size), math.floor(current_node_coord[1] / cell_size)
#     gx, gy = math.floor(goal_node_coord[0] / cell_size), math.floor(goal_node_coord[1] / cell_size)

#     # Choose distance metric: Manhattan or Euclidean
#     if use_euclidean:
#         # Euclidean distance (more realistic for most cases)
#         dx = current_node_coord[0] - goal_node_coord[0]
#         dy = current_node_coord[1] - goal_node_coord[1]
#         distance_cells = math.sqrt(dx**2 + dy**2)
#     else:
#         # Manhattan distance
#         distance_cells = abs(cx - gx) + abs(cy - gy)

#     # Average information value in the grid (use the current cell's info value as well)
#     avg_info = (info_grid.get((cx, cy), 1) + info_grid.get((gx, gy), 1)) / 2
#     distance_cells = distance_cells/1000  # Convert to km
#     # Avoid division by zero by setting a small value for avg_info
#     if distance_cells == 0:
#         distance_cells = 0.001  # to avoid division by zero

#     # Heuristic is inversely proportional to the average information value
#     # heuristic = distance_cells / avg_info
#     # heuristic = avg_info*distance_cells
#     # heuristic = distance_cells
#     heuristic = avg_info

#     return heuristic

def information_heuristic(current_node_coord, goal_node_coord, info_grid, cell_size=10, step_size=10):
    """
    Heuristic for A* that favors paths through high-information areas.
    Since info_weight is inverted (lower = better), this returns lower values for high-info paths.
    
    Args:
        current_node_coord: Current position (x, y)
        goal_node_coord: Goal position (x, y)
        info_grid: Dictionary mapping (cell_x, cell_y) to average info_weight
        cell_size: Size of grid cells in meters (default 250m to match build_information_grid)
        step_size: Distance between samples along the line (default 100m)
    
    Returns:
        Estimated cost: distance * avg_info_weight (lower for high-info areas)
    """
    x0, y0 = current_node_coord
    x1, y1 = goal_node_coord

    dx = x1 - x0
    dy = y1 - y0
    distance_m = math.hypot(dx, dy)
    distance_km = distance_m / 1000

    if distance_m == 0:
        return 0

    # Sample info_weights along the line from current to goal
    steps = max(int(distance_m / step_size), 1)
    info_weights = []

    for i in range(steps + 1):
        t = i / steps
        x = x0 + t * dx
        y = y0 + t * dy
        cell = (int(x // cell_size), int(y // cell_size))
        weight = info_grid.get(cell, 1.0)  # Default to 1.0 (neutral) if cell not in grid
        info_weights.append(weight)

    # Average info_weight along the path
    # Lower avg_weight = higher information = better path = lower heuristic cost
    avg_weight = sum(info_weights) / len(info_weights)
    
    # Return distance weighted by information: favors shorter paths through high-info areas
    #return distance_km * avg_weight
    return 0

def time_heuristic(current_node_coord, goal_node_coord):
    return calculate_distance(current_node_coord, goal_node_coord) / 100  # Convert to hours (100 km/h speed)


def determine_maxspeed(highway_type, maxspeed_value,zone_type):
    """Determine the maximum speed for a given road type and maxspeed value."""
        
    if maxspeed_value and maxspeed_value != None:
        maxspeed = int(maxspeed_value)
    elif highway_type == "motorway":
        maxspeed = 130
    else:
        if zone_type == "DE:rural":
            maxspeed = 100
        else:
            maxspeed = 50

    return maxspeed 


def restructure_osm_data(osm_file, benefit_data):
    restructured_data = {}

    # Load OSM data
    with open(osm_file, "r") as f:
        osm_data = json.load(f)

    # Load benefit data
    

    for road in osm_data["features"]:
        if road['properties']['nodes']=='nan':
            continue
        road_id = str(road["properties"]["osmid"])
        highway_type = road["properties"].get("highway", "")
        maxspeed_value = road["properties"].get("maxspeed", None)
        if maxspeed_value == "none":
            maxspeed_value = None
        # Initialize total_benefit with default values
        total_benefit = {str(i): 0 for i in range(1, 10)}

        # If the road has benefit data, update total_benefit
        if road_id in benefit_data:
            total_benefit.update(benefit_data[road_id].get("total_benefit", {}))

        road_data = {
            "id": road_id,
            "name": road["properties"].get("name", ""),
            "maxspeed": determine_maxspeed(highway_type, maxspeed_value,road["properties"].get("source:maxspeed", "")),
            "is_oneway": 1 if road["properties"].get("oneway") in ["yes", "1", "true"] else 0,
            "highway_type": highway_type,
            "total_benefit": total_benefit,  
            "segments": {}
        }

        coordinates = road["geometry"]["coordinates"]
        
        for i in range(len(coordinates) - 1):
            segment_id = str(i + 1)
            segment_data = {
                "segment_start_id": road["properties"]["nodes"][i],
                "segment_end_id": road["properties"]["nodes"][i + 1],
                "segment_start_coordinate": coordinates[i],
                "segment_end_coordinate": coordinates[i + 1],
                "number_of_points": 0,
                "points": {},
                "benefit": {str(i): 0 for i in range(1, 10)},
                'information_value': 0,
                'information_weight': 1
            }

            # If benefit data exists for this road and segment, update benefit values
            if road_id in benefit_data and "segments" in benefit_data[road_id]:
                segment_benefits = benefit_data[road_id]["segments"].get(segment_id, {}).get("benefit", {})
                segment_data["benefit"].update(segment_benefits)
                segment_data["number_of_points"] = benefit_data[road_id]["segments"].get(segment_id, {}).get("number_of_points", 0)
                segment_data["points"] = benefit_data[road_id]["segments"].get(segment_id, {}).get("points", {})
                segment_data["information_value"] = benefit_data[road_id]["segments"].get(segment_id, {}).get("information_value", 0)
                segment_data["information_weight"] = benefit_data[road_id]["segments"].get(segment_id, {}).get("information_weight", 1)
                # if segment_data["information_value"] != math.inf:
                #     print("here value", segment_data["number_of_points"])
                # else:
                #     print("here inf", segment_data["number_of_points"])
            road_data["segments"][segment_id] = segment_data

        restructured_data[road_id] = road_data

    return restructured_data


# Build directed graph from roads data
def build_road_network(roads_data):
    road_network = nx.DiGraph()
    for road_id, road_data in roads_data.items():
        max_speed = road_data["maxspeed"]
        segments = road_data["segments"]
        is_oneway = road_data["is_oneway"]
        for segment_id, segment_info in segments.items():
            start = tuple(segment_info["segment_start_coordinate"])
            end = tuple(segment_info["segment_end_coordinate"])
            length = calculate_distance(start, end) / 1000  # in km
            time_cost = length / max_speed  # time = distance / speed
            benefit = segment_info["benefit"]
            class_id = int(max(benefit.items(), key=lambda x: x[1])[0])
            minus_benefit = 1-(benefit[str(class_id)])
            info_weight = segment_info["information_weight"]
            info_value = segment_info["information_value"]
            is_motorway = 1 if road_data["highway_type"] == "motorway" else 0
            road_network.add_edge(start, end, road=road_id, segment=segment_id, benefit=benefit,
                                  distance=length, time_cost=time_cost, class_id=class_id, minus_benefit=minus_benefit,information_weight=info_weight,information_value=info_value, is_motorway=is_motorway)
            if not is_oneway:
                road_network.add_edge(end, start, road=road_id, segment=segment_id, benefit=benefit,
                                      distance=length, time_cost=time_cost, class_id=class_id, minus_benefit=minus_benefit,information_weight=info_weight,information_value=info_value, is_motorway=is_motorway)
    return road_network

# Is the segment valid?
def is_valid_segment(graph, node1, node2):
    return graph.has_edge(node1, node2)


class TimeoutException(Exception):
    pass

# def run_astar_with_timeout(road_network, start, end, info_grid,route_type,timeout=2):
#     """Runs A* with a manual timeout using the modified astar_generator."""
#     start_time = time.time()  # Start the timer

#     try:
#         # Run A* search and check for timeout
#         for path in astar_generator(road_network, start, end,info_grid, route_type):
#             if path is not None:  # Path found
#                 return path
#             if time.time() - start_time > timeout:  # Timeout occurred
#                 print(f"Timeout occurred for start: {start}, end: {end}")
#                 return None
#     except nx.NetworkXNoPath:
#         print(f"No path found for start: {start}, end: {end}")
#         return None  # No path found

import heapq
# # newest version (before 28.04)
# def astar_generator(road_network, start, end, route_type, heuristic=calculate_distance, weight='information_weight', timeout=2):
#     """Generator function to allow manual timeout checking during A* search."""
#     start_time = time.time()  # Start the timer
#     # if route_type == 'b':
#     #     weight = 'distance'
#     # Initialize data structures for A* search
#     open_set = []
#     heapq.heappush(open_set, (0, start))  # Priority queue with (f_score, node)
#     came_from = {}
#     g_score = {start: 0}  # Cost from start to each node
#     f_score = {start: heuristic(start, end)}  # Estimated total cost

#     while open_set:
#         # Check for timeout
#         if time.time() - start_time > timeout:
#             print(f"Timeout occurred while searching for path from {start} to {end}.")
#             yield None  # Timeout occurred
#             return

#         # Get the node with the lowest f_score
#         current_f, current = heapq.heappop(open_set)

#         # If the goal is reached, reconstruct the path
#         if current == end:
#             path = [current]
#             while current in came_from:
#                 current = came_from[current]
#                 path.append(current)
#                 if len(path) > 10000:
#                     print("Path too long, stopping.")
#                     return None
#             yield list(reversed(path))  # Return the path
#             return

#         # Explore neighbors
#         for neighbor in road_network.neighbors(current):
#             tentative_g = g_score[current] + road_network[current][neighbor].get(weight, 1)
#             if neighbor not in g_score or tentative_g < g_score[neighbor]:
#                 came_from[neighbor] = current
#                 g_score[neighbor] = tentative_g
#                 f_score[neighbor] = tentative_g + heuristic(neighbor, end)
#                 heapq.heappush(open_set, (f_score[neighbor], neighbor))

#         # Yield control to allow timeout checking
#         yield None

def astar_generator(road_network, start_id, end_id, info_grid, route_type, optimization_objective, heuristic=information_heuristic, weight='information_weight', timeout=9999, cell_size=250):
    """
    A* path generator that selects heuristic and edge weight based on optimization objective.
    
    Args:
        cell_size: Must match the cell_size used in build_information_grid (default 250m)
    """
    heuristic = lambda u, v: 0
    if route_type == 'b':
        weight = 'information_value'
    # weight='distance'
    if optimization_objective == 't':
        weight = 'time_cost'
        heuristic = time_heuristic
    elif optimization_objective == 'd':
        weight = 'distance'
        heuristic = distance_heuristic
    else:
        # Information-based optimization: minimize info_weight (favor high-info areas)
        weight = 'information_weight'
        heuristic = lambda u, v: 0
        
    try:
        path = nx.astar_path(road_network, source=start_id, target=end_id, heuristic=heuristic, weight=weight)
    except nx.NetworkXNoPath:
        if DEBUG:
            print(f"No path found from {start_id} to {end_id}.")
        yield None
    yield path

#NEW NEW (on 28.04)
import heapq
import time
import math

# def astar_generator(road_network, start_id, end_id, info_grid, route_type, heuristic=information_heuristic, weight='information_weight', timeout=9999, cell_size=10):
#     """A* generator for road segments based on information_weight or other criteria."""
#     start_time = time.time()

#     if route_type == 'b':
#         weight = 'information_value'
    
#     open_set = []
#     heapq.heappush(open_set, (0, start_id))

#     came_from = {}
#     g_score = {start_id: 0}
#     f_score = {start_id: heuristic(start_id, end_id, info_grid, cell_size)}  # Initial heuristic score for the start

#     # Precompute the heuristic values for the start and goal cells
#     start_cell = (math.floor(start_id[0] / cell_size), math.floor(start_id[1] / cell_size))
#     end_cell = (math.floor(end_id[0] / cell_size), math.floor(end_id[1] / cell_size))
#     start_info = info_grid.get(start_cell, 0)
#     end_info = info_grid.get(end_cell, 0)

#     while open_set:
#         if time.time() - start_time > timeout:
#             print(f"Timeout occurred while searching from {start_id} to {end_id}.")
#             yield None
#             return
        
#         current_f, current_id = heapq.heappop(open_set)

#         if current_id == end_id:
#             # Path found, reconstruct the path
#             path = [current_id]
#             while current_id in came_from:
#                 current_id = came_from[current_id]
#                 path.append(current_id)
#                 if len(path) > 10000:
#                     print("Path too long, stopping.")
#                     yield None
#                     return
#             yield list(reversed(path))
#             return
        

#         # Explore neighbors (all outgoing segments from current node)
#         for neighbor_id, edge_data in road_network[current_id].items():
#             segment_info = edge_data.get(weight, 1)
#             segment_length = edge_data.get('distance', 1)  # Default to 1 if not found
#             segment_weight = segment_info  # Adjust weight based on distance
#             # Only explore the neighbor if it's potentially better (g_score + heuristic)
#             tentative_g = g_score[current_id] + segment_weight
#             if neighbor_id not in g_score or tentative_g < g_score[neighbor_id]:
#                 came_from[neighbor_id] = current_id
#                 g_score[neighbor_id] = tentative_g

#                 # Precompute neighbor's heuristic score
#                 neighbor_cell = (math.floor(neighbor_id[0] / cell_size), math.floor(neighbor_id[1] / cell_size))
#                 neighbor_info = info_grid.get(neighbor_cell, 0)
#                 f_score[neighbor_id] = tentative_g + heuristic(neighbor_id, end_id, info_grid, cell_size)
                
#                 # Add to open set only if it's better than existing
#                 heapq.heappush(open_set, (f_score[neighbor_id], neighbor_id))

#         yield None  # Yield control back to avoid locking the program

def run_astar_with_timeout(road_network, start, end, info_grid, route_type,optimization_objective, timeout=2):
    """Runs A* with a manual timeout using the modified astar_generator."""
    start_time = time.time()  # Start the timer

    try:
        # Run A* search and check for timeout
        for path in astar_generator(road_network, start, end, info_grid, route_type,optimization_objective, timeout=timeout):
            if path is not None:  # Path found
                return path
            if time.time() - start_time > timeout:  # Timeout occurred
                if DEBUG:
                    print(f"Timeout occurred for start: {start}, end: {end}")
                return None
    except Exception as e:
        if DEBUG:
            print(f"Error occurred: {e}")
        return None  # No path found or error occurred




# # OLD VERSION
# def astar_generator(road_network, start, end,heuristic,weight='information_weight'):
    
#     """Generator function to allow manual timeout checking during A* search."""
#     start_time= time.time()  # Start the timer
#     try:
#         path=nx.astar_path(road_network, source=start, target=end, heuristic=heuristic, weight=weight)
#         #path=nx.dijkstra_path(road_network, source=start, target=end, weight=weight)
#         if time.time() - start_time > 2:
#             print("Timeout occurred.")
#             yield None  # Timeout occurred
#         else:
#             yield path
#     except nx.NetworkXNoPath:
#         yield None  # No path found

# # Example usage:
# # path = run_astar_with_timeout(road_network, start, end, timeout=5)



def find_shortest_path_with_fallback(road_network, start_nodes, end_nodes, is_calculated, calculated_path, calculated_distance, calculated_info_weight,calculated_time,route_type,info_grid,optimization_objective,timeout=2):
    """Finds the shortest path using A* with a fallback and timeout."""
    # Check cached results first
    for s, e in [(0, 0), (0, 1), (1, 0), (1, 1)]:
        if is_calculated.get((start_nodes[s], end_nodes[e]), False):
            return calculated_path[start_nodes[s], end_nodes[e]], s, e

    shortest_path = None
    shortest_path_length = float('inf')
    shortest_path_info_weight = float('inf')
    shortest_path_cost = float('inf')
    s_true, e_true = None, None

    for s, e in [(0, 0), (0, 1), (1, 0), (1, 1)]:
        start_0_added, start_1_added, end_0_added, end_1_added = False, False, False, False
        
        # Run A* with timeout
        path = run_astar_with_timeout(road_network, start_nodes[s], end_nodes[e], info_grid,route_type,optimization_objective,timeout)
        path_length = calculate_path_metrics(road_network, path)[0] if path else float('inf')
        path_information_weight = calculate_path_metrics(road_network, path)[2] if path else float('inf')
        path_time = calculate_path_metrics(road_network, path)[1] if path else float('inf')
        # Skip if no path found or timeout occurred
        if path is None:
            continue

        # Adjust start and end if needed
        if s == 0 and (len(path) == 1 or path[1] != start_nodes[1]) and is_valid_segment(road_network, start_nodes[1], start_nodes[0]):
            path.insert(0, start_nodes[1])
            path_length += road_network[start_nodes[1]][start_nodes[0]]['distance']
            path_information_weight += road_network[start_nodes[1]][start_nodes[0]]['information_weight']
            path_time += road_network[start_nodes[1]][start_nodes[0]]['time_cost']
            start_1_added = True
        elif s == 1 and (len(path) == 1 or path[1] != start_nodes[0]) and is_valid_segment(road_network, start_nodes[0], start_nodes[1]):
            path.insert(0, start_nodes[0])
            path_length += road_network[start_nodes[0]][start_nodes[1]]['distance']
            path_information_weight += road_network[start_nodes[0]][start_nodes[1]]['information_weight']
            path_time += road_network[start_nodes[0]][start_nodes[1]]['time_cost']
            start_0_added = True

        if e == 0 and (len(path) == 1 or path[-2] != end_nodes[1]) and is_valid_segment(road_network, end_nodes[0], end_nodes[1]):
            path.append(end_nodes[1])
            path_length += road_network[end_nodes[0]][end_nodes[1]]['distance']
            path_information_weight += road_network[end_nodes[0]][end_nodes[1]]['information_weight']
            path_time += road_network[end_nodes[0]][end_nodes[1]]['time_cost']
            end_1_added = True
        elif e == 1 and (len(path) == 1 or path[-2] != end_nodes[0]) and is_valid_segment(road_network, end_nodes[1], end_nodes[0]):
            path.append(end_nodes[0])
            path_length += road_network[end_nodes[1]][end_nodes[0]]['distance']
            path_information_weight += road_network[end_nodes[1]][end_nodes[0]]['information_weight']
            path_time += road_network[end_nodes[1]][end_nodes[0]]['time_cost']
            end_0_added = True
        if optimization_objective == 'd':
            path_cost = path_length
        elif optimization_objective == 't':
            path_cost = path_time
        else:
            path_cost = path_information_weight
        # Update shortest path if it's better
        if path_cost < shortest_path_cost:
            shortest_path_cost = path_cost
            shortest_path_length = path_length
            shortest_path = path
            s_true, e_true = s, e

            # Adjust start/end flags
            if start_0_added:
                s_true = 0
            if start_1_added:
                s_true = 1
            if end_0_added:
                e_true = 0
            if end_1_added:
                e_true = 1

            # Cache the result
            is_calculated[start_nodes[s_true], end_nodes[e_true]] = True
            calculated_path[start_nodes[s_true], end_nodes[e_true]] = shortest_path
            calculated_distance[start_nodes[s_true], end_nodes[e_true]] = shortest_path_length
            calculated_info_weight[start_nodes[s_true], end_nodes[e_true]] = path_information_weight
            calculated_time[start_nodes[s_true], end_nodes[e_true]] = path_time

    return shortest_path, s_true, e_true


from collections import defaultdict
import json
import numpy as np
from scipy.spatial import ConvexHull

from sklearn.decomposition import PCA
import numpy as np
from scipy.spatial import ConvexHull
import copy



def hull_construction(hull_data, selected_segments,benefit_type):

    # Let's say this is your input: dict with segments as keys, list of point dicts as values
    # segment_dict = {
    #     (segment_start_id, segment_end_id): [point_dict1, point_dict2, ...],
    #     ...
    # }
    segment_dict = hull_data
    # Step 1: Flatten all membership values for convex hull
    all_memberships = []
    point_to_segment_map = []

    for segment_key, points in segment_dict.items():
        for point in points.values():
            # all_memberships.append(point["membership_values"])
            if benefit_type == "m":
                if point["is_max_benefit"] == 1:
                    all_memberships.append(point["membership_values"])
                    point_to_segment_map.append((segment_key, point))
            else:
                all_memberships.append(point["membership_values"])
                point_to_segment_map.append((segment_key, point))  # Keep link to original

    points_array = np.array(all_memberships)

    # Step 2: Compute convex hull
    try:
        hull = ConvexHull(points_array)
        hull_indices = set(hull.vertices)
        if DEBUG:
            print("Hull contains", len(hull_indices), "points")
    except Exception as e:
        if DEBUG:
            print("Convex hull computation failed:", e)
        hull_indices = set()

    # Step 3: Update point values based on hull membership
    for idx in range(len(point_to_segment_map)):
        segment_key, point_ref = point_to_segment_map[idx]
        if idx in hull_indices:
            point_ref["value"] = 2
        else:
            point_ref["value"] = 1

    # Step 4: Add segment-level values based on point values
    final_output = []

    for segment_key, points in segment_dict.items():
        segment_value = 2 if any(p.get("value", 1) == 2 for p in points.values()) else 1
        
        segment_entry = {
            "segment_start_id": segment_key[0],
            "segment_end_id": segment_key[1],
            "segment_value": segment_value,
            "num_points": len(points),
            "points": copy.deepcopy(points)
        }
        
        if benefit_type == "m":
            segment_entry["points"] = {k: v for k, v in points.items() if v["is_max_benefit"] == 1}
            
        
        # debug
        if segment_value != 2:
            cluster_id = max(points[p]['class'] for p in points.keys() if points[p]['point_distance_weighted_benefit'] == max(point['point_distance_weighted_benefit'] for point in points.values()))
            if DEBUG:
                print("Segment with value 1 found:", segment_key, "cluster: ", cluster_id)
        
        final_output.append(segment_entry)
        for key, segment in list(selected_segments.items()):
            if segment['segment_start_id'] == segment_key[0] and segment['segment_end_id'] == segment_key[1]:
                if segment_entry['segment_value'] != 2:
                    selected_segments.pop(key)
                break
        
    return selected_segments

    

def select_segments(benefits_data, problematic_segments, segment_number_per_class, total_number_of_classes, roads_data):
    selected_segment_count = defaultdict(int)
    selected_segments = {}
    
    # Initialize selected segment counts for each class
    for i in range(1, total_number_of_classes + 1):
        selected_segment_count[i] = 0
    
    

    segment_hull_lookup = {}
    for data in benefits_data:
        class_id = data['class']
        
        # Skip if the selected count for this class exceeds the limit
        if selected_segment_count[class_id] >= segment_number_per_class:
            continue
        
        start_id = data['segment_start_id']
        end_id = data['segment_end_id']
        
        # Check if the segment has 'segment_value' of 2 (i.e., the point is on the convex hull)
        # segment_value = segment_value_map.get((start_id, end_id), 1)  # Default to 1 if not found
        # if segment_value != 2:
        #     continue
        
        # Skip if the segment is in the problematic segments
        if (start_id, end_id) in problematic_segments.values():
            continue
        
        # Select the segment
        selected_segments[(start_id, end_id)] = data
        selected_segment_count[class_id] += 1
        
        segment_hull_data = roads_data[str(data['road_id'])]["segments"][str(data['segment_id'])]["points"]
        segment_hull_lookup[(start_id, end_id)] = segment_hull_data
        # Stop early if we have selected enough segments for each class
        
        if all(count >= segment_number_per_class for count in selected_segment_count.values()):
            break
        
    
    if DEBUG:
        print(list(selected_segments.items())[0:1])    
    return selected_segments, segment_hull_lookup

def get_unique_nodes_from_selected_segments(selected_segment_dict):
    unique_nodes = set()
    for (start_id, end_id), _ in selected_segment_dict.items():
        unique_nodes.add(start_id)
        unique_nodes.add(end_id)
    return list(unique_nodes)

def precompute_all_shortest_paths_with_directions(road_network, segment_dict, info_grid, route_type, timeout=2):
    unique_segments = list(segment_dict.keys())  # Each is (start_id, end_id)

    is_calculated = {}
    calculated_path = {}
    calculated_distance = {}
    segment_connection_metadata = {}  # NEW: to store s_true and e_true per segment pair

    for i, seg_i in enumerate(unique_segments):
        for j, seg_j in enumerate(unique_segments):
            if seg_i == seg_j:
                continue

            # segment_i goes to segment_j
            start_nodes = seg_i  # (start, end)
            end_nodes = seg_j    # (start, end)

            key = (seg_i, seg_j)

            path, s_true, e_true = find_shortest_path_with_fallback(
                road_network,
                start_nodes,
                end_nodes,
                is_calculated,
                calculated_path,
                calculated_distance,
                route_type,
                info_grid,
                timeout
            )

            if path is not None:
                segment_connection_metadata[key] = {
                    "s_true": s_true,
                    "e_true": e_true,
                    "path": path,
                    "distance": calculated_distance[start_nodes[s_true], end_nodes[e_true]]
                }

    return path,s_true,e_true, segment_connection_metadata


# # OLD VERSION
# # Select top segments based on benefits and avoid problematic segments
# def select_segments(benefits_data, problematic_segments, segment_number_per_class, total_number_of_classes):
#     selected_segment_count = defaultdict(int)
#     selected_segments = {}
#     for i in range(1, total_number_of_classes + 1):
#         selected_segment_count[i] = 0
#     for data in benefits_data:
#         class_id = data['class']
#         if selected_segment_count[class_id] >= segment_number_per_class:
#             continue
#         start_id = data['segment_start_id']
#         end_id = data['segment_end_id']
#         if (start_id, end_id) in problematic_segments.values():
#             continue
        
#         # if any([start_id in values and end_id in values for values in problematic_segments.values()]):
#         #     continue
        
#         selected_segments[(start_id, end_id)] = data
#         selected_segment_count[class_id] += 1
#         if all(count >= segment_number_per_class for count in selected_segment_count.values()):
#             break

#     return selected_segments

def calculate_path_metrics(road_network, path):
    """Calculate total distance and time cost for a given path."""
    path_distance = 0
    path_time_cost = 0
    path_information_weight = 0
    path_information_value = 0
    on_motorway_segment_coordinates = []
    # Iterate over consecutive nodes in the path
    for i in range(len(path) - 1):
        current_node = path[i]
        next_node = path[i + 1]
        
        # Ensure the edge exists in the road network
        if road_network.has_edge(current_node, next_node):
            edge_data = road_network[current_node][next_node]
            path_distance += edge_data.get('distance', 0)  # Add distance
            path_time_cost += edge_data.get('time_cost', 0)  # Add time cost
            #path_benefit += edge_data.get('benefit', {})
            # if edge_data.get('information_weight') == 1:
            #     print("here")
            path_information_weight += edge_data.get('information_weight', 1)  # Add information weight
            path_information_value += edge_data.get('information_value', 0)  # Add information value
            if edge_data["is_motorway"] == 1:
                on_motorway_segment_coordinates.append(tuple[current_node,next_node])
        else:
            raise ValueError(f"No edge between {current_node} and {next_node} in the road network.")
    
    return path_distance, path_time_cost, path_information_weight, path_information_value


# Calculate paths between selected segments
def calculate_paths(selected_segments, road_network, problematic_segments, no_path_count,no_path_count_per_id, total_number_of_classes,is_calculated,calculated_path,calculated_distance,calculated_info_weight,calculated_time,route_type,info_grid,optimization_objective):
    all_paths = []
    is_wend=True
    no_path=False
    calculated_paths = []
    calculated_ids = []
    calculated_id_data = {}
    calculated_time = {}
    #no_path_count_per_id={}
    # problematic_segments = {}
    if DEBUG:
        print('selected segments',len(selected_segments))
    i=1
    for (start_id, end_id), start_data in selected_segments.items():
        if (start_id,end_id) not in no_path_count_per_id.keys():
            no_path_count_per_id[(start_id,end_id)]=0
        start_nodes = [
            tuple(start_data["segment_start_coordinate"]),
            tuple(start_data["segment_end_coordinate"])
        ]
        start_class_id = start_data["class"]
        start_road_id = start_data["road_id"]
        start_segment_id = start_data["segment_id"]
        start_segment_benefit = start_data["benefit"]
        start_segment_information_weight = start_data["information_weight"]
        start_segment_information_value = start_data["information_value"]
        j=1
        for (end_start_id, end_end_id), end_data in selected_segments.items():
            if (end_start_id,end_end_id) not in no_path_count_per_id.keys():
                no_path_count_per_id[(end_start_id,end_end_id)]=0
            end_class_id  = end_data["class"]
            if (start_class_id == end_class_id) and (start_id == end_start_id) and (end_id == end_end_id):
                j+=1
                continue
            individual_path_time_start = time.time()
            end_nodes = [
                tuple(end_data["segment_start_coordinate"]),
                tuple(end_data["segment_end_coordinate"])
            ]
            
            end_road_id = end_data["road_id"]
            end_segment_id = end_data["segment_id"]
            end_segment_benefit = end_data["benefit"]
            end_segment_information_weight = end_data["information_weight"]
            end_segment_information_value = end_data["information_value"]

            # Find the shortest path with fallback
            shortest_path, s, e = find_shortest_path_with_fallback(road_network, start_nodes, end_nodes,is_calculated,calculated_path,calculated_distance, calculated_info_weight,calculated_time,route_type,info_grid,optimization_objective)
                                                                   
            
            if not shortest_path:
                is_wend=False
                no_path=True
                if (start_id, end_id) or (end_start_id, end_end_id) not in problematic_segments:
                    no_path_count += 1
                    
                    
                    if i==1 and no_path_count_per_id[(start_id,end_id)]>=3:
                        
                        no_path_count_per_id[problematic_segments[no_path_count-1]]-=1
                        no_path_count_per_id[problematic_segments[no_path_count-2]]-=1
                        no_path_count_per_id[problematic_segments[no_path_count-3]]-=1
                        problematic_segments.pop(no_path_count-1)
                        problematic_segments.pop(no_path_count-2)
                        no_path_count-=3
                        problematic_segments[no_path_count] = (start_id, end_id)
                        no_path_count_per_id[(start_id,end_id)]+=1
                        if DEBUG:
                            print('abort for start segment c1, i=',i,'j=',j)
                            print('start_id',start_id,'end_id',end_id)
                        break
                    if i==1:
                        if j==2:
                            if start_segment_benefit>end_segment_benefit:
                                problematic_segments[no_path_count] = (end_start_id, end_end_id)
                                no_path_count_per_id[(end_start_id,end_end_id)]+=1
                                no_path_count_per_id[(start_id,end_id)]+=1
                                if DEBUG:
                                    print('abort for end segment c1, i=',i,'j=',j)
                                    print('start_id',start_id,'end_id',end_id)
                                    print('end_start_id',end_start_id,'end_end_id',end_end_id)
                            else:
                                problematic_segments[no_path_count] = (start_id, end_id)
                                no_path_count_per_id[(start_id,end_id)]+=1
                                if DEBUG:
                                    print('abort for start segment c2, i=',i,'j=',j)
                                    print('start_id',start_id,'end_id',end_id)
                        else:
                            problematic_segments[no_path_count] = (end_start_id, end_end_id)
                            no_path_count_per_id[(end_start_id,end_end_id)]+=1
                            no_path_count_per_id[(start_id,end_id)]+=1
                            if DEBUG:
                                print('abort for end segment c2, i=',i,'j=',j)
                                print('start_id',start_id,'end_id',end_id)
                                print('end_start_id',end_start_id,'end_end_id',end_end_id)

                    else:
                        problematic_segments[no_path_count] = (end_start_id, end_end_id)
                        no_path_count_per_id[(end_start_id,end_end_id)]+=1
                        if DEBUG:
                            print('abort for end segment c3, i=',i,'j=',j)
                            print('start_id',start_id,'end_id',end_id)
                            print('end_start_id',end_start_id,'end_end_id',end_end_id)
                    # problematic_segments[no_path_count] = (start_id, end_id)
                abort_time = time.time()
                print(f"Abort time: {abort_time - individual_path_time_start:.2f} seconds")
                break
            
            if s==0:
                actual_start_id = start_id
                
            else:
                actual_start_id = end_id
                
            if e==0:
                actual_end_id=end_start_id
                
            else:
                actual_end_id=end_end_id
                
        
            # path_distance = nx.dijkstra_path_length(road_network, source=shortest_path[0], target=shortest_path[-1], weight='distance')
            # path_time_cost = nx.dijkstra_path_length(road_network, source=shortest_path[0], target=shortest_path[-1], weight='time_cost')
            
            path_distance, path_time_cost,path_information_weight,path_information_value = calculate_path_metrics(road_network, shortest_path)
            
            if path_distance==0:
                print(actual_start_id, actual_end_id)
            # Calculate benefits
            benefits = {i: 0 for i in range(1, total_number_of_classes + 1)}
            benefits[start_class_id] += start_segment_benefit
            benefits[end_class_id] += end_segment_benefit
            if actual_start_id not in calculated_ids:
                calculated_ids.append(actual_start_id)
                calculated_id_data[actual_start_id] = start_data
                if actual_start_id==start_data['segment_start_id']:
                    calculated_id_data[actual_start_id]=copy.deepcopy(calculated_id_data[actual_start_id])
                    calculated_id_data[actual_start_id]['used'] = 'start'
                else:
                    calculated_id_data[actual_start_id]=copy.deepcopy(calculated_id_data[actual_start_id])
                    calculated_id_data[actual_start_id]['used'] = 'end'
                
            if actual_end_id not in calculated_ids:
                calculated_ids.append(actual_end_id)
                calculated_id_data[actual_end_id] = end_data
                if actual_end_id==end_data['segment_start_id']:
                    calculated_id_data[actual_end_id]=copy.deepcopy(calculated_id_data[actual_end_id])
                    calculated_id_data[actual_end_id]['used'] = 'start'
                else:
                    calculated_id_data[actual_end_id]=copy.deepcopy(calculated_id_data[actual_end_id])
                    calculated_id_data[actual_end_id]['used'] = 'end'
            calculated_paths.append((actual_start_id, actual_end_id))  # Fix: Use parentheses instead of square brackets
            all_paths.append({
                'start_road_id': start_road_id,
                "start_segment_id": start_segment_id,
                'actual_segment_start_id': actual_start_id,
                'end_road_id': end_road_id,
                "end_segment_id": end_segment_id,
                'actual_segment_end_id': actual_end_id,
                'number_of_segments': len(shortest_path),
                "distance": path_distance,
                "time": path_time_cost,
                "information_weight": path_information_weight,
                "information_value": path_information_value,
                "benefit": benefits,
                'start_segment_benefit': start_segment_benefit,
                'end_segment_benefit': end_segment_benefit,
                'start_segment_info_weight': start_segment_information_weight,
                'end_segment_info_weight': end_segment_information_weight,
                'start_segment_info_value': start_segment_information_value,
                'end_segment_info_value': end_segment_information_value,
                "path": shortest_path
            })
            if DEBUG:
                print('path found, i=',i,'j=',j, "length=",len(shortest_path))
            individual_path_time_end = time.time()
            if DEBUG:
                print(f"Individual path time: {individual_path_time_end - individual_path_time_start:.2f} seconds")
            j+=1
        i+=1
        if no_path:
            break
    return all_paths, problematic_segments, is_wend, no_path_count, calculated_paths,calculated_id_data,no_path_count_per_id,is_calculated,calculated_path,calculated_distance,calculated_info_weight,calculated_time

# TODO: Calculate other paths
def calculate_other_paths(calculated_paths,road_network,all_paths,calculated_id_data,total_number_of_classes,is_calculated,calculated_path,calculated_distance,calculated_info_weight,calculated_time,info_grid,route_type,optimization_objective):
    not_found_count=0
    for actual_start_id,start_data in calculated_id_data.items():
        if calculated_id_data[actual_start_id]['used']=='start':
            start_nodes = tuple(calculated_id_data[actual_start_id]["segment_start_coordinate"])
        else:
            start_nodes = tuple(calculated_id_data[actual_start_id]["segment_end_coordinate"]    )
        start_road_id = calculated_id_data[actual_start_id]["road_id"]
        start_segment_id = calculated_id_data[actual_start_id]["segment_id"]
        start_segment_benefit = calculated_id_data[actual_start_id]["benefit"]
        start_segment_class_id = calculated_id_data[actual_start_id]["class"]
        start_segment_info_weight = calculated_id_data[actual_start_id]["information_weight"]
        start_segment_info_value = calculated_id_data[actual_start_id]["information_value"]
        for actual_end_id, end_data in calculated_id_data.items():
            if actual_start_id==actual_end_id:
                continue
            if (actual_start_id, actual_end_id) in calculated_paths:
                continue
            if calculated_id_data[actual_end_id]['used']=='start':
                end_nodes = tuple(calculated_id_data[actual_end_id]["segment_start_coordinate"])
            else:
                end_nodes = tuple(calculated_id_data[actual_end_id]["segment_end_coordinate"])
            end_road_id = calculated_id_data[actual_end_id]["road_id"]
            end_segment_id = calculated_id_data[actual_end_id]["segment_id"]
            end_segment_benefit = calculated_id_data[actual_end_id]["benefit"]
            end_segment_class_id = calculated_id_data[actual_end_id]["class"]
            end_segment_info_weight = calculated_id_data[actual_end_id]["information_weight"]
            end_segment_info_value = calculated_id_data[actual_end_id]["information_value"]
            shortest_path=run_astar_with_timeout(road_network, start_nodes, end_nodes,info_grid,route_type,optimization_objective)
            benefits = {i: 0 for i in range(1, total_number_of_classes + 1)}
            if not shortest_path:
                path_distance=float('inf')
                path_time_cost=float('inf')
                start_segment_benefit=0
                end_segment_benefit=0
                start_segment_info_weight=1
                end_segment_info_weight=1
                start_segment_info_value=0
                end_segment_info_value=0
                not_found_count+=1
                print('no path found',not_found_count)
                len_shortest_path=0
            else:
                path_distance=calculate_path_metrics(road_network,shortest_path)[0]
                path_time_cost=calculate_path_metrics(road_network,shortest_path)[1]
                path_information_weight=calculate_path_metrics(road_network,shortest_path)[2]
                path_information_value=calculate_path_metrics(road_network,shortest_path)[3]
                benefits[start_segment_class_id] += start_segment_benefit
                benefits[end_segment_class_id] += end_segment_benefit
                len_shortest_path=len(shortest_path)
            all_paths.append({
                'start_road_id': start_road_id,
                "start_segment_id": start_segment_id,
                'actual_segment_start_id': actual_start_id,
                'end_road_id': end_road_id,
                "end_segment_id": end_segment_id,
                'actual_segment_end_id': actual_end_id,
                'number_of_segments': len_shortest_path,
                "distance": path_distance,
                "time": path_time_cost,
                "information_weight": path_information_weight,
                "information_value": path_information_value,
                "benefit": benefits,
                'start_segment_benefit': start_segment_benefit,
                'end_segment_benefit': end_segment_benefit,
                'start_segment_info_weight': start_segment_info_weight,
                'end_segment_info_weight': end_segment_info_weight,
                'start_segment_info_value': start_segment_info_value,
                'end_segment_info_value': end_segment_info_value,
                "path": shortest_path
            })
    return all_paths
# Main function
def path_finding(working_directory,segment_number_per_class, total_number_of_classes,route_type,optimization_objective):
    start_time = time.time()
    workdir = os.path.join(os.getcwd(), working_directory)
    input_dir = os.path.join(workdir, "input")
    transient_dir = os.path.join(workdir, "transient")
    roads_data_file = os.path.join(transient_dir, "bc_benefits_output.json")
    benefits_data_file = os.path.join(transient_dir, "bc_top_benefits_output.json")
    #hull_file_path = os.path.join(transient_dir, "point_hull_collection.json")
    roads_data = load_data(roads_data_file)
    benefits_data = load_data(benefits_data_file)
    benefits_data = benefits_data[1:]
    #hull_data = load_data(hull_file_path)
    
    osm_file=glob.glob(os.path.join(input_dir, '*.geojson'))
    osm_file=osm_file[0]
    osm_data=restructure_osm_data(osm_file,roads_data)
    road_network = build_road_network(osm_data)
    problematic_segments = {}
    is_wend=False
    no_path_count=0
    no_path_count_per_id={}
    # print(list(osm_data.items())[:1])
    #info_grid=build_information_grid(osm_data,route_type)
    info_grid={}
    is_calculated={}
    calculated_path={}
    calculated_distance={}
    calculated_info_weight={}
    calculated_time={}
    while True:
        selected_segments, segments_hull_lookup = select_segments(benefits_data, problematic_segments, segment_number_per_class, total_number_of_classes,roads_data)
        
        #selected_segments = hull_construction(segments_hull_lookup,selected_segments, benefit_type)
        if DEBUG:
            print('selected segments',len(selected_segments))
        all_paths, problematic_segments, is_wend, no_path_count, calculated_paths, calculated_id_data,no_path_count_per_id,is_calculated,calculated_path,calculated_distance,calculated_info_weight,calculated_time = calculate_paths(selected_segments, road_network, problematic_segments, no_path_count,no_path_count_per_id, total_number_of_classes,is_calculated,calculated_path,calculated_distance,calculated_info_weight,calculated_time, route_type,info_grid,optimization_objective)
        
        if is_wend:
            json_serializable_dict_segments = {str(key): value for key, value in selected_segments.items()}
            if DEBUG:
                with open(os.path.join(transient_dir, 'selected_segment_information.json'), 'w') as f:
                    json.dump(json_serializable_dict_segments, f, indent=4)
            # calculated_id_data = [data for data in benefits_data if data['segment_start_id'] in calculated_ids or data['segment_end_id'] in calculated_ids]
            if DEBUG:
                print('calculating other paths', no_path_count)
            all_paths=calculate_other_paths(calculated_paths,road_network,all_paths,calculated_id_data,total_number_of_classes,is_calculated,calculated_path,calculated_distance,calculated_info_weight, calculated_time, info_grid,route_type,optimization_objective)
            path_calculation_end_time = time.time()
            if DEBUG:
                print(f"Path calculation time: {path_calculation_end_time - start_time:.2f} seconds")
                print('done')
            break
        if DEBUG:
            print('not done',no_path_count)
    # all_paths.append(selected_segments)
    write_path = os.path.join(transient_dir, "pf_output.json")
    write_output(write_path, all_paths)
    
    if DEBUG:
        debug_path = os.path.join(transient_dir, "debug")
        with open(os.path.join(debug_path,'pf_output_tabbed.json'), 'w') as f:
            json.dump(all_paths, f, indent=4)
        end_time = time.time()
        print(f"Execution Time: {end_time - start_time:.2f} seconds")
        print("Paths calculation completed.")

# Write output to JSON file
def write_output(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f)

# Run the main function
if __name__ == "__main__":
    path_finding(
        working_directory='work_dir/minimal_test', #This is the working directory
        segment_number_per_class=1, #This is the number of segments per class
        total_number_of_classes=15, #This is the total number of classes
        route_type='g', #This is the type of route, 'g' for good, 'b' for bad
        optimization_objective='i'  #This is the optimization objective, 'd' for distance, 't' for time, 'i' for information weight
        )
