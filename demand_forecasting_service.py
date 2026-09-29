"""
Demand Forecasting & Surplus Prediction Service
Uses historical consumption time-series, headcount/booking data, calendar events,
weather index, and menu popularity to forecast required meal portions and surplus risks.
"""

from dataclasses import dataclass
from typing import List, Dict, Any
import datetime
import math

@dataclass
class DemandPredictionInput:
    date: str
    day_of_week: str
    target_headcount: int
    weather_condition: str  # e.g., 'Sunny', 'Rainy', 'Extreme Heat'
    temperature_c: float
    special_event: bool
    menu_category: str      # 'Main Course', 'Salad/Raw', 'Bakery', 'Dessert'
    historical_avg_consumption_per_person_kg: float

@dataclass
class DemandPredictionOutput:
    predicted_demand_kg: float
    recommended_prep_kg: float
    expected_surplus_risk_pct: float
    confidence_interval: tuple
    actionable_recommendations: List[str]

class AIDemandForecastingEngine:
    def __init__(self):
        # Weather impact elasticity multipliers
        self.weather_multipliers = {
            'Sunny': 1.02,
            'Mild': 1.00,
            'Rainy': 0.91,
            'Extreme Heat': 0.88,
            'Cold/Storm': 0.85
        }
        
        # Day of week attendance drift multipliers
        self.day_multipliers = {
            'Monday': 0.94,
            'Tuesday': 1.00,
            'Wednesday': 1.02,
            'Thursday': 0.98,
            'Friday': 0.82,  # Remote work / early leave trend
            'Saturday': 0.65,
            'Sunday': 0.60
        }

def predict_demand(self, inp: DemandPredictionInput) -> DemandPredictionOutput:
        base_demand = inp.target_headcount * inp.historical_avg_consumption_per_person_kg
        
        # Apply day and weather factor
        w_factor = self.weather_multipliers.get(inp.weather_condition, 1.0)
        d_factor = self.day_multipliers.get(inp.day_of_week, 1.0)
        e_factor = 1.15 if inp.special_event else 1.0
        
        adjusted_demand = base_demand * w_factor * d_factor * e_factor
        
        # Buffer recommendation (safety margin)
        # Main course needs less buffer (5%), perishable salads/bakery need tight control (2-3%)
                buffer_rates = {
            'Main Course': 0.05,
            'Salad/Raw': 0.03,
            'Bakery': 0.04,
            'Dessert': 0.03
        }
        buffer_rate = buffer_rates.get(inp.menu_category, 0.05)
        recommended_prep = adjusted_demand * (1.0 + buffer_rate)
        
        # Calculate overproduction surplus probability
        surplus_risk_pct = max(0.0, min(100.0, (1.0 - (adjusted_demand / (base_demand * 1.1 + 1e-5))) * 100))
        
        recommendations = []
        if inp.day_of_week == 'Friday' and w_factor < 0.95:
            recommendations.append("High likelihood of early departures and poor weather. Cut batch cook volume by 12%.")
        if inp.menu_category == 'Salad/Raw':
recommendations.append("Perishable category: Utilize Just-in-Time assembly in 2 separate shifts instead of single batch.")
        if surplus_risk_pct > 25.0:
            recommendations.append(f"High Surplus Alert ({surplus_risk_pct:.1f}% risk): Pre-alert partner NGOs for possible 3:00 PM batch pickup.")

        ci_low = round(adjusted_demand * 0.93, 2)
        ci_high = round(adjusted_demand * 1.07, 2)

        return DemandPredictionOutput(
            predicted_demand_kg=round(adjusted_demand, 2),
            recommended_prep_kg=round(recommended_prep, 2),
            expected_surplus_risk_pct=round(surplus_risk_pct, 1),
            confidence_interval=(ci_low, ci_high),
            actionable_recommendations=recommendations
        )

if __name__ == "__main__":
    engine = AIDemandForecastingEngine()
    sample_input = DemandPredictionInput(
        date="2026-09-28",
        day_of_week="Friday",
        target_headcount=1200,
        weather_condition="Rainy",
        temperature_c=19.5,
        special_event=False,
        menu_category="Main Course",
        historical_avg_consumption_per_person_kg=0.45
    )
    result = engine.predict_demand(sample_input)
    print("Demand Forecast Output:")
    print(f"Predicted Demand: {result.predicted_demand_kg} kg")
    print(f"Recommended Prep: {result.recommended_prep_kg} kg")
    print(f"Surplus Risk: {result.expected_surplus_risk_pct}%")
    print(f"Confidence Interval: {result.confidence_interval}")
    print(f"Recommendations: {result.actionable_recommendations}")
