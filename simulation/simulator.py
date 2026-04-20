import json
import copy
import os
from simulation.models import CityMetrics, PolicyInput

BASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "city_baseline.json")

def load_baseline() -> dict:
    with open(BASE_PATH, "r") as f:
        return json.load(f)

def extract_metrics(data: dict) -> CityMetrics:
    return CityMetrics(
        avg_congestion_percent=data["traffic"]["avg_congestion_percent"],
        public_transport_usage_percent=data["traffic"]["public_transport_usage_percent"],
        avg_commute_time_minutes=data["traffic"]["avg_commute_time_minutes"],
        renewable_percent=data["energy"]["renewable_percent"],
        co2_emissions_tons_per_day=data["pollution"]["co2_emissions_tons_per_day"],
        air_quality_index=data["pollution"]["air_quality_index"],
        avg_household_bill_usd=data["energy"]["avg_household_bill_usd"],
        unemployment_percent=data["economy"]["unemployment_percent"]
    )

def apply_policy(baseline_data: dict, policy: PolicyInput) -> CityMetrics:
    data = copy.deepcopy(baseline_data)
    p = policy.policy_type
    v = policy.change_value / 100

    if p == "reduce_bus_fare":
        data["traffic"]["public_transport_usage_percent"] += 22 * v
        data["traffic"]["avg_congestion_percent"] -= 15 * v
        data["traffic"]["avg_commute_time_minutes"] -= 8 * v
        data["pollution"]["co2_emissions_tons_per_day"] -= 600 * v
        data["pollution"]["air_quality_index"] -= 12 * v

    elif p == "increase_renewable_energy":
        data["energy"]["renewable_percent"] += 40 * v
        data["energy"]["fossil_fuel_percent"] -= 40 * v
        data["pollution"]["co2_emissions_tons_per_day"] -= 1800 * v
        data["pollution"]["air_quality_index"] -= 20 * v
        data["energy"]["avg_household_bill_usd"] += 10 * v

    elif p == "expand_green_spaces":
        data["pollution"]["air_quality_index"] -= 18 * v
        data["pollution"]["co2_emissions_tons_per_day"] -= 300 * v
        data["pollution"]["green_cover_percent"] += 15 * v

    elif p == "implement_congestion_tax":
        data["traffic"]["avg_congestion_percent"] -= 25 * v
        data["traffic"]["public_transport_usage_percent"] += 18 * v
        data["pollution"]["co2_emissions_tons_per_day"] -= 900 * v
        data["pollution"]["air_quality_index"] -= 16 * v

    elif p == "work_from_home_policy":
        data["traffic"]["avg_congestion_percent"] -= 30 * v
        data["traffic"]["avg_commute_time_minutes"] -= 15 * v
        data["pollution"]["co2_emissions_tons_per_day"] -= 700 * v
        data["economy"]["unemployment_percent"] -= 0.5 * v

    # Clamp to realistic ranges
    data["traffic"]["avg_congestion_percent"] = max(5, min(95, data["traffic"]["avg_congestion_percent"]))
    data["traffic"]["public_transport_usage_percent"] = max(5, min(90, data["traffic"]["public_transport_usage_percent"]))
    data["energy"]["renewable_percent"] = max(0, min(100, data["energy"]["renewable_percent"]))
    data["pollution"]["air_quality_index"] = max(10, data["pollution"]["air_quality_index"])
    data["pollution"]["co2_emissions_tons_per_day"] = max(500, data["pollution"]["co2_emissions_tons_per_day"])

    return extract_metrics(data)

def run_simulation(policy: PolicyInput):
    baseline_data = load_baseline()
    before = extract_metrics(baseline_data)
    after = apply_policy(baseline_data, policy)
    return before, after
