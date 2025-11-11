import csv
import json
from shapely import Point, STRtree, box
import math
import time
import os
import glob
import pandas as pd
import copy

# =============================================================================
# DEBUG CONFIGURATION - Set to True to enable debug prints for this module
# =============================================================================
DEBUG = False

def convert_optimal_grid_cells_to_csv(working_directory, num_clusters, optimal_cells_filename='optimal_grid_cells.json'):
    """
    Convert optimal grid cells from HPE output to points.csv format.
    Assigns equal cluster membership values to all points (uniform distribution).
    
    Args:
        working_directory: Root working directory
        num_clusters: Number of clusters in the analysis
        optimal_cells_filename: Name of the optimal grid cells JSON file (without number suffix)
    
    Returns:
        Path to the created points.csv file
    """
    workdir = working_directory
    input_dir = os.path.join(workdir, "input")
    transient_dir = os.path.join(workdir, "transient")
    
    # Find optimal grid cells file (with or without number suffix)
    optimal_files = glob.glob(os.path.join(transient_dir, 'optimal_grid_cells*.json'))
    
    if not optimal_files:
        if DEBUG:
            print(f"Error: No optimal_grid_cells*.json file found in {transient_dir}")
        return None
    
    # Use the first (or only) optimal grid cells file found
    optimal_file = optimal_files[0]
    if DEBUG:
        print(f"Loading optimal grid cells from: {optimal_file}")
    
    # Load optimal grid cells
    with open(optimal_file, 'r') as f:
        data = json.load(f)
    
    # Extract coordinates (handle both with and without execution_summary)
    if "optimal_grid_cells" in data:
        coordinates = data["optimal_grid_cells"]
    else:
        # Assume the entire file is the coordinates list
        coordinates = data
    
    if not coordinates:
        if DEBUG:
            print("Error: No coordinates found in optimal grid cells file")
        return None
    
    if DEBUG:
        print(f"Found {len(coordinates)} optimal grid cell coordinates")
    
    # Calculate equal membership value for all clusters
    equal_membership = 1.0 / num_clusters
    
    # Create data rows with equal cluster memberships
    rows = []
    for coord in coordinates:
        if len(coord) != 2:
            if DEBUG:
                print(f"Warning: Skipping invalid coordinate: {coord}")
            continue
        
        easting, northing = coord[0], coord[1]
        # Create equal membership values for all clusters
        memberships = [equal_membership] * num_clusters
        
        row = [easting, northing] + memberships
        rows.append(row)
    
    # Create column names
    columns = ["Easting", "Northing"] + [f"Cluster{i+1}" for i in range(num_clusters)]
    
    # Create DataFrame
    df = pd.DataFrame(rows, columns=columns)
    
    # Save to CSV in input directory
    output_file = os.path.join(input_dir, "points.csv")
    df.to_csv(output_file, index=False)
    
    if DEBUG:
        print(f"✅ Created points.csv with {len(rows)} points and {num_clusters} clusters")
        print(f"   Each point has equal membership: {equal_membership:.6f} per cluster")
        print(f"   Saved to: {output_file}")
    
    return output_file


def convert_to_csv(working_directory):
    workdir = working_directory
    input_dir = os.path.join(workdir, "input")
    input_files = glob.glob(os.path.join(input_dir, '*.txt'))  # Get list of txt files

    if not input_files:
        if DEBUG:
            print("No input files found.")
        return None

    input_file = input_files[0]  # Assuming there's only one .txt file
    output_file = os.path.join(input_dir, "converted.csv")

    # Read the text file
    with open(input_file, "r") as f:
        lines = f.readlines()

    if not lines:
        print("Input file is empty.")
        return None

    # Process data
    data = []
    for line in lines:
        values = line.split()  # Split by whitespace
        if len(values) < 3:  # Ensure there are at least Easting, Northing, and 1 cluster
            continue
        
        easting, northing = values[:2]  # First two columns
        clusters = values[2:]  # Everything else is a cluster
        row = [easting, northing] + clusters
        data.append(row)

    # Dynamically count clusters
    num_clusters = len(data[0]) - 2  # Subtracting Easting & Northing
    columns = ["Easting", "Northing"] + [f"Cluster{i+1}" for i in range(num_clusters)]

    # Create DataFrame
    df = pd.DataFrame(data, columns=columns)

    # Save to CSV
    df.to_csv(output_file, index=False)

    if DEBUG:
        print(f"CSV file saved as {output_file}")
    return output_file


