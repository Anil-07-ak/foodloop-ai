"""
Sustainability & ESG Analytics Engine
Calculates avoided greenhouse gas emissions (CO2 equivalent), virtual water footprint conserved,
landfill diversion rates, meals redistributed to vulnerable communities, and financial recovery value
according to standard GHG Protocol (Scope 3 Food Waste) and FAO/WRI Food Loss & Waste Protocol.
"""

from dataclasses import dataclass
from typing import Dict, List, Any

@dataclass
class WasteActivityLog:
    food_category: str        # 'Cooked Meal', 'Meat/Dairy', 'Produce/Vegetables', 'Grains/Bakery'
    quantity_kg: float
    disposition: str          # 'Redistributed to NGO', 'Upcycled in Kitchen', 'Composted', 'Landfill'

@dataclass
class ESGImpactReport:
    total_food_diverted_kg: float
    landfill_diversion_rate_pct: float
    co2e_emissions_avoided_kg: float
    water_footprint_saved_liters: float
    meals_served_equivalent: int
    economic_value_recovered_usd: float
    scope_3_emission_reduction_metric_tons: float
    esg_compliance_score: float # 0 - 100

class ESGAnalyticsCalculator:
    # Emission factor: kg CO2e avoided per kg food diverted from landfill (FAO / EPA WARM model)
    EMISSION_FACTORS = {
        'Cooked Meal': 2.85,
        'Meat/Dairy': 5.70,
        'Produce/Vegetables': 1.45,
        'Grains/Bakery': 2.10
    }

    # Virtual water footprint (liters of water required per kg food)
    WATER_FOOTPRINT_LITERS = {
        'Cooked Meal': 1850.0,
        'Meat/Dairy': 4200.0,
        'Produce/Vegetables': 380.0,
        'Grains/Bakery': 1200.0
    }

    # Average financial procurement value ($/kg)
    ECONOMIC_VALUE_PER_KG = {
        'Cooked Meal': 4.50,
        'Meat/Dairy': 7.80,
        'Produce/Vegetables': 2.20,
        'Grains/Bakery': 3.10
    }

    def compute_impact(self, logs: List[WasteActivityLog]) -> ESGImpactReport:
        total_kg = sum(l.quantity_kg for l in logs)
        diverted_kg = sum(l.quantity_kg for l in logs if l.disposition in ['Redistributed to NGO', 'Upcycled in Kitchen', 'Composted'])
        
        diversion_rate = (diverted_kg / max(0.001, total_kg)) * 100.0
        
        co2e_saved = 0.0
        water_saved = 0.0
        economic_val = 0.0
        redistributed_kg = 0.0

        for item in logs:
            if item.disposition != 'Landfill':
                co2_factor = self.EMISSION_FACTORS.get(item.food_category, 2.2)
                h2o_factor = self.WATER_FOOTPRINT_LITERS.get(item.food_category, 1000.0)
                val_factor = self.ECONOMIC_VALUE_PER_KG.get(item.food_category, 3.5)

                co2e_saved += item.quantity_kg * co2_factor
                water_saved += item.quantity_kg * h2o_factor
                economic_val += item.quantity_kg * val_factor

            if item.disposition == 'Redistributed to NGO':
                redistributed_kg += item.quantity_kg

        # Standard meal portion is 0.4 kg
        meals_equivalent = int(redistributed_kg / 0.4)
        scope3_tons = co2e_saved / 1000.0

        # ESG Composite Score (Weighted diversion rate, data integrity, social impact)
        esg_score = min(100.0, (diversion_rate * 0.7) + min(30.0, (meals_equivalent / 50.0) * 30.0))

        return ESGImpactReport(
            total_food_diverted_kg=round(diverted_kg, 2),
            landfill_diversion_rate_pct=round(diversion_rate, 1),
            co2e_emissions_avoided_kg=round(co2e_saved, 2),
            water_footprint_saved_liters=round(water_saved, 1),
            meals_served_equivalent=meals_equivalent,
            economic_value_recovered_usd=round(economic_val, 2),
            scope_3_emission_reduction_metric_tons=round(scope3_tons, 3),
            esg_compliance_score=round(esg_score, 1)
        )
        
if __name__ == "__main__":
    calculator = ESGAnalyticsCalculator()
    mock_logs = [
        WasteActivityLog("Cooked Meal", 180.0, "Redistributed to NGO"),
        WasteActivityLog("Produce/Vegetables", 65.0, "Upcycled in Kitchen"),
        WasteActivityLog("Grains/Bakery", 40.0, "Composted"),
        WasteActivityLog("Meat/Dairy", 12.0, "Landfill")
    ]
    report = calculator.compute_impact(mock_logs)
    print("ESG & Sustainability Impact Summary:")
    print(f"Total Diverted: {report.total_food_diverted_kg} kg ({report.landfill_diversion_rate_pct}% diversion rate)")
    print(f"GHG Avoided: {report.co2e_emissions_avoided_kg} kg CO2e ({report.scope_3_emission_reduction_metric_tons} MT Scope 3)")
    print(f"Water Conserved: {report.water_footprint_saved_liters} Liters")
    print(f"Meals Equivalent: {report.meals_served_equivalent} meals")
    print(f"Financial Recovery: ${report.economic_value_recovered_usd}")
    print(f"ESG Score: {report.esg_compliance_score}/100")
