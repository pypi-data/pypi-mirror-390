"""
HPE Single Mode - Filtered to Segment-Covered Cells Only
This file filters grid cells to only those covered by segments before optimization.
"""

# =============================================================================
# DEBUG CONFIGURATION - Set to True to enable debug prints for this module
# =============================================================================
DEBUG = False

import numpy as np
import json
import time
import os
from scipy.spatial import ConvexHull
from scipy.optimize import minimize
import matplotlib.pyplot as plt
from tqdm import tqdm
from datetime import datetime


def create_summary_data(mode, start_time, end_time, **kwargs):
    """
    Create a dictionary with execution summary data for JSON output.
    
    Args:
        mode: Execution mode ('single', 'golden', etc.)
        start_time: Execution start time
        end_time: Execution end time
        **kwargs: Additional parameters to include
    
    Returns:
        dict: Summary data structure
    """
    runtime = end_time - start_time
    start_readable = datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')
    end_readable = datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')
    
    summary = {
        "execution_summary": {
            "mode": mode.upper() + "_FILTERED",
            "timing": {
                "start_time": start_readable,
                "end_time": end_readable,
                "runtime_seconds": round(runtime, 2),
                "runtime_minutes": round(runtime/60, 2)
            },
            "parameters": {}
        }
    }
    
    # Add detailed time breakdown for longer runs
    if runtime >= 60:
        hours = runtime // 3600
        minutes = (runtime % 3600) // 60
        seconds = runtime % 60
        if hours > 0:
            summary["execution_summary"]["timing"]["detailed_time"] = f"{int(hours)}h {int(minutes)}m {seconds:.1f}s"
        else:
            summary["execution_summary"]["timing"]["detailed_time"] = f"{int(minutes)}m {seconds:.1f}s"
    
    # Mode-specific parameters
    if mode == 'single':
        summary["execution_summary"]["parameters"] = {
            "num_points": kwargs.get('num_points'),
            "goal_ratio": kwargs.get('goal_ratio'),
            "achieved_ratio": kwargs.get('achieved_ratio'),
            "use_fixed_seeds": kwargs.get('use_fixed_seeds'),
            "debug_seed": kwargs.get('debug_seed') if kwargs.get('use_fixed_seeds') else None,
            "allow_fewer_points": kwargs.get('allow_fewer_points'),
            "predictor_filename": kwargs.get('predictor_filename'),
            "route_filename": kwargs.get('route_filename'),
            "pm_output_filename": kwargs.get('pm_output_filename', 'pm_output.json'),
            "working_directory": kwargs.get('working_directory'),
            "filtering_enabled": True
        }
    
    return summary


def print_execution_summary(mode, start_time, end_time, **kwargs):
    """
    Print a comprehensive summary of the execution at the beginning of output.
    
    Args:
        mode: Execution mode ('single', 'golden', etc.)
        start_time: Execution start time
        end_time: Execution end time
        **kwargs: Additional parameters to display
    """
    if not DEBUG:
        return
        
    runtime = end_time - start_time
    
    print("=" * 80)
    print("🚀 SENSOR ROUTING OPTIMIZATION SUMMARY (FILTERED)")
    print("=" * 80)
    
    # Convert timestamps to readable format
    start_readable = datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')
    end_readable = datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')
    
    print(f"🔧 Mode: {mode.upper()} + SEGMENT FILTERING")
    
    if runtime > 0.1:  # Only show timing details if meaningful
        print(f"🕐 Start Time: {start_readable}")
        print(f"🕐 End Time: {end_readable}")
        print(f"⏱️  Total Runtime: {runtime:.2f} seconds ({runtime/60:.2f} minutes)")
        if runtime >= 60:
            hours = runtime // 3600
            minutes = (runtime % 3600) // 60
            seconds = runtime % 60
            if hours > 0:
                print(f"⏱️  Detailed Time: {int(hours)}h {int(minutes)}m {seconds:.1f}s")
            else:
                print(f"⏱️  Detailed Time: {int(minutes)}m {seconds:.1f}s")
    else:
        print(f"🕐 Started: {start_readable}")
        print(f"⏱️  Status: Starting optimization...")
    
    # Mode-specific parameters
    if mode == 'single':
        print(f"📊 Points Tested: {kwargs.get('num_points', 'N/A')}")
        print(f"🎯 Target Ratio: {kwargs.get('goal_ratio', 'N/A'):.1f}%")
        if kwargs.get('achieved_ratio') is not None:
            print(f"📈 Achieved Ratio: {kwargs.get('achieved_ratio'):.1f}%")
        print(f"🌱 Fixed Seeds: {kwargs.get('use_fixed_seeds', 'N/A')}")
        if kwargs.get('use_fixed_seeds'):
            print(f"🔢 Debug Seed: {kwargs.get('debug_seed', 'N/A')}")
    
    # Working directory and file information
    print(f"📁 Working Directory: {kwargs.get('working_directory', 'N/A')}")
    print(f"📄 Predictor File: {kwargs.get('predictor_filename', 'N/A')}")
    print(f"🗺️  Route File: {kwargs.get('route_filename', 'N/A')}")
    print(f"🔍 PM Output File: {kwargs.get('pm_output_filename', 'pm_output.json')}")
    print(f"✨ Filtering: ENABLED (only segment-covered cells)")
    print("=" * 80)
    print()