def distance_point_to_segment(point, segment_start, segment_end):
    def dot(v, w):
        return v[0] * w[0] + v[1] * w[1]

    def length_sq(v):
        return v[0] ** 2 + v[1] ** 2

    def distance_sq_point_to_line(point, line_start, line_end):
        line_vec = (line_end[0] - line_start[0], line_end[1] - line_start[1])
        point_vec = (point[0] - line_start[0], point[1] - line_start[1])
        proj_length = dot(point_vec, line_vec) / length_sq(line_vec)

        if proj_length < 0:
            return length_sq(point_vec)
        elif proj_length > 1:
            return length_sq((point[0] - line_end[0], point[1] - line_end[1]))
        else:
            proj_point = (
                line_start[0] + proj_length * line_vec[0],
                line_start[1] + proj_length * line_vec[1],
            )
            return length_sq((point[0] - proj_point[0], point[1] - proj_point[1]))

    return math.sqrt(distance_sq_point_to_line(point, segment_start, segment_end))

def determine_maxspeed(highway_type, maxspeed_value,maxspeed_list,zone_type):
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
    if maxspeed not in maxspeed_list:        
        maxspeed_list.append(maxspeed)
    return maxspeed_list, maxspeed    


def build_node_to_roads_map(data):
    """Build a mapping from nodes to roads that contain them."""
    node_to_roads = {}
    for feature in data["features"]:
        if feature["geometry"]["type"] == "LineString":
            road_id = int(feature["properties"]["osmid"])
            nodes = feature["properties"]["nodes"]
            for node in nodes:
                if node not in node_to_roads:
                    node_to_roads[node] = []
                node_to_roads[node].append(road_id)
    return node_to_roads


def is_road_isolated(nodes, node_to_roads, road_id):
    """Check if a road is topologically isolated (no connections to other roads)."""
    # Check start and end nodes only
    start_node = nodes[0]
    end_node = nodes[-1]
    
    # If either endpoint connects to another road, it's not isolated
    start_connections = [r for r in node_to_roads.get(start_node, []) if r != road_id]
    end_connections = [r for r in node_to_roads.get(end_node, []) if r != road_id]
    
    return len(start_connections) == 0 and len(end_connections) == 0


