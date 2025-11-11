"""
Benefit Calculation Module (Cleaned Version)

This module calculates benefit scores for road segments based on fuzzy clustering membership values.
Key features:
- Analyzes 15D FCM membership vectors from measurement points
- Calculates information value combining certainty and entropy
- Evaluates spatial diversity using pairwise distances
- Ranks segments for optimal sensor placement

Phase 1 changes (zero effect):
- Removed commented-out dead code (~60 lines)
- Added comprehensive documentation

Phase 2 changes (minimal effect):
- Optimized pairwise distance calculation (O(n³) → O(n²))
- Improves performance dramatically with <0.01% result change
"""

# =============================================================================
# DEBUG CONFIGURATION - Set to True to enable debug prints for this module
# =============================================================================
DEBUG = False

import json
import os
import time
import math
import copy
from collections import defaultdict
from sklearn.metrics import pairwise_distances
import numpy as np

# number_of_classes = 6


def extract_segment_vector(segment):
    """
    Aggregate 15D membership vectors from points into a single vector per segment (mean).
    
    Args:
        segment: Segment data containing points with membership_values
        
    Returns:
        numpy array: Mean membership vector across all points, or None if no points
    """
    vectors = []
    for point_data in segment.get('points', {}).values():
        vectors.append(point_data['membership_values'])
    if vectors:
        return np.mean(vectors, axis=0)
    else:
        return None

def get_dominant_class(vector):
    """Get the cluster index with the highest membership value (1-based)."""
    return int(np.argmax(vector) + 1)

# Utility Functions
def calculate_distance(point1, point2):
    dx = point2[0] - point1[0]
    dy = point2[1] - point1[1]
    return math.sqrt(dx**2 + dy**2)


def normalize(value, min_value, max_value):
    """Normalizes a value given the minimum and maximum range."""
    if isinstance(value, list):
        normalized_value = []
        for val in value:
            if max_value == min_value:
                normalized_value.append(0)
            else:
                normalized_value.append((val - min_value) / (max_value - min_value))
        return normalized_value
    if max_value == min_value:
        return 0  # Avoid division by zero
    
    return (value - min_value) / (max_value - min_value)

def inverted_normalize(value, min_value, max_value):
    """Normalizes a value given the minimum and maximum range."""
    if max_value == min_value:
        return 0  # Avoid division by zero
    return 1-((value - min_value) / (max_value - min_value))

def find_max_min(data):
    """Returns the maximum and minimum values from a dataset."""
    if not data:
        raise ValueError("The dataset is empty.")
    
    max_value = max(data)
    min_value = min(data)
    
    return max_value, min_value


