"""CAISO IRP 2023 Stochastic Model - Manual conversion script.

This script demonstrates manual control over the CAISO IRP23 conversion process,
including scenario selection and outage modeling.
"""

from pathlib import Path

from network.conversion import create_model
from network.generators_csv import (
    apply_generator_units_timeseries_csv,
    load_data_file_profiles_csv,
)
from network.outages import apply_outage_schedule, load_outages_from_monthly_files
from network.slack import add_slack_generators
from network.storage_csv import add_storage_inflows_csv

# Configuration
MODEL_ID = "caiso-irp23"
SCENARIO = 1  # Stochastic scenario to use (1-500, for both load and outages)
OPTIMIZE_YEAR = 2024  # Year to optimize

SOLVER_CONFIG = {
    "solver_name": "gurobi",
    "solver_options": {
        "Threads": 6,
        "Method": 2,  # barrier
        "Crossover": 0,
        "BarConvTol": 1.0e-5,
        "Seed": 123,
        "AggFill": 0,
        "PreDual": 0,
        "GURO_PAR_BARDENSETHRESH": 200,
    },
}

# Paths
model_path = Path("src/examples/data/caiso-irp23")
xml_csv_dir = model_path / "csvs_from_xml" / "WECC"
units_out_dir = model_path / "Units Out"

# Create network
# - Auto-loads demand from LoadProfile/ (500 stochastic scenarios, Year/Month/Day/Period format)
# - Auto-loads fixed hydro dispatch from FixedDispatch/ via Rating.Data File (NP15_ROR, SP15_ROR)
# - VRE generators use static Rating/Rating Factor values from Time varying properties
# - Capacity expansions use time-varying Max Capacity at model start date
network, summary = create_model(
    MODEL_ID,
    use_csv=True,
    load_scenario=SCENARIO,  # Select which of 500 load scenarios to use
)

# Load Rating profiles (p_max_pu) for hydro dispatch
hydro_rating_summary = load_data_file_profiles_csv(
    network=network,
    csv_dir=xml_csv_dir,
    profiles_path=model_path,
    property_name="Rating",
    target_property="p_max_pu",
    target_type="generators_t",
    apply_mode="replace",
    scenario="Value",  # ← Hydro files use "Value" column, not scenario numbers
    generator_filter=lambda gen: "Hydro" in gen or "ROR" in gen,
    carrier_mapping={"Hydro": "hydro", "ROR": "hydro"},
)

# Load Min Stable Level profiles (p_min_pu) for must-run constraints
hydro_min_summary = load_data_file_profiles_csv(
    network=network,
    csv_dir=xml_csv_dir,
    profiles_path=model_path,
    property_name="Min Stable Level",
    target_property="p_min_pu",
    target_type="generators_t",
    apply_mode="replace",
    scenario="Value",  # ← Hydro files use "Value" column
    generator_filter=lambda gen: "Hydro" in gen or "ROR" in gen,
)

# Add hydrological inflows to storage units
inflows_summary = add_storage_inflows_csv(
    network=network,
    csv_dir=xml_csv_dir,
    inflow_path=model_path,
)

# Apply generator Units time series
# - Handles retirements, new builds, capacity scaling
# - Uses time-varying Max Capacity with dates (capacity expansions)
units_summary = apply_generator_units_timeseries_csv(network, xml_csv_dir)

# Load outages from monthly files (PRIMARY source)
# - Units Out/M01-M12/ directories contain pre-computed stochastic outages
# - 500 scenarios matching the 500 load scenarios
# - Format: Year/Month/Day/Period with 0=available, 1=on outage
# - Converted to capacity factors: 1.0=available, 0.0=fully on outage
outage_schedule = load_outages_from_monthly_files(
    units_out_dir=units_out_dir,
    network=network,
    scenario=SCENARIO,  # Match load scenario for consistency
)

# Apply outage schedule to network
# - Modifies p_max_pu (reduces available capacity during outages)
# - Modifies p_min_pu (maintains operational constraints during partial outages)
outage_summary = apply_outage_schedule(
    network,
    outage_schedule,
    ramp_aware=True,
)

# Add slack generators
slack_summary = add_slack_generators(network)

# Verify network consistency
network.consistency_check()

#  Optimize
optimize_snapshots = network.snapshots[network.snapshots.year == OPTIMIZE_YEAR]
network.optimize(snapshots=optimize_snapshots, **SOLVER_CONFIG)