def evaluateVolume(x, predictor_data):
    """Evaluate convex hull volume for given indices."""
    # Round to get integer indices
    indices = np.round(x).astype(int)
    
    # Check bounds
    if np.any(indices < 0) or np.any(indices >= len(predictor_data)):
        return 1e6  # Large positive value for invalid indices
    
    # Check for duplicate indices
    if len(np.unique(indices)) < len(indices):
        return 1e6  # Penalize duplicate indices
    
    # Get selected points
    selected_points = predictor_data[indices]
    
    # Check if we have at least 4 points for a 3D hull
    if len(selected_points) < 4:
        return 1e6
    
    try:
        # Create convex hull and return negative volume for minimization
        hull = ConvexHull(selected_points)
        return -hull.volume  # Negative for minimization
    except:
        return 1e6  # Return large positive value for degenerate cases


def particle_swarm_optimization(fitness_func, num_variables, lb, ub, 
                              swarm_size=500, max_iterations=150, 
                              w=0.5, c1=1.5, c2=1.5,
                              use_fixed_seeds=False, debug_seed=42, use_adaptive_params=False):
    """Particle Swarm Optimization implementation."""
    
    if use_fixed_seeds:
        np.random.seed(debug_seed)
    
    # Initialize particles
    positions = np.random.uniform(lb, ub, (swarm_size, num_variables))
    velocities = np.random.uniform(-1, 1, (swarm_size, num_variables))
    
    # Personal best positions and fitness
    personal_best_positions = positions.copy()
    personal_best_fitness = np.full(swarm_size, np.inf)
    
    # Global best
    global_best_position = None
    global_best_fitness = np.inf
    
    # Evaluate initial fitness
    for i in range(swarm_size):
        fitness = fitness_func(positions[i])
        personal_best_fitness[i] = fitness
        
        if fitness < global_best_fitness:
            global_best_fitness = fitness
            global_best_position = positions[i].copy()
    
    # PSO iterations
    original_w = w
    for iteration in range(max_iterations):
        if use_adaptive_params:
            # Adaptive inertia weight - decreases over time
            w = original_w * (1 - iteration / max_iterations)
        
        for i in range(swarm_size):
            # Update velocity
            r1, r2 = np.random.random(2)
            cognitive = c1 * r1 * (personal_best_positions[i] - positions[i])
            social = c2 * r2 * (global_best_position - positions[i])
            velocities[i] = w * velocities[i] + cognitive + social
            
            # Update position
            positions[i] += velocities[i]
            
            # Apply bounds
            positions[i] = np.clip(positions[i], lb, ub)
            
            # Evaluate fitness
            fitness = fitness_func(positions[i])
            
            # Update personal best
            if fitness < personal_best_fitness[i]:
                personal_best_fitness[i] = fitness
                personal_best_positions[i] = positions[i].copy()
                
                # Update global best
                if fitness < global_best_fitness:
                    global_best_fitness = fitness
                    global_best_position = positions[i].copy()
        
        # Print progress every 50 iterations
        if iteration % 50 == 0 or iteration == max_iterations - 1:
            if DEBUG:
                print(f"Iteration {iteration}, Best fitness: {global_best_fitness:.6f}, w: {w:.3f}")
    
    if DEBUG:
        print(f"PSO completed after {max_iterations} iterations")
    
    return global_best_position, global_best_fitness