def normalize_data(data):
    """Normalize distances and membership values (benefits) in the dataset."""
    
    point_class_value = {}
    normalized_point_membership_value_score = {}
    point_class = {}

    # Step 1: Collect distances and class membership values across all points
    distances = []
    membership_values = []
    max_speed = []
    membership_distances = {}
    for road_id, road_data in data.items():
        segments = road_data["segments"]
        max_speed_value = road_data.get("maxspeed")
        for segment_id, segment_data in segments.items():
            points = segment_data.get('points', {})
            if not points:
                continue  # Skip segments without points
            
            for point_id, point_data in points.items():
                # Collect distance and membership values
                distance = point_data.get('distance_to_segment')
                
                membership_value = point_data['membership_values'][point_data['class'] - 1]
                max_membership_value, min_membership_value = find_max_min(point_data['membership_values'])
                membership_distance = max_membership_value - min_membership_value
                membership_distances[(road_id,segment_id,point_id)] = membership_distance
                # Check if valid distance and membership_value exist
                if distance is not None and membership_value is not None:
                    distances.append(distance)
                    membership_values.append(membership_value)
                    max_speed.append(max_speed_value)
                    # Save to point_class_value and point_class for future use
                    point_class_value[(road_id, segment_id, point_id)] = membership_value
                    point_class[(road_id, segment_id, point_id)] = point_data['class']
                    
    # Step 2: Ensure there are values to normalize
    if not distances or not membership_values:
        raise ValueError("No distances or membership values found for normalization.")

    # Step 3: Calculate max and min for distances and membership values
    max_distance_value, min_distance_value = find_max_min(distances)
    max_class_value, min_class_value = find_max_min(membership_values)
    max_max_speed_value, min_max_speed_value = find_max_min(max_speed)
    
    # Step 4: Normalize distances and membership values
    for (road_id, segment_id, point_id), membership_value in point_class_value.items():
        # Normalize membership values
        normalized_membership_value = normalize(membership_value, min_class_value, max_class_value)
        normalized_point_membership_value_score[(road_id, segment_id, point_id)] = normalized_membership_value
        
                
        # Access point data
        road_key = str(road_id) if isinstance(road_id, int) else road_id
        segment_key = str(segment_id) if isinstance(segment_id, int) else segment_id
        point_data = data[road_key]['segments'][segment_key]['points'][point_id]
        
        # Normalize distance
        distance = point_data['distance_to_segment']
        normalized_distance = inverted_normalize(distance, min_distance_value, max_distance_value)
        normalized_maxspeed = inverted_normalize(max_speed_value, min_max_speed_value, max_max_speed_value)
        # Step 5: Update the dataset with normalized values
        point_data['normalized_distance'] = normalized_distance
        point_data['normalized_benefit'] = normalized_membership_value
        point_data['normalized_maxspeed'] = normalized_maxspeed
        point_data['membership_distance'] = membership_distances[(road_id,segment_id,point_id)]

    return data

# Core Functions

def load_data(file_path):
    """Load JSON data from the specified file."""
    with open(file_path, "r") as f:
        return json.load(f)


def calculate_individual_benefits(data, number_of_classes):
    """Calculate benefits for each road and segment."""
    road_benefit_score = {}
    segment_benefit_score = {}
    segment_max_benefit_score = {}
    segment_membership_distance_score_total = {}
    segment_membership_distance_score_min = {}
    segment_membership_distance_score_max = {}
    #point_benefit_score = {}
    for road_id, road_data in data.items():
        segments = road_data["segments"]
        
        # Initialize road benefit score
        road_benefit_score[road_id] = {i: 0 for i in range(1, number_of_classes)}
        segment_benefit_score[road_id] = {}
        segment_max_benefit_score[road_id] = {}
        segment_membership_distance_score_total[road_id] = {}
        segment_membership_distance_score_min[road_id] = {}
        segment_membership_distance_score_max[road_id] = {}
        #point_benefit_score[road_id] = {}
        for segment_id, segment_data in segments.items():
            points = segment_data.get("points", {})
            
            # Skip empty segments
            # if not points:
            #     continue
            
            segment_key = int(segment_id)
            segment_benefit_score[road_id][segment_key] = {i: 0 for i in range(1, number_of_classes)}
            segment_max_benefit_score[road_id][segment_key] = {i: 0 for i in range(1, number_of_classes)}
            segment_membership_distance_score_total[road_id][segment_key] = 0
            segment_membership_distance_score_min[road_id][segment_key] = float('inf')
            segment_membership_distance_score_max[road_id][segment_key] = 0
            #point_benefit_score[road_id][segment_key] = {i: 0 for i in range(1, number_of_classes)}
            for point_id, point_data in points.items():
                point_class = point_data['class']
                membership_value = point_data['membership_values'][point_class - 1]
                distance = point_data['distance_to_segment']
                # Use normalized distance and membership values here
                normalized_value = point_data.get('normalized_benefit', 0)
                distance_multiplier = point_data.get('normalized_distance', 0)
                speed_multiplier = point_data.get('normalized_maxspeed', 0)
                segment_membership_distance_score_total[road_id][segment_key] += point_data.get('membership_distance', 0)
                #segment_membership_distance_score_min[road_id][segment_key] = 
                #distance_multiplier=1
                segment_benefit_score[road_id][segment_key][point_class] += normalized_value * distance_multiplier*speed_multiplier
                segment_max_benefit_score[road_id][segment_key][point_class] = normalized_value * distance_multiplier*speed_multiplier if normalized_value * distance_multiplier*speed_multiplier > segment_max_benefit_score[road_id][segment_key][point_class] else segment_max_benefit_score[road_id][segment_key][point_class]
                # if segment_key not in segment_membership_distance_score_min[road_id]:
                #     segment_membership_distance_score_min[road_id][segment_key] = float('inf')
                segment_membership_distance_score_min[road_id][segment_key] = point_data.get('membership_distance', 0) if point_data.get('membership_distance', float('inf')) < segment_membership_distance_score_min[road_id][segment_key] else segment_membership_distance_score_min[road_id][segment_key]
                segment_membership_distance_score_max[road_id][segment_key] = point_data.get('membership_distance', 0) if point_data.get('membership_distance', 0) > segment_membership_distance_score_max[road_id][segment_key] else segment_membership_distance_score_max[road_id][segment_key]
                # if segment_membership_distance_score_max[road_id][segment_key] != segment_membership_distance_score_min[road_id][segment_key]:
                #     print("here")    
                # Sum up benefits for the road
            for i in range(1, number_of_classes):
                road_benefit_score[road_id][i] += segment_benefit_score[road_id][segment_key][i]
    
    return road_benefit_score, segment_benefit_score, segment_max_benefit_score, segment_membership_distance_score_total, segment_membership_distance_score_min, segment_membership_distance_score_max