def point_mapping(
    working_directory, min_distance_to_road, is_reversed, 
    use_optimal_grid_cells=False, num_clusters=15
):
    """
    Map sensor points to road segments with connectivity filtering.
    
    Args:
        working_directory: Root working directory
        min_distance_to_road: Maximum distance (meters) for point-segment matching
        is_reversed: Coordinate order (False=E,N, True=N,E)
        use_optimal_grid_cells: If True, converts optimal_grid_cells*.json to points.csv first
        num_clusters: Number of clusters (required if use_optimal_grid_cells=True)
    """
    workdir = working_directory
    maxspeed_list = []
    
    # Set up directory paths for input and transient (intermediate) data
    input_dir = os.path.join(workdir, "input")
    transient_dir = os.path.join(workdir, "transient")
    
    # If using optimal grid cells, convert them to points.csv first
    if use_optimal_grid_cells:
        if DEBUG:
            print("=" * 80)
            print("🔄 Converting optimal grid cells to points.csv...")
            print("=" * 80)
        csv_path = convert_optimal_grid_cells_to_csv(working_directory, num_clusters)
        if csv_path is None:
            print("❌ Failed to convert optimal grid cells")
            return None
        print()
    
    # Find all GeoJSON files in the input directory
    geojson_files = glob.glob(os.path.join(input_dir, '*.geojson'))
    
    # Select the road information GeoJSON file (excluding files with '_4326' coordinate system suffix)
    road_information_path = next((f for f in geojson_files if '_4326' not in f), None)
    
    # Construct the path to the points CSV file containing sensor location data
    csv_files = os.path.join(input_dir, "points.csv")
    # csv_files = glob.glob(os.path.join(input_dir, '*.csv'))
    # if not csv_files:
    #     csv_files = convert_to_csv(working_directory)
    # else:
    #     csv_files = csv_files[0]
    point_information_path = csv_files
    start_time = time.time()
    # print("Start time is:", time.localtime())

    # Load point information and initialize STRtree
    marker_classification = {}
    markers = []
    with open(point_information_path, "r") as f:
        next(f)  # Skip header
        for line in f:
            line.strip()
            # classification = [float(c) for c in line.split("   ")[3:]]
            if line.split(",")[2] == '':
                continue
            classification = [float(c) for c in line.split(",")[2:]]
            number_of_classes = len(classification)
            if 0.9999 > sum(classification) > 1:
                print("Error: ", classification)
                continue
            # for entry in line[3:]:
            #     print(entry)
            # x_string=line.split('   ')[1]
            x, y = float(line.split(",")[0]), float(line.split(",")[1]) #correct easting northing
            if is_reversed:
                x,y = y,x
            # y,x = x,y #reversed
            markers.append(Point(x, y))
            marker_classification[(x, y)] = classification

    str_tree = STRtree(markers)

    # Load road information and build node connectivity map
    if DEBUG:
        print("Loading road network and building connectivity map...")
    with open(road_information_path, "r") as f:
        data = json.load(f)
    
    node_to_roads = build_node_to_roads_map(data)
    if DEBUG:
        print(f"  Found {len(node_to_roads)} unique nodes")
    
    # Load road information and process each road
    roads = {}
    isolated_roads = []
    
    global_x_min = math.inf
    global_y_min = math.inf
    global_x_max = -math.inf
    global_y_max = -math.inf
    
    for feature in data["features"]:
        access_information= feature["properties"].get("access", None)
        is_accessible= 1 if access_information == "yes" or access_information is None else 0
        maxspeed= feature["properties"].get("maxspeed", None)
        if maxspeed == 'none':
            maxspeed = None
        
        #is_traversible = 1 if maxspeed > 10 else 0
        is_traversible = 1
        # is_legitimate = True if feature["properties"]['highway'] in road_types else False
        is_legitimate = True
        if feature["geometry"]["type"] == "LineString" and is_legitimate and is_accessible==1 and is_traversible==1:
            road_id = int(feature["properties"]["osmid"])

            # Check if this road is indicated as a one-way
            # is_oneway = 1 if road_id in oneway_ids else 0
            oneway_information= feature["properties"].get("oneway", None)
            
            way_points = feature["geometry"]["coordinates"]
            segment_nodes = feature["properties"]["nodes"]
            highway_type = feature["properties"]["highway"]
            road_name = feature["properties"]["name"]
            
            # NEW: Check if road is topologically isolated
            if is_road_isolated(segment_nodes, node_to_roads, road_id):
                isolated_roads.append(road_id)
                continue  # Skip this road
            
            zone_type= feature["properties"].get("source:maxspeed", None)
            maxspeed_list,maxspeed = determine_maxspeed(highway_type, maxspeed, maxspeed_list,zone_type)
            maxspeed = int(maxspeed)
            is_oneway= 1 if oneway_information == "yes" else 0
            

            # Update global bounding box
            x_min = min([x for x, y in way_points])
            y_min = min([y for x, y in way_points])
            x_max = max([x for x, y in way_points])
            y_max = max([y for x, y in way_points])
            global_x_min = min(global_x_min, x_min)
            global_y_min = min(global_y_min, y_min)
            global_x_max = max(global_x_max, x_max)
            global_y_max = max(global_y_max, y_max)

            # Query STRtree for points within min_distance_to_road
            indices = str_tree.query(box(x_min, y_min, x_max, y_max), predicate="dwithin", distance=min_distance_to_road)

            points_covered = [(str_tree.geometries[index].x, str_tree.geometries[index].y) for index in indices]
            if points_covered:
                roads[road_id] = [
                    way_points,
                    (x_min, y_min, x_max, y_max),
                    segment_nodes,
                    highway_type,
                    road_name,
                    maxspeed,
                    is_oneway,
                    is_accessible,
                    points_covered,
                ]
    
        if DEBUG:
            print(f"Filtered out {len(isolated_roads)} isolated roads")
            if isolated_roads:
                print(f"  Examples: {isolated_roads[:10]}")
    
    with open(os.path.join(transient_dir, "maxspeed_information.json"), "w") as f:
        json.dump(maxspeed_list, f)
    segment_point_count = {}
    structured_data = {}
    min_distances = {}
    max_distance_to_segment = min_distance_to_road
    segment_hull_identifier = {}
    act_max_benefit = {}
    #max_membership_value = {}
    act_min_distance={}
    points_covered = {}
    for road_id, road_data in roads.items():
        way_points, _, segment_nodes, _, _, _, _, _, _ = road_data
        segment_point_count[road_id] = {}
        points_covered[road_id] = {}
        for i in range(len(way_points) - 1):
            segment_key = i + 1
            segment_point_count[road_id][segment_key] = 0
            unique_point_count = 0
            lp1 = way_points[i]
            lp2 = way_points[i + 1]
            points_covered[road_id][segment_key] = {}
            segment_hull_data = {}
            act_max_benefit[segment_key]= 0
            for p in road_data[-1]:
                point_data={}
                # if p==(4440600.0,5728500.0):
                #     print('found')
                # max_membership_value[p]=0 if p not in max_membership_value.keys() else max_membership_value[p]
                # act_min_distance[p]=max_distance_to_segment if p not in act_min_distance.keys() else act_min_distance[p]
                # if p not in point_hull_identifier.keys():
                #     point_hull_data = {
                #         "value": 0,
                #         "class": None,
                #         "membership_values": None,
                #         "road_id": None,
                #         "segment_key": None,
                #         "actual_distance": None,
                #         "segment_start_coordinate": None,
                #         "segment_end_coordinate": None,
                #         "segment_start_id": None,
                #         "segment_end_id": None,
                #     }
                act_dist = distance_point_to_segment(p, lp1, lp2)
                if road_id not in min_distances:
                    min_distances[road_id] = {}
                if segment_key not in min_distances[road_id]:
                    min_distances[road_id][segment_key] = {}
                if act_dist <= max_distance_to_segment:
                    segment_point_count[road_id][segment_key] += 1
                    cluster = marker_classification[p].index(max(marker_classification[p]))+1
                    min_distances[road_id][segment_key][segment_point_count[road_id][segment_key]] = {
                        "point_coordinates": p,
                        "distance_to_segment": act_dist,
                        "membership_values": marker_classification[p],
                        "class": cluster,
                    }
            
    for road_id, road_data in roads.items():
        (
            way_points,
            bounding_box,
            segment_nodes,
            highway_type,
            road_name,
            maxspeed,
            is_oneway,
            is_accessible,
            points_covered,
        ) = road_data
        road_id = int(road_id)
        if road_id in min_distances:
            structured_data[road_id] = {
                "id": road_id,
                "name": road_name,
                "maxspeed": maxspeed,
                "is_oneway": is_oneway,
                "is_accessible": is_accessible,
                "highway_type": highway_type,
                "segments": {},
            }
        else:
            continue

        for i in range(len(way_points) - 1):
            segment_key = i + 1
            lp1 = way_points[i]
            lp2 = way_points[i + 1]
            segment_data = {
                "segment_start_id": segment_nodes[i],
                "segment_end_id": segment_nodes[i + 1],
                "segment_start_coordinate": [lp1],
                "segment_end_coordinate": [lp2],
                "number_of_points": segment_point_count[road_id][segment_key],
                "points": (
                    min_distances[road_id][segment_key]
                    if segment_key in min_distances[road_id]
                    else {}
                ),
            }

            segment_data["number_of_points"] = segment_point_count[road_id][segment_key]
            # find total benefit for the segment for each cluster
            segment_data["total_benefit"] = {}
            for i in range(1, number_of_classes+1):
                segment_data["total_benefit"][i] = 0
            for point_data in segment_data["points"].values():
                membership_values = point_data["membership_values"]
                for i in range(1, number_of_classes+1):
                    segment_data["total_benefit"][i] += membership_values[i - 1]
            # Avoid redundant addition of the entire list
            if segment_data["points"] == {}:
                segment_data.pop("points")
                segment_data["number_of_points"] = 0
            structured_data[road_id]["segments"][segment_key] = segment_data
    os.makedirs(transient_dir, exist_ok=True)
    write_file_path = os.path.join(transient_dir, "econ_pm_output.json")
    # Save to file
    with open(write_file_path, "w") as f:
        json.dump(structured_data, f)
    
    #for checking
    if DEBUG:
        debug_dir = os.path.join(transient_dir, "debug")
        os.makedirs(debug_dir, exist_ok=True)
        with open(os.path.join(debug_dir,"econ_pmo_debug_tabbed.json"), "w") as f:
            json.dump(structured_data, f, indent=4)
        
        # Save isolated roads list for reference
        with open(os.path.join(debug_dir, "econ_isolated_roads.json"), "w") as f:
            json.dump(isolated_roads, f, indent=4)
    
    # # Convert tuple keys to strings
    # point_hull_identifier_serializable = {
    #     str(key): value for key, value in point_hull_identifier.items()
    # }

    # Save to JSON
    with open(os.path.join(transient_dir, "point_hull_collection.json"), "w") as f:
        json.dump(segment_hull_identifier, f)

    # For debugging
    if DEBUG:
        debug_dir = os.path.join(transient_dir, "debug")
        os.makedirs(debug_dir, exist_ok=True)
        with open(os.path.join(debug_dir, "hull_debug.json"), "w") as f:
            json.dump(segment_hull_identifier, f, indent=4)
    
    end_time = time.time()
    execution_time = end_time - start_time
    if DEBUG:
        print(f"Point mapping completed in {execution_time:.2f} seconds")
    # print("Execution time:", execution_time / 60, "minutes")
    # print("done")
    return len(classification)


if __name__ == "__main__":
    
    working_directory = 'work_dir/minimal_test'
    is_reversed = False
    
    # ============================================================================
    # OPTION 1: Use HPE optimal grid cells (converts them to points.csv)
    # ============================================================================
    use_optimal_grid_cells = True  # Set to True to use HPE output
    num_clusters = 15  # Must match the number of clusters in your analysis
    
    # ============================================================================
    # OPTION 2: Use existing points.csv (traditional approach)
    # ============================================================================
    # use_optimal_grid_cells = False  # Set to False to use existing points.csv
    # num_clusters = 9  # Still needed for processing
    
    print("🔧 Economics Point Mapping (Connected)")
    print("=" * 80)
    if use_optimal_grid_cells:
        print("📊 Mode: Using HPE optimal grid cells")
        print(f"🔢 Clusters: {num_clusters}")
        print(f"📍 Will convert optimal_grid_cells*.json → points.csv")
    else:
        print("📊 Mode: Using existing points.csv")
    print("=" * 80)
    print()
    
    point_mapping(
        working_directory,
        50,  # This is the maximum distance to the road (meters)
        is_reversed,
        use_optimal_grid_cells=use_optimal_grid_cells,
        num_clusters=num_clusters
    )
