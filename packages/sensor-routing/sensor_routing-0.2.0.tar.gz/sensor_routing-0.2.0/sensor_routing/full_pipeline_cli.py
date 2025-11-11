import argparse
import time
import json
import os
from annotated_types import T
import numpy as np
from pydantic import BaseModel, Field, ValidationError, ConfigDict

# =============================================================================
# GLOBAL DEBUG CONFIGURATION
# =============================================================================
# Set ENABLE_MODULE_DEBUG = True to enable debug prints in all modules
# You can still control individual modules by setting their DEBUG flags in their files
ENABLE_MODULE_DEBUG = False  # <-- MASTER DEBUG SWITCH FOR ALL MODULES

# Import modules first (as modules, not functions)
import point_mapping as point_mapping_module
import benefit_calculation as benefit_calculation_module
import path_finding as path_finding_module
import route_finding as route_finding_module
import hull_points_extraction as hull_points_extraction_module
import econ_mapping as econ_mapping_module
import econ_benefit as econ_benefit_module
import econ_paths as econ_paths_module
import econ_route as econ_route_module

# Apply global debug setting to all modules
if ENABLE_MODULE_DEBUG:
    point_mapping_module.DEBUG = True
    benefit_calculation_module.DEBUG = True
    path_finding_module.DEBUG = True
    route_finding_module.DEBUG = True
    hull_points_extraction_module.DEBUG = True
    econ_mapping_module.DEBUG = True
    econ_benefit_module.DEBUG = True
    econ_paths_module.DEBUG = True
    econ_route_module.DEBUG = True

# Now import the functions from the modules
from point_mapping import point_mapping
from benefit_calculation import benefit_calculation
from path_finding import path_finding
from route_finding import route_finding
from hull_points_extraction import hpe_optimization
from econ_mapping import point_mapping as econ_point_mapping
from econ_benefit import benefit_calculation as econ_benefit_calculation
from econ_paths import path_finding as econ_path_finding
from econ_route import route_finding as econ_route_finding

# Import modules with numeric prefixes using importlib
import importlib
import sys
import os