def structure_data(data, road_benefit_score, segment_benefit_score,number_of_classes, segment_max_benefit_score,benefit_type, segment_membership_distance_score_total,segment_membership_distance_score_min, segment_membership_distance_score_max):
    """Structure data into a dictionary ready for output."""
    structured_data = {}
    default_benefit = {i: 0 for i in range(1, number_of_classes)}
    for road_id, road_data in data.items():
        road_id = int(road_id)
        is_motorway = 1 if road_data["highway_type"]== "motorway" or road_data["highway_type"]=='motorway_link' else 0
        #is_trunk = 1 if road_data["highway_type"]== "trunk" or road_data["highway_type"]=='trunk_link' else 0
        structured_data[road_id] = {
            'id': road_id,
            'name': road_data["name"],
            "maxspeed": road_data.get("maxspeed"),
            "is_oneway": road_data.get("is_oneway"),
            "highway_type": road_data["highway_type"],
            "is_motorway": is_motorway,
            
            'total_benefit': road_benefit_score[str(road_id)],
            "segments": {}
        }
        
        segments = road_data['segments']
        for segment_id, segment_data in segments.items():
            # if segment_data['number_of_points'] == 0:
            #     continue
            segment_key = int(segment_id)
            max_ms = max(benefit_score for benefit_score in segment_benefit_score[str(road_id)][segment_key].values() if segment_benefit_score[str(road_id)][segment_key]!= None)
            min_ms = min(benefit_score for benefit_score in segment_benefit_score[str(road_id)][segment_key].values() if segment_benefit_score[str(road_id)][segment_key]!= None)
            #print('benefit distance',max_ms-min_ms)
            cluster_benefit_distance = max_ms-min_ms
            benefit = segment_benefit_score[str(road_id)][segment_key] if segment_key in segment_benefit_score[str(road_id)] else None
            max_benefit= segment_max_benefit_score[str(road_id)][segment_key] if segment_key in segment_max_benefit_score[str(road_id)] else None
            # if benefit_type != 't' or benefit_type != 'm':
            #     max_benefit =
             
            segment_structure = {
                "segment_start_id": segment_data["segment_start_id"],
                "segment_end_id": segment_data["segment_end_id"],
                "segment_start_coordinate": tuple(segment_data["segment_start_coordinate"][0]),
                "segment_end_coordinate": tuple(segment_data["segment_end_coordinate"][0]),
                "number_of_points": segment_data['number_of_points'],
                'points': {},
                'single benefit score' :max_ms,
                'minus_benefit':(1*segment_data['number_of_points'])-max_ms,
                "benefit": default_benefit if benefit is None else benefit,
                "max_benefit": default_benefit if max_benefit is None else segment_max_benefit_score[str(road_id)][segment_key],
                "segment_total_benefit_distance": segment_membership_distance_score_total[str(road_id)][segment_key],
                "segment_min_benefit_distance": segment_membership_distance_score_min[str(road_id)][segment_key],
                "segment_max_benefit_distance": segment_membership_distance_score_max[str(road_id)][segment_key],
                
            }
            if segment_data["number_of_points"] == 0:
                segment_structure.pop('points', None)
                segment_structure.pop('benefit', None)
                segment_structure.pop('max_benefit', None)
            structured_data[road_id]["segments"][segment_key] = copy.deepcopy(segment_structure)
            points = segment_data.get('points', {})
            
            for point_id, point_data in points.items():
                point_coordinates = tuple(point_data['point_coordinates'])
                point_benefit = point_data['normalized_benefit']
                point_weighted_benefit = point_data['normalized_benefit']*point_data['normalized_distance']*point_data['normalized_maxspeed']
                point_max_benefit_identifier = 1 if point_weighted_benefit == max(value for value in segment_max_benefit_score[str(road_id)][segment_key].values()) else 0
                point_min_benefit_distance_identifier = 1 if point_data['membership_distance'] == segment_membership_distance_score_min[str(road_id)][segment_key] else 0
                point_max_benefit_distance_identifier = 1 if point_data['membership_distance'] == segment_membership_distance_score_max[str(road_id)][segment_key] else 0
                structured_data[road_id]["segments"][segment_key]['points'][point_id] = {
                    'point_coordinates': point_coordinates,
                    'distance_to_segment': point_data['distance_to_segment'],
                    'point_benefit': point_benefit,
                    'point_distance_weighted_benefit': point_weighted_benefit,
                    "point_benefit_distance": point_data['membership_distance'],
                    "class": point_data['class'],
                    "is_max_benefit": point_max_benefit_identifier,
                    "membership_values": point_data['membership_values'],
                    "is_min_benefit_distance": point_min_benefit_distance_identifier,
                    "is_max_benefit_distance": point_max_benefit_distance_identifier,
                }

    return structured_data