def hpe_optimization(
    working_directory='work_dir/full_test_2',
    num_points=50,
    goal_ratio=100.0,
    use_fixed_seeds=False,
    debug_seed=42,
    predictor_filename='predictors.txt',
    route_filename='initial_route.json',
    pm_output_filename='pm_output.json',
    return_ratio=False,
    fast_search_mode=False,
    allow_fewer_points=False,
    include_summary=False,
    mode=None,
    start_time=None,
    **summary_kwargs
):
    """
    High-performance route optimization with SEGMENT FILTERING.
    Only selects grid cells that are covered by segments in pm_output.json.
    """
    # Configuration from parameters
    USE_FIXED_SEEDS = use_fixed_seeds
    DEBUG_SEED = debug_seed
    
    # Construct file paths
    input_dir = os.path.join(working_directory, 'input')
    transient_dir = os.path.join(working_directory, 'transient')
    predictor_path = os.path.join(input_dir, predictor_filename)
    route_path = os.path.join(input_dir, route_filename)
    pm_output_path = os.path.join(transient_dir, pm_output_filename)
    
    # Ensure transient directory exists
    os.makedirs(transient_dir, exist_ok=True)
    
    # Load predictors and route data
    try:
        dat = np.loadtxt(predictor_path)  # columnwise: X, Y, mask, predictors
        if DEBUG:
            print(f"Loaded predictor data from {predictor_path} with shape: {dat.shape}")
        
        # Check for NaN values in predictor columns only (not X, Y, mask)
        if DEBUG:
            print("Checking for NaN values in predictor columns...")
        predictor_cols = dat[:, 3:]  # Columns 3 and beyond are predictors
        nan_rows = np.isnan(predictor_cols).any(axis=1)
        if DEBUG:
            print(f"Found {np.sum(nan_rows)} rows with NaN values out of {len(dat)} total rows")
        
        if np.sum(nan_rows) > 0:
            # Remove rows with NaN values in predictor columns
            dat = dat[~nan_rows]
            if DEBUG:
                print(f"After removing NaN rows: {dat.shape}")
        
        with open(route_path, 'r') as f:
            so = json.load(f)
        if DEBUG:
            print(f"Loaded solution from {route_path} with {len(so['Path'])} path points")
        
        # Load pm_output to get segment-covered points
        if DEBUG:
            print(f"\n🔍 Loading pm_output from {pm_output_path}...")
        with open(pm_output_path, 'r') as f:
            pm = json.load(f)
        
        # Extract all points covered by segments
        pm_coords = set()
        for road in pm.values():
            for seg in road['segments'].values():
                if seg.get('number_of_points', 0) > 0:
                    for pt in seg['points'].values():
                        pm_coords.add(tuple(pt['point_coordinates']))
        
        if DEBUG:
            print(f"✅ Found {len(pm_coords)} grid cells covered by segments")
        
    except FileNotFoundError as e:
        if DEBUG:
            print(f"Error: File not found - {e}")
        return None
    
    # Set up random seeding strategy
    if USE_FIXED_SEEDS:
        base_seed = DEBUG_SEED
        if DEBUG:
            print(f"Using FIXED random seeds for reproducible results (base seed: {base_seed})")
        random_seed_mode = "FIXED"
    else:
        base_seed = int(time.time()) % 10000  # Keep it reasonable
        if DEBUG:
            print(f"Using TIME-BASED random seeds for varied results (base seed: {base_seed})")
        random_seed_mode = "VARIABLE"
    
    if DEBUG:
        print(f"Random seed mode: {random_seed_mode}")
    
    # Create spatial grid
    unique_x = np.unique(dat[:, 0])
    unique_y = np.unique(dat[:, 1])
    dx = unique_x[1] - unique_x[0] if len(unique_x) > 1 else 1.0
    dy = unique_y[1] - unique_y[0] if len(unique_y) > 1 else 1.0
    
    if DEBUG:
        print(f"Grid dimensions: {len(unique_x)} x {len(unique_y)}")
        print(f"Available data points: {len(dat)}")
        print(f"Expected grid size: {len(unique_x) * len(unique_y)}")
        print(f"Grid spacing: dx={dx:.3f}, dy={dy:.3f}")
    
    # Create coordinate mappings for grid indexing
    x_to_idx = {x: i for i, x in enumerate(unique_x)}
    y_to_idx = {y: i for i, y in enumerate(unique_y)}
    
    # Create full grid structure for route matching
    X_full = np.zeros((len(unique_y), len(unique_x)))
    Y_full = np.zeros((len(unique_y), len(unique_x)))
    for i, y in enumerate(unique_y):
        for j, x in enumerate(unique_x):
            X_full[i, j] = x
            Y_full[i, j] = y
    
    # Match route and map - find grid cells crossed by route
    if DEBUG:
        print("Matching route with map...")
    route_mask = np.zeros(X_full.shape, dtype=bool)
    
    # Use tqdm only if DEBUG is enabled
    path_range = tqdm(range(len(so['Path']) - 1)) if DEBUG else range(len(so['Path']) - 1)
    for ii in path_range:
        # Line interpolation for two neighboring points on the route
        p1 = so['Path'][ii]
        p2 = so['Path'][ii + 1]
        
        dist = np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
        no_pieces = max(int(round(dist)), 2)
        
        x_line = np.linspace(p1[0], p2[0], no_pieces)
        y_line = np.linspace(p1[1], p2[1], no_pieces)
        
        # Map grid index calculation (Python uses 0-based indexing)
        ix = np.round((x_line - X_full[0, 0]) / dx).astype(int)
        iy = np.round((y_line - Y_full[0, 0]) / dy).astype(int)
        
        # Limit to valid indices
        ix = np.clip(ix, 0, X_full.shape[1] - 1)
        iy = np.clip(iy, 0, X_full.shape[0] - 1)
        
        # Flag map grid nodes crossed by route
        route_mask[iy, ix] = True
    
    # Keep only predictor data for grid cells crossed by route
    # We need to match the route_mask with our actual data points
    
    # Create a mapping from grid coordinates to data indices
    coord_to_data_idx = {}
    for i, row in enumerate(dat):
        x, y = row[0], row[1]
        coord_to_data_idx[(x, y)] = i
    
    # Find which data points correspond to route-crossed grid cells
    route_data_indices = []
    for i in range(len(unique_y)):
        for j in range(len(unique_x)):
            if route_mask[i, j]:
                x, y = X_full[i, j], Y_full[i, j]
                if (x, y) in coord_to_data_idx:
                    route_data_indices.append(coord_to_data_idx[(x, y)])
    
    if len(route_data_indices) == 0:
        if DEBUG:
            print("Error: No data points found along the route")
        return None
    
    dat_red = dat[route_data_indices]
    if DEBUG:
        print(f"Reduced data shape (route-crossed): {dat_red.shape}")
    
    # *** NEW: Filter to only segment-covered cells ***
    if DEBUG:
        print(f"\n🔍 FILTERING: Keeping only cells covered by segments...")
    segment_covered_mask = np.array([tuple(row[:2]) in pm_coords for row in dat_red])
    dat_red_before = len(dat_red)
    dat_red = dat_red[segment_covered_mask]
    if DEBUG:
        print(f"✅ Filtered from {dat_red_before} to {len(dat_red)} cells ({100*len(dat_red)/dat_red_before:.1f}%)")
    
    if len(dat_red) == 0:
        if DEBUG:
            print("❌ Error: No segment-covered data points found")
        return None
    
    # Check data before filtering
    if DEBUG:
        print(f"Urban areas (mask==1): {np.sum(dat_red[:, 2] == 1)} points")
        print(f"Non-urban areas (mask!=1): {np.sum(dat_red[:, 2] != 1)} points")
    
    # Double-check for any remaining NaN values (should be none after initial cleaning)
    remaining_nan = np.isnan(dat_red[:, 3:]).any(axis=1)
    if np.sum(remaining_nan) > 0:
        if DEBUG:
            print(f"Warning: Found {np.sum(remaining_nan)} additional rows with NaN values, removing them")
        dat_red = dat_red[~remaining_nan]
        if DEBUG:
            print(f"After removing remaining NaN values: {dat_red.shape}")
    
    # Eliminate grid cells in urban areas (mask == 1)
    dat_red = dat_red[dat_red[:, 2] != 1]
    if DEBUG:
        print(f"After removing urban areas: {dat_red.shape}")
    
    if len(dat_red) == 0:
        if DEBUG:
            print("Error: No valid data points remaining after cleaning")
        return None
    
    # Check if we have enough points for the analysis
    num_predictors = dat_red.shape[1] - 3  # subtract X, Y, mask columns
    min_points_for_hull = num_predictors + 1
    
    if len(dat_red) < min_points_for_hull:
        if DEBUG:
            print(f"Warning: Only {len(dat_red)} points available, but need at least {min_points_for_hull} for {num_predictors}D convex hull")
            print("Consider:")
            print("1. Including urban areas in analysis")
            print("2. Using a different route or expanding the route coverage")
            print("3. Reducing the number of predictor dimensions")
        
        # Option to include urban areas if not enough points
        if len(dat_red) < min_points_for_hull:
            if DEBUG:
                print("Attempting to include urban areas to get more data points...")
            # Reapply segment filter but keep urban areas
            dat_red_all = dat[route_data_indices]
            segment_covered_mask_all = np.array([tuple(row[:2]) in pm_coords for row in dat_red_all])
            dat_red_with_urban = dat_red_all[segment_covered_mask_all]
            
            if len(dat_red_with_urban) >= min_points_for_hull:
                if DEBUG:
                    print(f"Including urban areas: {len(dat_red_with_urban)} points available")
                dat_red = dat_red_with_urban
            else:
                if DEBUG:
                    print(f"Even with urban areas, only {len(dat_red_with_urban)} points available")
                return None
    
    # Normalize data relative to full dataset (excluding NaN values - already done)
    minval = np.min(dat[:, 3:], axis=0)  # dat already has NaN rows removed
    maxval = np.max(dat[:, 3:], axis=0)
    
    # Avoid division by zero
    range_vals = maxval - minval
    range_vals[range_vals == 0] = 1
    
    ndat_red = dat_red.copy()
    ndat_red[:, 3:] = (dat_red[:, 3:] - minval) / range_vals
    
    # Compute convex hull for normalized predictor data
    if DEBUG:
        print("Computing convex hull...")
    
    # Check for remaining NaN or infinite values
    predictor_data = ndat_red[:, 3:]
    if np.any(np.isnan(predictor_data)) or np.any(np.isinf(predictor_data)):
        if DEBUG:
            print(f"Error: NaN or infinite values found in normalized predictor data")
            print(f"NaN count: {np.sum(np.isnan(predictor_data))}")
            print(f"Inf count: {np.sum(np.isinf(predictor_data))}")
        return None
    
    # Check if we have enough points for convex hull
    min_points_needed = predictor_data.shape[1] + 1  # n+1 points for n-dimensional space
    if len(predictor_data) < min_points_needed:
        if DEBUG:
            print(f"Error: Need at least {min_points_needed} points for {predictor_data.shape[1]}-dimensional convex hull, but only have {len(predictor_data)}")
            print("\nPossible solutions:")
            print("1. Check if the route covers enough grid cells")
            print("2. Include urban areas in the analysis")
            print("3. Use a different route with broader coverage")
            print("4. Reduce the number of predictor variables")
            print(f"5. Current predictor dimensions: {predictor_data.shape[1]}")
            
            # Print some sample data for debugging
            print(f"\nSample of available data:")
            print(f"Coordinates (X,Y): {dat_red[:min(5, len(dat_red)), :2]}")
            print(f"Predictor stats: min={np.min(predictor_data, axis=0)}, max={np.max(predictor_data, axis=0)}")
        return None
    
    try:
        hull = ConvexHull(predictor_data)
        hull_point_indices = np.unique(hull.simplices.flatten())
        P_hull = ndat_red[hull_point_indices]
        
        if DEBUG:
            print(f"Convex hull uses {len(hull_point_indices)} points")
    except Exception as e:
        if DEBUG:
            print(f"Error computing convex hull: {e}")
            print(f"Data shape: {predictor_data.shape}")
            print(f"Data stats - min: {np.min(predictor_data):.3f}, max: {np.max(predictor_data):.3f}")
        return None
    
    # Save hull points for verification (only in debug mode)
    if DEBUG:
        points_2d = P_hull[:, :2].tolist()  # Get only X and Y coordinates
        hull_points_path = os.path.join(transient_dir, 'hull_points_check_filtered.json')
        with open(hull_points_path, 'w') as f:
            json.dump(points_2d, f, indent=2)
        print(f"Saved hull points to {hull_points_path}")

    # Calculate full volume
    try:
        full_hull = ConvexHull(P_hull[:, 3:])
        V_full = full_hull.volume
        if DEBUG:
            print(f"Full convex hull volume: {V_full}")
    except Exception as e:
        if DEBUG:
            print(f"Error calculating full volume: {e}")
        return None
    
    if V_full <= 0:
        if DEBUG:
            print("Error: Full volume is zero or negative")
        return None
    
    # Enhanced optimization with different random seeds and parameter sets
    N = len(P_hull)
    if DEBUG:
        print("Starting enhanced optimization with different random seeds and parameter sets...")
        print(f"Target: Select {num_points} points from {N} hull points")
    
    # Different parameter configurations to try
    if fast_search_mode:
        # Adaptive parameters based on target ratio for speed optimization
        target_ratio = goal_ratio - 10  # Infer actual target from goal
        if target_ratio <= 30:
            # Ultra-fast for very low targets  
            param_configs = [
                {"swarm_size": 50, "max_iterations": 20, "w": 0.9, "c1": 2.0, "c2": 2.0},
            ]
            max_random_states = 1
            print("⚡ ULTRA-FAST MODE: Minimal parameters for very low target ratios")
        elif target_ratio <= 50:
            # Balanced-fast for low targets (still needs to find solutions!)
            param_configs = [
                {"swarm_size": 100, "max_iterations": 50, "w": 0.9, "c1": 2.0, "c2": 2.0},
            ]
            max_random_states = 1
            print("⚡ BALANCED-FAST MODE: Optimized parameters for low target ratios")
        elif target_ratio <= 70:
            # Fast for medium targets
            param_configs = [
                {"swarm_size": 150, "max_iterations": 60, "w": 0.9, "c1": 2.0, "c2": 2.0},
            ]
            max_random_states = 1
            print("🚀 SPEED MODE: Reduced parameters for medium target ratios")
        else:
            # Balanced for high targets (need more precision)
            param_configs = [
                {"swarm_size": 200, "max_iterations": 75, "w": 0.9, "c1": 2.0, "c2": 2.0},
            ]
            max_random_states = 2
            print("🚀 FAST SEARCH MODE: Balanced parameters for high target ratios")
    else:
        # Full parameters for final optimization (more accurate)
        param_configs = [
            {"swarm_size": 300, "max_iterations": 100, "w": 0.9, "c1": 2.0, "c2": 2.0},  # Balanced
            {"swarm_size": 200, "max_iterations": 120, "w": 0.8, "c1": 2.5, "c2": 1.5},  # Exploitation focused
        ]
        max_random_states = 3  # 2 random states for thoroughness
    
    # Initialize optimization variables
    opt_ratio = 0
    opt_best_idx = None
    run_count = 0
    for ii in range(1, max_random_states):  # Use variable number of states
        for config_idx, config in enumerate(param_configs):
            run_count += 1
            if DEBUG:
                print(f"\n================Run {run_count}: Random state: {ii}, Config: {config_idx+1}================")
                print(f"Config: {config}")
            
            # Use configurable seeding strategy
            if USE_FIXED_SEEDS:
                current_seed = base_seed + ii * 10 + config_idx  # Predictable but different seeds
            else:
                current_seed = base_seed + ii * 100 + config_idx * 10  # More spread for time-based
            
            if DEBUG:
                print(f"Current seed: {current_seed} ({'FIXED' if USE_FIXED_SEEDS else 'TIME-BASED'})")
            
            try:
                # Create fitness function closure with predictor data
                def fitness_func(x):
                    return evaluateVolume(x, P_hull[:, 3:])
                
                # Start PSO with current configuration
                x_best, fval = particle_swarm_optimization(
                    fitness_func, num_points, 
                    lb=np.zeros(num_points), 
                    ub=np.full(num_points, N-1),
                    **config,
                    use_adaptive_params=True
                )
                
                # Get results with better handling
                if x_best is None:
                    if DEBUG:
                        print("PSO returned None result, skipping...")
                    continue
                    
                best_idx = np.unique(np.round(x_best).astype(int))
                
                # Apply local search improvement (hill climbing) - reduced iterations
                if DEBUG:
                    print("Applying local search refinement...")
                current_fitness = fval
                improved = True
                local_iterations = 0
                max_local_iterations = 300
                
                while improved and local_iterations < max_local_iterations:
                    improved = False
                    local_iterations += 1
                    
                    # Try swapping each selected point with unselected points
                    if len(best_idx) > 0:
                        unselected = list(set(range(N)) - set(best_idx))
                        
                        if len(unselected) > 0:
                            for i, selected_point in enumerate(best_idx):
                                # Try fewer random unselected points
                                n_candidates = min(4, len(unselected))  # Reduced from 3
                                if n_candidates > 0:
                                    candidates = np.random.choice(unselected, n_candidates, replace=False)
                                    
                                    for candidate in candidates:
                                        # Create new solution by swapping
                                        test_idx = best_idx.copy()
                                        test_idx[i] = candidate
                                        
                                        # Create position array for fitness evaluation
                                        test_pos = np.zeros(num_points)
                                        test_pos[:len(test_idx)] = test_idx
                                        
                                        test_fitness = fitness_func(test_pos)
                                        
                                        if test_fitness < current_fitness:
                                            best_idx[i] = candidate
                                            current_fitness = test_fitness
                                            improved = True
                                            
                                            # Update unselected list
                                            unselected.remove(candidate)
                                            unselected.append(selected_point)
                                            break
                    
                    if local_iterations % 5 == 0 and improved:  # Reduced frequency
                        if DEBUG:
                            print(f"Local search iteration {local_iterations}, fitness improved to {current_fitness:.6f}")
                
                if DEBUG:
                    print(f"Local search completed after {local_iterations} iterations")
                
                # Update final fitness value
                fval = current_fitness
                
                # Handle point count based on allow_fewer_points setting
                if DEBUG:
                    print(f"PSO found {len(best_idx)} unique indices (target: {num_points})")
                
                if len(best_idx) < num_points:
                    if allow_fewer_points:
                        if DEBUG:
                            print(f"✅ Accepting {len(best_idx)} points (allow_fewer_points=True)")
                        # Check if we have enough points for convex hull
                        min_points_needed = P_hull.shape[1] - 3 + 1  # predictor dimensions + 1
                        if len(best_idx) < min_points_needed:
                            if DEBUG:
                                print(f"❌ Error: {len(best_idx)} points insufficient for {P_hull.shape[1]-3}D convex hull (need {min_points_needed})")
                            continue  # Skip this attempt
                    else:
                        if DEBUG:
                            print(f"⚠️  Warning: Only {len(best_idx)} unique indices found, need {num_points}")
                            print(f"🔧 Padding with random additional indices (allow_fewer_points=False)")
                        # Pad with random additional indices if needed
                        remaining_indices = list(set(range(N)) - set(best_idx))
                        additional_needed = min(num_points - len(best_idx), len(remaining_indices))
                        if len(remaining_indices) > 0:
                            if USE_FIXED_SEEDS:
                                np.random.seed(current_seed + 1000)  # Reproducible padding
                            additional_indices = np.random.choice(remaining_indices, additional_needed, replace=False)
                            best_idx = np.concatenate([best_idx, additional_indices])
                            if DEBUG:
                                print(f"📊 Padded to {len(best_idx)} points")
                
                # Truncate if we have too many (only when padding was used)
                if len(best_idx) > num_points and not allow_fewer_points:
                    best_idx = best_idx[:num_points]
                    if DEBUG:
                        print(f"✂️  Truncated to {num_points} points")
                
                if DEBUG:
                    print(f"📊 Final selection: {len(best_idx)} indices")
                
                final_points = P_hull[best_idx]
                
                # Calculate volume and ratio
                final_hull = ConvexHull(final_points[:, 3:])
                V_final = final_hull.volume
                ratio = 100 * V_final / V_full
                if DEBUG:
                    print(f'Final Volume: {V_final:.6f} ({ratio:.3f}% of original Volume)')
                    print(f'Selected {len(best_idx)} points, PSO fitness: {fval:.6f}, Ratio: {ratio:.3f}%')
                
                if opt_ratio < ratio:
                    opt_best_idx = best_idx
                    opt_ratio = ratio
                    if DEBUG:
                        print(f'*** New best ratio: {ratio:.3f}% ***')
                    
                    # Aggressive early termination for speed based on goal ratio
                    inferred_target = goal_ratio - 10  # Since goal_ratio is typically target + 10
                    if fast_search_mode:
                        if inferred_target <= 50 and ratio >= inferred_target + 5:  # Low target: stop if exceeded by 5%
                            print(f"⚡ SPEED: Early termination for low target ({ratio:.1f}% >> {inferred_target}%)")
                            break
                        elif inferred_target <= 70 and ratio >= inferred_target + 10:  # Medium target: stop if exceeded by 10%
                            print(f"⚡ SPEED: Early termination for medium target ({ratio:.1f}% >> {inferred_target}%)")
                            break
                        elif ratio >= goal_ratio:  # High target: traditional early termination
                            print(f"Excellent result achieved ({ratio:.3f}%), terminating early")
                            break
                    else:
                        # Traditional early termination for full mode
                        if ratio >= goal_ratio:
                            print(f"Excellent result achieved ({ratio:.3f}%), terminating early")
                            break
                    
            except Exception as e:
                print(f"Error in run {run_count}: {e}")
                continue
        
        # Break outer loop too if excellent result found
        if opt_ratio >= goal_ratio:
            break
    
    if opt_best_idx is not None:
        opt_grid_cells = P_hull[opt_best_idx, :2]
        if DEBUG:
            print(f"\nOptimal solution found with {opt_ratio:.2f}% volume preservation")
            print(f"Selected {len(opt_best_idx)} grid cells")
        
        # Verify all selected cells are segment-covered
        selected_coords = set(tuple(cell) for cell in opt_grid_cells)
        verified_count = len(selected_coords & pm_coords)
        if DEBUG:
            print(f"✅ Verification: {verified_count}/{len(opt_best_idx)} selected cells are segment-covered")
        
        # Save optimal grid cells
        optimal_cells_path = os.path.join(transient_dir, f'optimal_grid_cells_{num_points}_filtered.json')
        
        # Prepare data for JSON output
        output_data = {}
        
        # Add execution summary if requested
        if include_summary and mode and start_time is not None:
            end_time = time.time()
            summary_data = create_summary_data(
                mode=mode,
                start_time=start_time,
                end_time=end_time,
                num_points=num_points,
                goal_ratio=goal_ratio,
                achieved_ratio=opt_ratio,
                use_fixed_seeds=use_fixed_seeds,
                debug_seed=debug_seed,
                allow_fewer_points=allow_fewer_points,
                predictor_filename=predictor_filename,
                route_filename=route_filename,
                pm_output_filename=pm_output_filename,
                working_directory=working_directory,
                **summary_kwargs
            )
            output_data.update(summary_data)
        
        # Add the optimal grid cells data
        output_data["optimal_grid_cells"] = opt_grid_cells.tolist()
        output_data["verification"] = {
            "total_selected": len(opt_best_idx),
            "segment_covered": verified_count,
            "all_covered": verified_count == len(opt_best_idx)
        }
        
        with open(optimal_cells_path, 'w') as f:
            json.dump(output_data, f, indent=2)
        if DEBUG:
            print(f"Saved optimal grid cells to {optimal_cells_path}")
            print(f"JSON includes: {'Summary + ' if include_summary else ''}Grid cells data + Verification")

        if return_ratio:
            return opt_grid_cells, opt_ratio
        else:
            return opt_grid_cells
    else:
        if DEBUG:
            print("No valid solution found")
        if return_ratio:
            return None, None
        else:
            return None