# Add current directory to path for relative imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Pydantic configuration model
class FullPipelineConfig(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    segment_number: int = Field(1, alias="sn", ge=1, le=10, description="Must be between 1 and 10")
    lower_benefit_limit: float = Field(0.1, alias="lbf", ge=0.0, le=1.0, description="Must be between 0.0 and 1.0")
    time_limit: int = Field(80, alias="tl", gt=0, description="Must be a positive number")
    optimization_objective: str = Field("d", alias="oo", pattern="^(d|t|i)$", description="Must be 'd' or 't'")
    max_aco_iteration: int = Field(50, alias="mai", gt=0, description="Must be a positive integer")
    ant_no: int = Field(500, alias="an", gt=0, description="Must be a positive integer")
    is_reversed: bool = Field(False, alias="ir", description="Must be true or false")
    working_directory: str = Field("work_dir", alias="wd", description="Working directory path")
    max_distance: int = Field(50, alias="md", gt=0, description="Must be a positive integer")
    benefit_type: str = Field("t", alias="bt", pattern="^(t|m)$", description="Must be 'total' or 'max'")
    route_type: str = Field("g", alias="rt", pattern="^(g|b)$", description="Must be 'good' or 'bad'")
    
    # HPE-specific parameters
    num_points: int = Field(50, alias="np", gt=0, description="Number of points for HPE optimization")
    goal_ratio: float = Field(100.0, alias="gr", gt=0, description="Goal ratio for HPE optimization")
    use_fixed_seeds: bool = Field(False, alias="ufs", description="Use fixed seeds for reproducible results")
    debug_seed: int = Field(42, alias="ds", gt=0, description="Debug seed value")
    allow_fewer_points: bool = Field(True, alias="afp", description="Allow fewer points than requested")

def load_or_create_parameters(working_dir="work_dir/test_pipeline", filename="parameters.json"):
    """Loads parameters from a JSON file in the specified working directory or creates it with default values."""
    # Ensure the working directory exists
    os.makedirs(working_dir, exist_ok=True)
    
    parameters_path = os.path.join(working_dir, filename)
    
    if ENABLE_MODULE_DEBUG:
        print(f"Checking if {parameters_path} exists...")

    if not os.path.exists(parameters_path):
        print("File not found, creating it with default values...")
        
        # Create default values dictionary directly
        default_config_dict = {
            "sn": 1,    # segment_number
            "lbf": 0.1, # lower_benefit_limit
            "tl": 80,   # time_limit
            "oo": "d",  # optimization_objective
            "mai": 50,  # max_aco_iteration
            "an": 500,  # ant_no
            "ir": False,    # is_reversed
            "wd": working_directory,    # working_directory
            "md": 50,   # max_distance
            "bt": "t",  # benefit_type
            "rt": "g",  # route_type
            "np": 50,   # num_points
            "gr": 100.0,    # goal_ratio
            "ufs": False,   # use_fixed_seeds
            "ds": 42,   # debug_seed
            "afp": True   # allow_fewer_points
        }
        
        if ENABLE_MODULE_DEBUG:
            print("Default config:", default_config_dict)

        # Write to the file
        try:
            with open(parameters_path, "w") as file:
                json.dump(default_config_dict, file, indent=4)
            print(f"Created default {parameters_path} with values")
        except Exception as e:
            print(f"Error writing to file: {e}")

        # Confirm file creation with a check
        if os.path.exists(parameters_path):
            print(f"File {parameters_path} successfully created!")
        else:
            print(f"Failed to create file at {parameters_path}")

    # Load the parameters from the file
    with open(parameters_path, "r") as file:
        params = json.load(file)
    if ENABLE_MODULE_DEBUG:
        print(f"Loaded parameters from {parameters_path}: {params}")

    return FullPipelineConfig(**params)

def parse_args():
    """Parses command-line arguments using argparse."""
    parser = argparse.ArgumentParser(description="Full sensor routing pipeline program")
    
    # Original parameters
    parser.add_argument("--sn", "-segment_number", type=int, help="how many segments will be visited per cluster")
    parser.add_argument("--lbf", "-lower_benefit_limit", type=float, help="lower benefit limit for the benefit calculation")
    parser.add_argument("--tl", "-time_limit", type=int, help="time limit for the agent")
    parser.add_argument("--oo", "-optimization_objective", type=str, help="optimization objective for the agent (d for distance, t for time)")
    parser.add_argument("--mai", "-max_aco_iteration", type=int, help="max ACO iteration for the agent")
    parser.add_argument("--an", "-ant_no", type=int, help="ant number for the agent")
    parser.add_argument("--ir", "-is_reversed", type=bool, help="is the road network reversed")
    parser.add_argument("--wd", "-working_directory", type=str, help="working directory")
    parser.add_argument("--bt", "-benefit_type", type=str, help="benefit type, t(total) or m(max)")
    parser.add_argument("--rt", "-route_type", type=str, help="route type, g(good) or b(bad)")
    
    # HPE-specific parameters
    parser.add_argument("--np", "-num_points", type=int, help="number of points for HPE optimization")
    parser.add_argument("--gr", "-goal_ratio", type=float, help="goal ratio for HPE optimization")
    parser.add_argument("--ufs", "-use_fixed_seeds", type=bool, help="use fixed seeds for reproducible results")
    parser.add_argument("--ds", "-debug_seed", type=int, help="debug seed value")
    parser.add_argument("--afp", "-allow_fewer_points", type=bool, help="allow fewer points than requested")
    
    args = parser.parse_args()
    
    return {k: v for k, v in vars(args).items() if v is not None}  # Remove None values

def get_final_config(manual_working_dir=None):
    """Combines JSON config and command-line arguments, with CLI taking priority."""
    cli_args = parse_args()
    
    # Priority: CLI args > manual override > default
    if "wd" in cli_args:
        working_dir = cli_args["wd"]  # Command-line argument takes highest priority
    elif manual_working_dir:
        working_dir = manual_working_dir  # Manual setting second
    else:
        working_dir = "work_dir/test_pipeline"  # Default fallback
        
    json_config = load_or_create_parameters(working_dir=working_dir)  # Load parameters from JSON or create them
    merged_params = json_config.model_dump(by_alias=True)  # Use model_dump() to get the parameters as a dictionary
    merged_params.update(cli_args)  # Update with command-line args
    
    try:
        return FullPipelineConfig(**merged_params)  # Validate final config
    except ValidationError as e:
        print("Configuration Validation Error:", e)
        exit(1)

def full_sensor_routing_pipeline(config):
    """
    Execute the full sensor routing pipeline with all 9 steps:
    1. Point Mapping (Initial) - creates pm_output.json + point_hull_collection.json
    2. Benefit Calculation (Initial) - creates bc_benefits_output.json, bc_top_benefits_output.json
    3. Path Finding (Initial) - creates pf_output.json
    4. Route Finding (Initial) - creates solution.json
    5. Hull Points Extraction - creates optimal_grid_cells_N_filtered.json
    6. Econ Point Mapping - creates econ_pm_output.json (uses optimal grid cells)
    7. Econ Benefit Calculation - creates econ_bc_benefits_output.json, econ_bc_top_benefits_output.json
    8. Econ Path Finding - creates econ_pf_output.json
    9. Econ Route Finding - creates econ_solution.json (FINAL OUTPUT)
    
    Note: Steps 6-9 use the "econ" (economical) versions that work with optimized points from hull extraction
    """
    if ENABLE_MODULE_DEBUG:
        print("🚀 Starting Full Sensor Routing Pipeline")
        print("=" * 80)
    
    pipeline_start_time = time.time()
    
    try:
        # Step 1: Point Mapping (Initial)
        if ENABLE_MODULE_DEBUG:
            print("\n📍 Step 1: Point Mapping (Initial)")
            print("-" * 40)
        step_start = time.time()
        
        total_number_of_classes = point_mapping(
            config.working_directory,
            config.max_distance,
            config.is_reversed
        )
        
        step_time = time.time() - step_start
        if ENABLE_MODULE_DEBUG:
            print(f"✅ Step 1 completed in {step_time:.2f} seconds")
            print(f"   Classes found: {total_number_of_classes}")
            print(f"   Outputs: transient/pm_output.json, point_hull_collection.json")
        
        # Step 2: Benefit Calculation (Initial)
        if ENABLE_MODULE_DEBUG:
            print("\n💰 Step 2: Benefit Calculation (Initial)")
            print("-" * 40)
        step_start = time.time()
        
        benefit_calculation(
            config.working_directory,
            config.lower_benefit_limit,
            total_number_of_classes,
            config.benefit_type,
            config.route_type
        )
        
        step_time = time.time() - step_start
        if ENABLE_MODULE_DEBUG:
            print(f"✅ Step 2 completed in {step_time:.2f} seconds")
            print(f"   Outputs: transient/bc_benefits_output.json, bc_top_benefits_output.json")
        
        # Step 3: Path Finding (Initial)
        if ENABLE_MODULE_DEBUG:
            print("\n🛤️  Step 3: Path Finding (Initial)")
            print("-" * 40)
        step_start = time.time()
        
        path_finding(
            config.working_directory,
            config.segment_number,
            total_number_of_classes,
            config.route_type,
            'i'
        )
        
        step_time = time.time() - step_start
        if ENABLE_MODULE_DEBUG:
            print(f"✅ Step 3 completed in {step_time:.2f} seconds")
            print(f"   Output: transient/pf_output.json")
        
        # Step 4: Route Finding (Initial)
        if ENABLE_MODULE_DEBUG:
            print("\n🗺️  Step 4: Route Finding (Initial)")
            print("-" * 40)
        step_start = time.time()
        
        route_finding(
            config.working_directory,
            total_number_of_classes,
            config.time_limit,
            config.optimization_objective,
            config.max_aco_iteration,
            config.ant_no,
            config.segment_number,
            config.benefit_type,
            config.route_type
        )
        
        step_time = time.time() - step_start
        if ENABLE_MODULE_DEBUG:
            print(f"✅ Step 4 completed in {step_time:.2f} seconds")
            print(f"   Output: transient/solution.json")
        
        # Step 5: Hull Points Extraction (HPE Optimization)
        if ENABLE_MODULE_DEBUG:
            print("\n🔷 Step 5: Hull Points Extraction")
            print("-" * 40)
            print(f"   Extracting optimal {config.num_points} points using PSO")
        step_start = time.time()
        
        hpe_result = hpe_optimization(
            working_directory=config.working_directory,
            num_points=config.num_points,
            goal_ratio=config.goal_ratio,
            use_fixed_seeds=config.use_fixed_seeds,
            debug_seed=config.debug_seed,
            predictor_filename='predictors.txt',
            route_filename='initial_route.json',
            pm_output_filename='pm_output.json',
            return_ratio=True,
            allow_fewer_points=config.allow_fewer_points,
            include_summary=True,
            mode='single',
            start_time=step_start
        )
        
        step_time = time.time() - step_start
        if hpe_result is not None:
            if isinstance(hpe_result, tuple):
                grid_cells, ratio = hpe_result
                if ENABLE_MODULE_DEBUG:
                    print(f"✅ Step 5 completed in {step_time:.2f} seconds")
                    print(f"   Achieved ratio: {ratio:.1f}%")
                    print(f"   Optimal points: {len(grid_cells) if grid_cells is not None else 0}")
                    print(f"   Output: transient/optimal_grid_cells_{config.num_points}_filtered.json")
            else:
                if ENABLE_MODULE_DEBUG:
                    print(f"✅ Step 5 completed in {step_time:.2f} seconds")
        else:
            if ENABLE_MODULE_DEBUG:
                print(f"⚠️  Step 5 completed in {step_time:.2f} seconds (no result)")
        
        # Step 6: Econ Point Mapping
        if ENABLE_MODULE_DEBUG:
            print("\n📍 Step 6: Econ Point Mapping")
            print("-" * 40)
            print("   Using optimized points from hull extraction")
        step_start = time.time()
        
        total_number_of_classes_econ = econ_point_mapping(
            config.working_directory,
            config.max_distance,
            config.is_reversed,
            use_optimal_grid_cells=True,
            num_clusters=total_number_of_classes
        )
        
        step_time = time.time() - step_start
        if ENABLE_MODULE_DEBUG:
            print(f"✅ Step 6 completed in {step_time:.2f} seconds")
            print(f"   Classes found: {total_number_of_classes_econ}")
            print(f"   Output: transient/econ_pm_output.json")
        
        # Step 7: Econ Benefit Calculation
        if ENABLE_MODULE_DEBUG:
            print("\n💰 Step 7: Econ Benefit Calculation")
            print("-" * 40)
        step_start = time.time()
        
        econ_benefit_calculation(
            config.working_directory,
            config.lower_benefit_limit,
            total_number_of_classes_econ,
            config.benefit_type,
            config.route_type
        )
        
        step_time = time.time() - step_start
        if ENABLE_MODULE_DEBUG:
            print(f"✅ Step 7 completed in {step_time:.2f} seconds")
            print(f"   Outputs: transient/econ_bc_benefits_output.json, econ_bc_top_benefits_output.json")
        
        # Step 8: Econ Path Finding
        if ENABLE_MODULE_DEBUG:
            print("\n🛤️  Step 8: Econ Path Finding")
            print("-" * 40)
        step_start = time.time()
        
        econ_path_finding(
            config.working_directory,
            config.segment_number,
            total_number_of_classes_econ,
            config.route_type,
            config.optimization_objective
        )
        
        step_time = time.time() - step_start
        if ENABLE_MODULE_DEBUG:
            print(f"✅ Step 8 completed in {step_time:.2f} seconds")
            print(f"   Output: transient/econ_pf_output.json")
        
        # Step 9: Econ Route Finding (FINAL STEP)
        if ENABLE_MODULE_DEBUG:
            print("\n🗺️  Step 9: Econ Route Finding (FINAL)")
            print("-" * 40)
        step_start = time.time()
        
        econ_route_finding(
            config.working_directory,
            total_number_of_classes_econ,
            config.time_limit,
            config.optimization_objective,
            config.max_aco_iteration,
            config.ant_no,
            config.segment_number,
            config.benefit_type,
            config.route_type
        )
        
        step_time = time.time() - step_start
        if ENABLE_MODULE_DEBUG:
            print(f"✅ Step 9 completed in {step_time:.2f} seconds")
            print(f"   Output: transient/econ_solution.json ⭐ FINAL RESULT")
        
    except Exception as e:
        print(f"❌ Pipeline failed at current step: {e}")
        if ENABLE_MODULE_DEBUG:
            import traceback
            traceback.print_exc()
        return False
    
    # Final summary
    total_time = time.time() - pipeline_start_time
    if ENABLE_MODULE_DEBUG:
        print("\n" + "=" * 80)
        print("🏁 FULL PIPELINE COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print(f"⏱️  Total Execution Time: {total_time:.2f} seconds ({total_time/60:.2f} minutes)")
        
        if total_time >= 3600:  # 1 hour
            hours = total_time // 3600
            minutes = (total_time % 3600) // 60
            seconds = total_time % 60
            print(f"⏱️  Detailed Time: {int(hours)}h {int(minutes)}m {seconds:.1f}s")
        elif total_time >= 60:
            minutes = total_time // 60
            seconds = total_time % 60
            print(f"⏱️  Detailed Time: {int(minutes)}m {seconds:.1f}s")
        
        print(f"📁 Working Directory: {config.working_directory}")
    if ENABLE_MODULE_DEBUG:
        print("✨ All 9 pipeline steps completed successfully!")
        print("\n📊 Pipeline Summary:")
        print(f"   1. Point Mapping → pm_output.json, point_hull_collection.json ({total_number_of_classes} classes)")
        print(f"   2. Benefit Calculation → bc_benefits_output.json, bc_top_benefits_output.json")
        print(f"   3. Path Finding → pf_output.json")
        print(f"   4. Route Finding → solution.json")
        print(f"   5. Hull Points Extraction → optimal_grid_cells_{config.num_points}_filtered.json")
        print(f"   6. Econ Point Mapping → econ_pm_output.json ({total_number_of_classes_econ} classes)")
        print(f"   7. Econ Benefit Calculation → econ_bc_benefits_output.json, econ_bc_top_benefits_output.json")
        print(f"   8. Econ Path Finding → econ_pf_output.json")
        print(f"   9. Econ Route Finding → econ_solution.json ⭐")
    
    return True

def main():
    """
    Main entry point for the sensor-routing command-line interface.
    This function is called when running 'sensor-routing' from the command line.
    """
    from datetime import datetime
    
    # Ensure we're running from the correct directory (repository root)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)  # Go up one level from sensor_routing/
    os.chdir(repo_root)
    
    # Start timestamp
    main_start_time = time.time()
    start_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    print(f"SENSOR ROUTING PIPELINE STARTED")
    print(f"Start Time: {start_timestamp}")
    
    if ENABLE_MODULE_DEBUG:
        print(f"📁 Working from: {os.getcwd()}")
        print("🔧 FULL SENSOR ROUTING PIPELINE")
        print("📊 Running all 9 steps in sequence")
        print("=" * 80)
        print("Pipeline Order:")
        print("1. Point Mapping (Initial)")
        print("2. Benefit Calculation (Initial)")
        print("3. Path Finding (Initial)")
        print("4. Route Finding (Initial)")
        print("5. Hull Points Extraction")
        print("6. Econ Point Mapping")
        print("7. Econ Benefit Calculation")
        print("8. Econ Path Finding")
        print("9. Econ Route Finding (FINAL)")
        print("=" * 80)
    
    config = get_final_config(manual_working_dir=None)
    
    # Now, `config` contains validated parameters and can be used in your program
    if ENABLE_MODULE_DEBUG:
        print("\n✅ Final Configuration Loaded:")
        print(config)
        print()
    
    # Run the full pipeline
    success = full_sensor_routing_pipeline(config)
    
    # End timestamp
    end_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    total_runtime = time.time() - main_start_time
    
    if success:
        print(f"\nPIPELINE COMPLETED SUCCESSFULLY")
        print(f"End Time: {end_timestamp}")
        print(f"Total Runtime: {total_runtime:.2f} seconds ({total_runtime/60:.2f} minutes)")
    else:
        print(f"\nPIPELINE FAILED")
        print(f"End Time: {end_timestamp}")
        print(f"Runtime before failure: {total_runtime:.2f} seconds")
        exit(1)

if __name__ == "__main__":
    from datetime import datetime
    
    # ============================================================================
    # MANUAL WORKING DIRECTORY SETUP (for "Run without debugging" in VS Code)
    # ============================================================================
    # Set this to override the default working directory when running directly
    # Example: MANUAL_WORKING_DIR = "work_dir/test_pipeline"
    # Set to None to use command-line arguments or default
    MANUAL_WORKING_DIR = "work_dir/test_pipeline"  # <-- CHANGE THIS
    # ============================================================================
    
    # Ensure we're running from the correct directory (repository root)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(script_dir)  # Go up one level from sensor_routing/
    os.chdir(repo_root)
    
    # Start timestamp
    main_start_time = time.time()
    start_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    print(f"SENSOR ROUTING PIPELINE STARTED")
    print(f"Start Time: {start_timestamp}")
    
    if ENABLE_MODULE_DEBUG:
        print(f"📁 Working from: {os.getcwd()}")
        if MANUAL_WORKING_DIR:
            print(f"📂 Manual working directory set to: {MANUAL_WORKING_DIR}")
        
        print("🔧 FULL SENSOR ROUTING PIPELINE")
        print("📊 Running all 9 steps in sequence")
        print("=" * 80)
        print("Pipeline Order:")
        print("1. Point Mapping (Initial)")
        print("2. Benefit Calculation (Initial)")
        print("3. Path Finding (Initial)")
        print("4. Route Finding (Initial)")
        print("5. Hull Points Extraction")
        print("6. Econ Point Mapping")
        print("7. Econ Benefit Calculation")
        print("8. Econ Path Finding")
        print("9. Econ Route Finding (FINAL)")
        print("=" * 80)
    
    config = get_final_config(manual_working_dir=MANUAL_WORKING_DIR)
    
    # Now, `config` contains validated parameters and can be used in your program
    if ENABLE_MODULE_DEBUG:
        print("\n✅ Final Configuration Loaded:")
        print(config)
        print()
    
    # Run the full pipeline
    success = full_sensor_routing_pipeline(config)
    
    # End timestamp
    end_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    total_runtime = time.time() - main_start_time
    
    if success:
        print(f"\nPIPELINE COMPLETED SUCCESSFULLY")
        print(f"End Time: {end_timestamp}")
        print(f"Total Runtime: {total_runtime:.2f} seconds ({total_runtime/60:.2f} minutes)")
    else:
        print(f"\nPIPELINE FAILED")
        print(f"End Time: {end_timestamp}")
        print(f"Runtime before failure: {total_runtime:.2f} seconds")
        exit(1)