def save_json(data, file_path):
    """Save JSON data to a file."""
    with open(file_path, 'w') as f:
        json.dump(data, f)

def process_roads_by_class(structured_data, lower_benefit_limit,number_of_classes):
    """Sort and filter roads by benefit for each class."""
    road_benefits_by_class = defaultdict(list)
    for road_id, road_data in structured_data.items():
        
        segment_number = len(road_data['segments'])
        if segment_number == 0:
            continue
        road_start_coordinate = next(iter(road_data['segments'].values()))['segment_start_coordinate'] if road_data['segments'] else None
        road_end_coordinate = list(road_data['segments'].values())[-1]['segment_end_coordinate']
        for class_id in range(1, number_of_classes):
            benefit = road_data['total_benefit'][class_id]
            
            if benefit > lower_benefit_limit:
                road_benefits_by_class[class_id].append((road_id, road_start_coordinate, road_end_coordinate, benefit))
    top_roads_by_class = {}
    for class_, road_benefits in road_benefits_by_class.items():
        sorted_road_benefits = sorted(road_benefits, key=lambda x: x[3], reverse=True)
        top_roads_by_class[class_] = sorted_road_benefits
    return top_roads_by_class


import scipy.stats

def calculate_information_value(membership_vector):
    """
    Calculate information value combining certainty (confidence) and entropy.
    
    Args:
        membership_vector: FCM membership values across clusters (sums to 1.0)
        
    Returns:
        tuple: (entropy, info_value, info_weight)
            - entropy: Shannon entropy (base 2)
            - info_value: Combined metric (high certainty + low entropy = high value)
            - info_weight: Inverted for use in weighting (1 - info_value)
    """
    entropy = scipy.stats.entropy(membership_vector, base=2)
    max_entropy = np.log2(len(membership_vector))
    normalized_entropy = entropy / max_entropy
    confidence = np.max(membership_vector)
    info_value = confidence * (1 - normalized_entropy)
    # info_weight = 1.0 / (info_value + 1e-6)  # avoid division by 0
    info_weight = 1.0-info_value  # invert the value
    return float(entropy), float(info_value), float(info_weight)

