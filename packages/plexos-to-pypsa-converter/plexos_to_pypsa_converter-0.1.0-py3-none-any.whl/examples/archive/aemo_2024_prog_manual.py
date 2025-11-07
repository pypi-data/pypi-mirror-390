"""AEMO 2024 Progressive Change example (manual workflow).

This script demonstrates both chronological and investment-period setup paths.
Set ``USE_INVESTMENT_PERIODS`` below to switch between modes.
"""

import sys

from network.conversion import create_model
from network.generators_csv import (
    apply_generator_units_timeseries_csv,
    load_data_file_profiles_csv,
)
from network.investment import get_snapshot_timestamps
from network.outages import (
    apply_outage_schedule,
    build_outage_schedule,
    generate_stochastic_outages_csv,
)
from network.storage_csv import add_storage_inflows_csv

MODEL_ID = "aemo-2024-isp-progressive-change"
SOLVER_CONFIG = {
    "solver_name": "gurobi",
    "solver_options": {
        "Threads": 6,
        "Method": 2,
        "Crossover": 0,
        "BarConvTol": 1.0e-5,
        "Seed": 123,
        "AggFill": 0,
        "PreDual": 0,
        "GURO_PAR_BARDENSETHRESH": 200,
    },
}
XML_CSV_DIR = "src/examples/data/aemo-2024-isp-progressive-change/csvs_from_xml/NEM"
MODEL_PATH = "src/examples/data/aemo-2024-isp-progressive-change"

_INVESTMENT_PERIODS = [
    {"label": 2025, "start_year": 2024, "end_year": 2029},
    {"label": 2030, "start_year": 2030, "end_year": 2034},
    {"label": 2035, "start_year": 2035, "end_year": 2039},
    {"label": 2040, "start_year": 2040, "end_year": 2044},
    {"label": 2045, "start_year": 2045, "end_year": 2049},
    {"label": 2050, "start_year": 2050, "end_year": 2053},
]

# Toggle to switch between chronological and investment-period flows
USE_INVESTMENT_PERIODS = True
OPTIMIZATION_PERIOD = 2030


def run_investment_period_demo() -> None:
    """Mirror the automated workflow using investment periods."""
    network, setup_summary = create_model(
        MODEL_ID,
        use_csv=True,
        use_investment_periods=True,
        investment_periods=_INVESTMENT_PERIODS,
    )

    print("\nInvestment-period network summary:")
    print("  Loads:", len(network.loads))
    print("  Snapshots:", len(network.snapshots))
    print("  Snapshot mode:", setup_summary.get("snapshots_mode"))
    print("  Summary keys:", list(setup_summary.keys()))

    period_info = setup_summary.get("investment_periods", {})
    label_mapping = period_info.get("label_mapping", {})
    if period_info:
        print("\nPeriod weights (years):")
        for label, weight in period_info.get("period_weights", {}).items():
            label_name = label_mapping.get(label, str(label))
            print(f"  {label_name} (idx {label}): {weight:.3f}")
        print(
            "Total snapshot weight (years):",
            period_info.get("snapshot_weight_total_years"),
        )

    timestamp_level = get_snapshot_timestamps(network.snapshots)
    print("\nChronological span:")
    print(f"  Start: {timestamp_level[0]}  End: {timestamp_level[-1]}")
    print("  First 8 MultiIndex entries:")
    print(network.snapshots[:8])

    print("\nLoading VRE profiles...")
    load_data_file_profiles_csv(
        network=network,
        csv_dir=XML_CSV_DIR,
        profiles_path=MODEL_PATH,
        property_name="Rating",
        target_property="p_max_pu",
        target_type="generators_t",
        apply_mode="replace",
        scenario=1,
        generator_filter=None,
        carrier_mapping={"Wind": "wind", "Solar": "solar"},
        value_scaling=1.0,
    )

    print("Adding storage inflows...")
    inflow_summary = add_storage_inflows_csv(
        network=network,
        csv_dir=XML_CSV_DIR,
        inflow_path=MODEL_PATH,
        use_investment_periods=True,
    )
    print(
        f"  Storage units with inflows: {inflow_summary.get('storage_units_with_inflows', 0)}"
    )
    print(
        f"  Storage units without inflows: {inflow_summary.get('storage_units_without_inflows', 0)}"
    )

    print("Applying generator Units schedules...")
    units_summary = apply_generator_units_timeseries_csv(network, XML_CSV_DIR)
    print(
        f"  Generators with Units data: {units_summary.get('generators_with_units_data', 0)}"
    )

    print("Generating stochastic outages...")
    outage_events = generate_stochastic_outages_csv(
        csv_dir=XML_CSV_DIR,
        network=network,
        include_forced=True,
        include_maintenance=True,
        random_seed=42,
        existing_outage_events=None,
        generator_filter=lambda gen: network.generators.at[gen, "carrier"] != "",
    )
    outage_schedule = build_outage_schedule(outage_events, network.snapshots)
    apply_outage_schedule(network, outage_schedule)
    print(f"  Outage events generated: {len(outage_events)}")

    label_map = getattr(network, "investment_period_label_map", {})
    target_period = OPTIMIZATION_PERIOD
    if isinstance(OPTIMIZATION_PERIOD, str):
        for pid, label in label_map.items():
            if str(label) == OPTIMIZATION_PERIOD:
                target_period = int(pid)
                break
        else:
            try:
                target_period = int(OPTIMIZATION_PERIOD)
            except ValueError as exc:  # pragma: no cover - defensive path
                msg = (
                    f"OPTIMIZATION_PERIOD '{OPTIMIZATION_PERIOD}' not recognised. "
                    f"Available labels: {sorted(str(v) for v in label_map.values())}"
                )
                raise ValueError(msg) from exc
    mask = network.snapshots.get_level_values("period") == OPTIMIZATION_PERIOD
    period_snapshots = network.snapshots[mask]

    print(
        f"\nOptimising period {label_map.get(int(target_period), target_period)} "
        f"(idx {int(target_period)}) with {len(period_snapshots)} snapshots..."
    )
    network.consistency_check()
    network.optimize(
        snapshots=period_snapshots,
        **SOLVER_CONFIG,
    )
    network.model.print_infeasibilities()
    print("  Objective:", network.objective)


