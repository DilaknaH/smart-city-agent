import os
import json
from langchain.tools import tool
from simulation.simulator import run_simulation
from simulation.models import PolicyInput

BASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "city_baseline.json")

@tool
def simulate_policy(policy_json: str) -> str:
    """
    Simulate the impact of a city policy change.
    Input must be a JSON string with keys:
    - policy_type: one of [reduce_bus_fare, increase_renewable_energy,
                           expand_green_spaces, implement_congestion_tax,
                           work_from_home_policy]
    - change_value: number between 10 and 100 (percentage intensity)
    - description: short human-readable description
    Returns before/after metrics as JSON.
    """
    try:
        data = json.loads(policy_json)
        policy = PolicyInput(**data)
        before, after = run_simulation(policy)
        result = {
            "policy": data,
            "before": before.dict(),
            "after": after.dict(),
            "changes": {
                k: round(after.dict()[k] - before.dict()[k], 2)
                for k in before.dict()
            }
        }
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Simulation error: {str(e)}"

@tool
def get_city_status(query: str) -> str:
    """
    Get the current baseline status of the city.
    Use when the user asks about current city conditions or starting state.
    """
    with open(BASE_PATH, "r") as f:
        data = json.load(f)
    return json.dumps(data, indent=2)

@tool
def list_available_policies(query: str) -> str:
    """
    List all available policy types that can be simulated.
    Use when the user asks what options are available.
    """
    policies = {
        "reduce_bus_fare": "Reduce public bus fares to encourage transit use",
        "increase_renewable_energy": "Increase the share of renewable energy sources",
        "expand_green_spaces": "Increase parks and green cover across the city",
        "implement_congestion_tax": "Tax private vehicles entering city center",
        "work_from_home_policy": "Implement mandatory work-from-home days"
    }
    return json.dumps(policies, indent=2)

@tool
def compare_policies(policies_json: str) -> str:
    """
    Compare two policies side by side.
    Input: JSON string with 'policy1' and 'policy2' keys,
    each containing policy_type, change_value, description.
    """
    try:
        data = json.loads(policies_json)
        results = {}
        for name in ["policy1", "policy2"]:
            p = PolicyInput(**data[name])
            before, after = run_simulation(p)
            results[name] = {
                "policy_type": data[name]["policy_type"],
                "changes": {
                    k: round(after.dict()[k] - before.dict()[k], 2)
                    for k in before.dict()
                }
            }
        return json.dumps(results, indent=2)
    except Exception as e:
        return f"Comparison error: {str(e)}"
    