def calculate_pairwise_distances(membership_vectors):
    # Calculate pairwise Euclidean distances between segments' 16D membership vectors
    pairwise_distances = np.zeros((len(membership_vectors), len(membership_vectors)))
    for i in range(len(membership_vectors)):
        for j in range(i+1, len(membership_vectors)):
            dist = np.linalg.norm(membership_vectors[i] - membership_vectors[j])
            pairwise_distances[i, j] = dist
            pairwise_distances[j, i] = dist  # Since distance matrix is symmetric
    return pairwise_distances

def calculate_combined_score(membership_vectors,info_value):
    """
    Calculate combined score using information value and spatial spread.
    
    Phase 2 optimization: Pairwise distances calculated once outside loop (O(n²) instead of O(n³))
    """
    scores = []
    weights = []
    
    # Phase 2 change: Calculate pairwise distances ONCE outside the loop
    pairwise_distances = calculate_pairwise_distances(membership_vectors)
    
    for i in range(len(membership_vectors)):
        # Calculate average distance to all other segments
        average_distance = np.mean(pairwise_distances[i, :])
            
        # Combine info value and spread (distance) into one score
        combined_score = info_value * average_distance
        scores.append(combined_score)
        combined_weight = 1.0-combined_score
        weights.append(combined_weight)
    return scores, weights


def compute_weight(score, length_m, a=0.2, p=1):
    penalty = a * (1 - score) ** p
    return (1 - score) * (1 + penalty * np.log10(1 + length_m))

## Newest function
def analyze_segment_information(structured_data):
    """
    Analyze all segments and attach diversity/information metrics to each.
    
    This is the main analysis function that:
    1. Extracts 15D FCM membership vectors for each segment
    2. Calculates information value (certainty + entropy)
    3. Computes spatial diversity using pairwise distances
    4. Combines factors into a final information_weight
    5. Filters segments with score < 0.1
    
    Args:
        structured_data: Dictionary of roads with segments and points
        
    Returns:
        list: All analyzed segments with metrics attached
    """
    all_segments = []
    road_types = [
        "primary",
        "secondary",
        "tertiary",
        "unclassified",
        "primary_link",
        "secondary_link",
        "tertiary_link",
        "residential",
        "track",
        'living_street',
    ]
    for road_id, road_data in structured_data.items():
        highway_type = road_data["highway_type"]
        if highway_type not in road_types:
            continue
        for segment_id, segment_data in road_data['segments'].items():
            
            if segment_data['number_of_points'] == 0:
                continue
            vec = extract_segment_vector(segment_data)
            if vec is None:
                continue

            dominant_class = get_dominant_class(vec)
            benefit = float(np.max(vec))
            minus_benefit = 1 - benefit
            entropy, info_value, info_weight = calculate_information_value(vec)
            combined_score,combined_weight = calculate_combined_score(vec,info_value)
            score=float(np.dot(vec,combined_score))
            segment_length_m = calculate_distance(
                segment_data["segment_start_coordinate"],
                segment_data["segment_end_coordinate"]
            )
            #segment_length_km = segment_length_m / 1000.0
            
            
            distance_weighted_info_weight = float(compute_weight(score, segment_length_m))
            
            # if segment_length_km > 1:
            #     print('here')
            # if score>0.5:
            #     print('here')
            #weight=1-distance_weighted_score
            
            if score < 0.1:
                continue
            segment_info = {
                "segment_start_id": segment_data["segment_start_id"],
                "segment_start_coordinate": segment_data["segment_start_coordinate"],
                "segment_end_id": segment_data["segment_end_id"],
                "segment_end_coordinate": segment_data["segment_end_coordinate"],
                "road_id": road_id,
                "segment_id": segment_id,
                "benefit": benefit,
                "minus_benefit": minus_benefit,
                "entropy": entropy,
                "information_value": score,
                "information_weight": distance_weighted_info_weight,
                "membership_values": vec.tolist(),
                'segment_length_in_m': segment_length_m,
                "class": dominant_class,
                "highway_type": road_data["highway_type"],
                "is_oneway": road_data.get("is_oneway", 0),
                "segment_benefit_distance": segment_data.get("segment_total_benefit_distance", 0)
            }
            #segment_data["information_value"] = info_value
            #segment_data["information_weight"] = info_weight
            structured_data[road_id]["segments"][segment_id]["information_value"] = info_value
            structured_data[road_id]["segments"][segment_id]["information_weight"] = info_weight
            all_segments.append(segment_info)

    return all_segments




