from network.conversion import create_model
from network.generators_csv import (
    apply_generator_units_timeseries_csv,
    load_data_file_profiles_csv,
)
from network.outages import (
    apply_outage_schedule,
    build_outage_schedule,
    generate_stochastic_outages_csv,
    parse_explicit_outages_from_properties,
)
from network.ramp import fix_outage_ramp_conflicts
from network.slack import add_slack_generators
from network.storage_csv import add_storage_inflows_csv

# Constants
MODEL_ID = "sem-2024-2032"
SNAPSHOTS_PER_YEAR = 60
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
SEM_VRE_MAPPINGS = {
    "Wind NI -- All": "StochasticWindNI",
    "Wind ROI": "StochasticWindROI",
    "Wind Offshore": "StochasticWindOffshore",
    "Wind Offshore -- Arklow Phase 1": "StochasticWindROI",
    "Solar NI -- All": "StochasticSolarNI",
    "Solar ROI": "StochasticSolarROI",
}

xml_csv_dir = "src/examples/data/sem-2024-2032/csvs_from_xml/SEM Forecast model"
model_path = "src/examples/data/sem-2024-2032"

# Create the model
network, summary = create_model(MODEL_ID, use_csv=True)

# Load VRE profiles from CSVs, allowing curtailment (p_min_pu = 0)
vre_summary = load_data_file_profiles_csv(
    network=network,
    csv_dir=xml_csv_dir,
    profiles_path=model_path,
    property_name="Rating",
    target_property="p_max_pu",
    target_type="generators_t",
    apply_mode="replace",  # Allow curtailment: p_min_pu = 0, p_max_pu = profile
    scenario=1,  # No scenario filtering needed
    generator_filter=lambda gen: "Wind" in gen or "Solar" in gen,
    carrier_mapping={"Wind": "Wind", "Solar": "Solar"},
    value_scaling=0.01,
    manual_mappings=SEM_VRE_MAPPINGS,
)

# Add hydrological inflows to storage units
inflows_summary = add_storage_inflows_csv(
    network=network,
    csv_dir=xml_csv_dir,
    inflow_path=model_path,
)

# Apply generator Units time series (retirements, new builds, capacity scaling)
# IMPORTANT: Must be called AFTER VRE profiles are loaded
units_summary = apply_generator_units_timeseries_csv(
    network=network,
    csv_dir=xml_csv_dir,
    generator_filter=lambda gen: network.generators.at[gen, "ramp_limit_up"] >= 0.4,
)

# Get demand profile for intelligent maintenance scheduling
try:
    demand = network.loads_t.p_set.sum(axis=1)
    print(f"\nDemand profile: peak={demand.max():.1f} MW, min={demand.min():.1f} MW")
    has_demand = True
except Exception:
    print("\nNo demand profile available, maintenance will be scheduled uniformly")
    demand = None
    has_demand = False

# Get explicit outages from CSV
# Parse explicit outages from "Units Out" property
explicit_events = parse_explicit_outages_from_properties(
    csv_dir=xml_csv_dir,
    network=network,
    property_name="Units Out",
    generator_filter=lambda gen: network.generators.at[gen, "ramp_limit_up"] >= 0.4,
)


# Generate stochastic outages (uses Forced Outage Rate from Time varying properties)
# For AEMO: Filter out VRE generators by carrier (empty carrier = VRE)
stochastic_events = generate_stochastic_outages_csv(
    csv_dir=xml_csv_dir,
    network=network,
    include_forced=True,
    include_maintenance=True,
    demand_profile=demand if has_demand else None,
    random_seed=42,  # For reproducibility
    existing_outage_events=explicit_events,
    generator_filter=lambda gen: network.generators.at[gen, "carrier"] != ""
    and network.generators.at[gen, "ramp_limit_up"] >= 0.4,
)

# Build outage schedule
schedule = build_outage_schedule(explicit_events + stochastic_events, network.snapshots)
outage_summary = apply_outage_schedule(network, schedule)

# Fix any ramp rate conflicts caused by outages
fix_outage_ramp_conflicts(network)

# Add slack generators
add_slack_generators(network)


network.consistency_check()
network_subset = network.snapshots[network.snapshots.year == 2023]
res = network.optimize(**SOLVER_CONFIG)
network.model.print_infeasibilities()

network.consistency_check()


gen = "MP2"
p_max = network.generators_t.p_max_pu[gen].copy()
p_min = network.generators_t.p_min_pu[gen].copy()
ramp_rate = network.generators.at[gen, "ramp_limit_up"].copy()

p_min.reset_index().query("snapshot >= '2025-06-30 23:00:00'").head()
p_max.reset_index().query("snapshot >= '2025-06-30 23:00:00'").head()
p_min.reset_index().query("snapshot >= '2023-01-07 07:00:00'").head()
p_max.reset_index().query("snapshot >= '2023-01-07 07:00:00'").head()

# check for any p_min_pu > p_max_pu
merged_p = p_min.reset_index().merge(
    p_max.reset_index(), left_index=True, right_index=True, suffixes=("_min", "_max")
)
conflicts = merged_p[merged_p["Lisahally_min"] > merged_p["Lisahally_max"]]

fix_outage_ramp_conflicts(network)

post_min = network.generators_t.p_min_pu["Lisahally"].copy()
post_max = network.generators_t.p_max_pu["Lisahally"].copy()

post_min.reset_index().query("snapshot <= '2023-02-17 17:00:00'")
post_max.reset_index().query("snapshot <= '2023-02-17 17:00:00'").head()

# query for 5 hours before and after 2023-02-17 17:00:00
post_min.reset_index().query(
    "snapshot >= '2023-02-17 12:00:00' & snapshot <= '2023-02-17 22:00:00'"
)
post_max.reset_index().query(
    "snapshot >= '2023-02-17 12:00:00' & snapshot <= '2023-02-17 22:00:00'"
)

# check for outages
post_max.reset_index().query("Lisahally < 1 & Lisahally > 0")

outage_start = pd.Timestamp("2023-01-07 08:00:00")
initial_p_min = p_min.loc[outage_start - pd.Timedelta(hours=1)]
if initial_p_min > 0:
    ramp_down_hours = int(np.ceil(initial_p_min / ramp_rate))
    for h in range(ramp_down_hours):
        timestamp = outage_start - pd.Timedelta(hours=h)
        if timestamp in p_min.index:
            # p_min decreases at ramp rate, but not below 0
            p_min.loc[timestamp] = max(initial_p_min - h * ramp_rate, 0)


merged_post = post_min.reset_index().merge(
    post_max.reset_index(), left_index=True, right_index=True, suffixes=("_min", "_max")
)
conflicts_post = merged_post[
    merged_post["Lisahally_min"] > merged_post["Lisahally_max"]
]
