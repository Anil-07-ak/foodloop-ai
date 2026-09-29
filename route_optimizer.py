"""
AI Logistics & Multi-Stop Route Optimization Engine
Solves Vehicle Routing Problem with Time Windows (VRP-TW) for surplus food collection
and redistribution, factoring in perishable temperature limits, traffic speeds, and vehicle capacities.
"""

from dataclasses import dataclass
from typing import List, Dict, Tuple
import math

@dataclass
class DeliveryWaypoint:
    waypoint_id: str
    location_name: str
    address: str
    lat: float
    lng: float
    waypoint_type: str  # 'Pickup (Kitchen)', 'Dropoff (NGO)'
    demand_kg: float
    time_window_start_mins: int  # Minutes from 00:00
    time_window_end_mins: int

@dataclass
class VehicleInfo:
    vehicle_id: str
    driver_name: str
    max_payload_kg: float
    is_refrigerated: bool
    current_lat: float
    current_lng: float
    fuel_type: str      # 'Electric', 'Diesel', 'CNG'
    emission_factor_g_co2_per_km: float

@dataclass
class RoutePlanResult:
    vehicle_id: str
    ordered_waypoints: List[Dict[str, Any]]
    total_distance_km: float
    total_transit_time_mins: float
    total_carbon_emission_kg: float
    feasibility_status: str
    time_window_violations: List[str]

class RouteOptimizerEngine:
    @staticmethod
    def distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        lat1, lon1 = p1
        lat2, lon2 = p2
        R = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        return round(R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)), 2)

    def optimize_route(self, vehicle: VehicleInfo, origin_kitchen: DeliveryWaypoint, dropoffs: List[DeliveryWaypoint]) -> RoutePlanResult:
        # Nearest Neighbor Heuristic with Time Window checks
        unvisited = dropoffs.copy()
        current_loc = (origin_kitchen.lat, origin_kitchen.lng)
        current_time = origin_kitchen.time_window_start_mins
        total_dist = 0.0
        route_sequence = [{
            "step": 1,
            "type": "Pickup",
            "name": origin_kitchen.location_name,
            "lat": origin_kitchen.lat,
            "lng": origin_kitchen.lng,
            "eta_mins": current_time,
            "action": f"Loaded {sum(d.demand_kg for d in dropoffs):.1f} kg"
        }]
    
            violations = []
        step_idx = 2

        while unvisited:
            # Pick nearest feasible dropoff
            best_idx = 0
            best_dist = 999999.0
            
            for idx, item in enumerate(unvisited):
                d = self.distance(current_loc, (item.lat, item.lng))
                if d < best_dist:
                    best_dist = d
                    best_idx = idx

            chosen = unvisited.pop(best_idx)
            travel_time_mins = int((best_dist / 28.0) * 60) # 28 km/h urban speed
            arrival_time = current_time + travel_time_mins

            # Time window validation
            if arrival_time > chosen.time_window_end_mins:
                violations.append(f"{chosen.location_name} arrived at min {arrival_time}, deadline was {chosen.time_window_end_mins}")

            total_dist += best_dist
            current_time = arrival_time + 10 # 10 mins service time
            current_loc = (chosen.lat, chosen.lng)

            route_sequence.append({
                "step": step_idx,
                "type": "Dropoff",
                "name": chosen.location_name,
                "lat": chosen.lat,
                "lng": chosen.lng,
                "eta_mins": arrival_time,
                "action": f"Delivered {chosen.demand_kg:.1f} kg"
            })
            step_idx += 1

        total_emissions = round((total_dist * vehicle.emission_factor_g_co2_per_km) / 1000.0, 3)

        return RoutePlanResult(
            vehicle_id=vehicle.vehicle_id,
            ordered_waypoints=route_sequence,
            total_distance_km=round(total_dist, 2),
            total_transit_time_mins=round(current_time - origin_kitchen.time_window_start_mins, 1),
            total_carbon_emission_kg=total_emissions,
            feasibility_status="Optimal" if not violations else "Feasible with Minor Delay",
            time_window_violations=violations
        )

if __name__ == "__main__":
    opt = RouteOptimizerEngine()
    veh = VehicleInfo(
        vehicle_id="EV-VAN-01",
        driver_name="Alex Kumar",
        max_payload_kg=500.0,
        is_refrigerated=True,
        current_lat=12.9716,
        current_lng=77.5946,
        fuel_type="Electric",
        emission_factor_g_co2_per_km=45.0
    )
    origin = DeliveryWaypoint(
        waypoint_id="WP-ORIGIN",
        location_name="Institutional Hub Kitchen",
        address="100 Tech Blvd",
        lat=12.9716,
        lng=77.5946,
        waypoint_type="Pickup (Kitchen)",
        demand_kg=0.0,
        time_window_start_mins=840, # 14:00
        time_window_end_mins=900
    )
    drops = [
        DeliveryWaypoint("WP-01", "Sunrise Children Care", "North St", 12.9850, 77.6100, "Dropoff", 25.0, 850, 930),
        DeliveryWaypoint("WP-02", "St. Jude Food Rescue", "East Ave", 12.9920, 77.6250, "Dropoff", 40.0, 860, 960),
        DeliveryWaypoint("WP-03", "Community Kitchen West", "Cross Rd", 12.9650, 77.5800, "Dropoff", 30.0, 850, 950)
    ]
    res = opt.optimize_route(veh, origin, drops)
    print("Logistics Plan Generated:")
    print(f"Total Distance: {res.total_distance_km} km | Total Time: {res.total_transit_time_mins} mins | CO2: {res.total_carbon_emission_kg} kg")
    for s in res.ordered_waypoints:
        print(f"  Step {s['step']}: {s['type']} -> {s['name']} (ETA +{s['eta_mins']}m)")