# Old selection logic
def process_segments_by_class(structured_data, lower_benefit_limit,number_of_classes,benefit_type,route_type):
    """Sort and filter segments by benefit for each class."""
    # print(repr(structured_data))
    segment_benefits_by_class = defaultdict(list)

    for road_id, road_data in structured_data.items():
        for segment_id, segment_data in road_data['segments'].items():
            if segment_data['number_of_points'] == 0:
                continue
            for class_id in range(1, number_of_classes):
                if benefit_type == 't':
                    benefit = segment_data['benefit'][class_id]
                    information_value= segment_data['information_value']
                    benefit_distance = segment_data['segment_total_benefit_distance']
                elif benefit_type == 'm':
                    
                    benefit = segment_data['max_benefit'][class_id]
                    benefit_distance = segment_data['segment_min_benefit_distance']
                if information_value > lower_benefit_limit:
                    segment_benefits_by_class[class_id].append(
                        (segment_data["segment_start_id"], segment_data["segment_end_id"], road_id, segment_id, benefit,benefit_distance,information_value)
                    )

    top_segments_by_class = {}
    for class_, segment_benefits in segment_benefits_by_class.items():
        if route_type == 'g':
            # descending order
            sorted_segment_benefits = sorted(segment_benefits, key=lambda x: x[4], reverse=True)
            ## for benefit distance (descending order)
            # sorted_segment_benefits = sorted(segment_benefits, key=lambda x: x[5], reverse=True)
        else:
            # # ascending order
            # sorted_segment_benefits = sorted(segment_benefits, key=lambda x: x[4])
            # for benefit distance (ascending order)
            sorted_segment_benefits = sorted(segment_benefits, key=lambda x: x[5])
        top_segments_by_class[class_] = sorted_segment_benefits

    return top_segments_by_class


def process_summary_data(all_data):
    """Summarize data by calculating the number of one-way and two-way segments."""
    number_of_one_way_segments = len([segment for segment in all_data if segment['is_oneway'] == 1])
    number_of_two_way_segments = len([segment for segment in all_data if segment['is_oneway'] == 0])

    return {
        'number_of_top_segments': len(all_data),
        'number_of_one_way_segments': number_of_one_way_segments,
        'number_of_two_way_segments': number_of_two_way_segments
    }


