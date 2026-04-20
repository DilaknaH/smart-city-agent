# agent/memory.py - replace entire file with this:
from typing import List, Dict

class SimulationMemory:
    def __init__(self):
        self.history: List[Dict] = []

    def add_simulation(self, policy_type: str, change_value: float,
                       before: dict, after: dict):
        entry = {
            "policy_type": policy_type,
            "change_value": change_value,
            "key_changes": {
                k: round(after[k] - before[k], 2)
                for k in before
            }
        }
        self.history.append(entry)

    def get_history_summary(self) -> str:
        if not self.history:
            return "No simulations have been run yet."
        summaries = []
        for i, sim in enumerate(self.history[-3:], 1):
            c = sim["key_changes"]
            summaries.append(
                f"Run {i}: {sim['policy_type']} at {sim['change_value']}% — "
                f"CO2: {c.get('co2_emissions_tons_per_day', 0):+.0f} tons/day, "
                f"Congestion: {c.get('avg_congestion_percent', 0):+.1f}%"
            )
        return "\n".join(summaries)

    def clear(self):
        self.history = []
        