def run_chronological_workflow() -> None:
    """Run the original chronological example workflow end-to-end."""
    network_chron, summary_chron = create_model(MODEL_ID, use_csv=True)
    print("Chronological network summary:")
    print("  Loads:", len(network_chron.loads))
    print("  Generators:", len(network_chron.generators))
    print("  Snapshots:", len(network_chron.snapshots))
    print("  Snapshot mode:", summary_chron.get("snapshots_mode"))

    # Load VRE profiles from CSVs, allowing curtailment (p_min_pu = 0)
    load_data_file_profiles_csv(
        network=network_chron,
        csv_dir=XML_CSV_DIR,
        profiles_path=MODEL_PATH,
        property_name="Rating",
        target_property="p_max_pu",
        target_type="generators_t",
        apply_mode="replace",
        scenario=1,
        generator_filter=None,
        carrier_mapping={"Wind": "wind", "Solar": "solar"},
        value_scaling=1.0,
    )

    # Add hydrological inflows to storage units
    add_storage_inflows_csv(
        network=network_chron,
        csv_dir=XML_CSV_DIR,
        inflow_path=MODEL_PATH,
    )

    # Apply generator Units time series (retirements, new builds, capacity scaling)
    apply_generator_units_timeseries_csv(network_chron, XML_CSV_DIR)

    try:
        demand = network_chron.loads_t.p_set.sum(axis=1)
        print(
            f"\nDemand profile: peak={demand.max():.1f} MW, min={demand.min():.1f} MW"
        )
        has_demand = True
    except Exception:  # pragma: no cover - diagnostic path
        print("\nNo demand profile available; maintenance will be uniform")
        demand = None
        has_demand = False

    stochastic_events = generate_stochastic_outages_csv(
        csv_dir=XML_CSV_DIR,
        network=network_chron,
        include_forced=True,
        include_maintenance=True,
        demand_profile=demand if has_demand else None,
        random_seed=42,
        existing_outage_events=None,
        generator_filter=lambda gen: network_chron.generators.at[gen, "carrier"] != "",
    )

    schedule = build_outage_schedule(stochastic_events, network_chron.snapshots)
    apply_outage_schedule(network_chron, schedule)

    network_chron.consistency_check()

    target_year = 2025
    timestamps = get_snapshot_timestamps(network_chron.snapshots)
    snapshots = network_chron.snapshots[timestamps.year == target_year]
    print(
        f"Running optimisation for year {target_year} with {len(snapshots)} snapshots..."
    )
    network_chron.optimize(snapshots=snapshots, **SOLVER_CONFIG)


if __name__ == "__main__":
    if USE_INVESTMENT_PERIODS:
        run_investment_period_demo()
        sys.exit(0)

    run_chronological_workflow()