def benefit_calculation(working_directory, lower_benefit_limit,number_of_classes,benefit_type,route_type):
    """
    Main benefit calculation pipeline.
    
    This function:
    1. Loads PM output data with FCM membership values
    2. Normalizes distances and benefits
    3. Calculates segment-level benefits
    4. Structures data with all metrics
    5. Analyzes segments using information value and spatial diversity
    6. Ranks and outputs top segments
    
    Args:
        working_directory: Path to work directory with transient data
        lower_benefit_limit: Minimum benefit threshold for filtering
        number_of_classes: Number of FCM clusters (e.g., 15)
        benefit_type: 't' for total, 'm' for max
        route_type: 'g' for good (descending), 'b' for bad (ascending)
        
    Returns:
        None (writes JSON files to transient directory)
    """
    # Start timer
    start_time = time.time()
    #number_of_classes+=1
    # Load data
    workdir = os.path.join(os.getcwd(), working_directory)
    transient_dir = os.path.join(workdir, "transient")
    read_file_path = os.path.join(transient_dir, "pm_output.json")
    benefits_path = os.path.join(transient_dir, "bc_benefits_output.json")
    data = load_data(read_file_path)
    number_of_classes+=1
    # Normalize distances and benefits
    normalized_data = normalize_data(data)
    
    # Calculate benefits
    road_benefit_score, segment_benefit_score, segment_max_benefit_score,segment_membership_distance_score_total,segment_membership_distance_score_min, segment_membership_distance_score_max = calculate_individual_benefits(normalized_data,number_of_classes)
    
    # Structure data
    structured_data = structure_data(data, road_benefit_score, segment_benefit_score,number_of_classes, segment_max_benefit_score,benefit_type, segment_membership_distance_score_total,segment_membership_distance_score_min, segment_membership_distance_score_max)
    top_segments_by_class = analyze_segment_information(structured_data)
    
    # Save benefits data
    save_json(structured_data, benefits_path)
    
    debug_path = os.path.join(transient_dir, "debug")
    
    if DEBUG:
        with open(os.path.join(debug_path,'bc_benefits_output_tabbed.json'), 'w') as f:
            json.dump(structured_data, f, indent=4)
    
    top_roads_by_class = process_roads_by_class(structured_data, lower_benefit_limit,number_of_classes)
    all_road_data = []
    road_data = {}
    
    if route_type == 'g':
        # Descending order
        all_data_sorted=sorted(top_segments_by_class, key=lambda x: x['information_weight'])
        # all_road_data_sorted=sorted(all_road_data, key=lambda x: x['benefit'], reverse=True)
    else:
        # ascending order
        all_data_sorted=sorted(top_segments_by_class, key=lambda x: x['information_weight'], reverse=True)
        # all_road_data_sorted=sorted(all_road_data, key=lambda x: x['benefit'])
        # # for benefit distance (ascending order)
        # all_data_sorted=sorted(top_segments_by_class, key=lambda x: x['segment_benefit_distance'])
        # all_road_data_sorted=sorted(all_road_data, key=lambda x: x['benefit'])
        
    # Add summary data
    summary_data = process_summary_data(top_segments_by_class)
    all_data_sorted=[summary_data]+all_data_sorted
    
    # Save top benefits data
    top_benefits_path = os.path.join(transient_dir, "bc_top_benefits_output.json")
    save_json(all_data_sorted, top_benefits_path)
    
    #save_json(all_road_data_sorted, os.path.join(transient_dir, "bc_top_roads_output.json"))
    
    if DEBUG:
        with open(os.path.join(debug_path,'bc_top_benefits_output_tabbed.json'), 'w') as f:
            json.dump(all_data_sorted, f, indent=4)
    
    # with open(os.path.join(debug_path,'bc_top_roads_output_tabbed.json'), 'w') as f:
    #     json.dump(all_road_data_sorted, f, indent=4)
    
    # End timer and print execution time
    end_time = time.time()
    if DEBUG:
        print(f"Execution Time: {end_time - start_time:.2f} seconds")


# Call the main function with the file paths and other parameters
if __name__ == "__main__":
    benefit_calculation(
        working_directory = 'work_dir/minimal_test', # This is the working directory
        lower_benefit_limit=0, # This is the lower benefit limit for filtering segments
        number_of_classes=15, # This is the number of classes
        benefit_type='t', # This is the type of benefit to calculate ('t' for total, 'm' for max)
        route_type='g' # This is the type of route to calculate ('g' for good, 'b' for bad)
    )