if __name__ == "__main__":
    # Default parameters - can be overridden when calling the function directly
    working_directory = 'work_dir/minimal_test'
    
    print("🔧 RUNNING MODE: single + FILTERING")
    print("📍 Executing: Single optimization mode with segment filtering")
    
    # Original single optimization
    num_points = 50
    goal_ratio = 100.0
    use_fixed_seeds = False  # Set to True for reproducible results, False for variation
    debug_seed = 42
    predictor_filename = 'predictors.txt'
    route_filename = 'initial_route.json'
    pm_output_filename = 'pm_output.json'
    allow_fewer_points = True  # Set to True to accept fewer points if PSO finds that optimal
    
    print(f"📝 Point handling: {'Allow fewer points' if allow_fewer_points else 'Pad to exact count'}")
    
    # Print initial summary (before execution)
    start_time = time.time()
    print_execution_summary(
        mode='single',
        start_time=start_time,
        end_time=start_time,  # Will be updated later
        num_points=num_points,
        goal_ratio=goal_ratio,
        achieved_ratio=None,  # Will be updated later
        use_fixed_seeds=use_fixed_seeds,
        debug_seed=debug_seed,
        working_directory=working_directory,
        predictor_filename=predictor_filename,
        route_filename=route_filename,
        pm_output_filename=pm_output_filename
    )
    
    # Start actual optimization
    result = hpe_optimization(
        working_directory=working_directory,
        num_points=num_points,
        goal_ratio=goal_ratio,
        use_fixed_seeds=use_fixed_seeds,
        debug_seed=debug_seed,
        predictor_filename=predictor_filename,
        route_filename=route_filename,
        pm_output_filename=pm_output_filename,
        return_ratio=True,  # Get both grid cells and achieved ratio
        allow_fewer_points=allow_fewer_points,
        include_summary=True,  # Include summary in JSON output
        mode='single',
        start_time=start_time
    )
    
    # End timing and print final summary
    end_time = time.time()
    
    # Extract achieved ratio from result
    achieved_ratio = None
    if result is not None:
        if isinstance(result, tuple) and len(result) == 2:
            grid_cells, achieved_ratio = result
        else:
            achieved_ratio = None  # Fallback if format unexpected
    
    print("\n" + "="*80)
    print("🏁 FINAL RESULTS SUMMARY")
    print("="*80)
    
    # Show detailed timing
    runtime = end_time - start_time
    start_readable = datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')
    end_readable = datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')
    
    print(f"🕐 Started: {start_readable}")
    print(f"🕐 Finished: {end_readable}")
    print(f"⏱️  Total Runtime: {runtime:.2f} seconds ({runtime/60:.2f} minutes)")
    if runtime >= 60:
        hours = runtime // 3600
        minutes = (runtime % 3600) // 60
        seconds = runtime % 60
        if hours > 0:
            print(f"⏱️  Detailed Time: {int(hours)}h {int(minutes)}m {seconds:.1f}s")
        else:
            print(f"⏱️  Detailed Time: {int(minutes)}m {seconds:.1f}s")
    
    print(f"📊 Points Tested: {num_points}")
    print(f"🎯 Target Ratio: {goal_ratio:.1f}%")
    if achieved_ratio is not None:
        print(f"📈 Achieved Ratio: {achieved_ratio:.1f}%")
        if achieved_ratio >= goal_ratio * 0.9:  # Within 90% of target
            print("✅ SUCCESS: Target achieved!")
        else:
            print("⚠️  PARTIAL: Below target ratio")
    else:
        print("❌ FAILED: No valid solution found")
    print("="*80)
    
    print("\n✨ Done!")
