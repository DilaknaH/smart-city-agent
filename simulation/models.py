from pydantic import BaseModel

class CityMetrics(BaseModel):
    avg_congestion_percent: float
    public_transport_usage_percent: float
    avg_commute_time_minutes: float
    renewable_percent: float
    co2_emissions_tons_per_day: float
    air_quality_index: float
    avg_household_bill_usd: float
    unemployment_percent: float

class PolicyInput(BaseModel):
    policy_type: str
    change_value: float
    description: str

class SimulationResult(BaseModel):
    policy: PolicyInput
    before: CityMetrics
    after: CityMetrics
    summary: str
    confidence: str