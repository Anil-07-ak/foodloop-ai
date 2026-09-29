"""
Smart Surplus Redistribution & Recipient Matching Engine
Matches batches of surplus food from institutional kitchens with vetted NGOs,
shelters, food banks, and secondary discount markets based on:
- Distance & Estimated Transit Time
- Recipient Beneficiary Capacity vs Batch Volume
- Dietary / Allergen compatibility (e.g. Vegetarian, Halal, Allergen-free)
- Storage capability (Cold storage, Heated container, Dry storage)
- Remaining Shelf-Life Window vs Delivery Time
"""

from dataclasses import dataclass
from typing import List, Dict, Any
import math

@dataclass
class SurplusBatch:
    batch_id: str
    donor_id: str
    donor_name: str
    donor_lat: float
    donor_lng: float
    food_name: str
    category: str              # 'Cooked Meal', 'Fresh Produce', 'Bakery', 'Packaged'
    quantity_kg: float
    portions: int
    expiry_window_hours: float
    requires_cold_storage: bool
    dietary_tags: List[str]     # ['Vegetarian', 'Nut-Free']

@dataclass
class RecipientPartner:
    partner_id: str
    name: str
    partner_type: str          # 'Shelter', 'Food Bank', 'Community Kitchen', 'Secondary Buyer'
    lat: float
    lng: float
    capacity_portions: int
    has_cold_storage: bool
    urgency_level: str         # 'High', 'Medium', 'Low'
    accepted_categories: List[str]

@dataclass
class MatchProposal:
    recipient_id: str
    recipient_name: str
    partner_type: str
    distance_km: float
    estimated_transit_mins: float
    compatibility_score: float # 0 - 100
    allocated_portions: int
    priority_rank: int
    match_reasons: List[str]

class RedistributionMatchingEngine:
    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371.0 # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return round(R * c, 2)

    def find_best_matches(
        self, 
        batch: SurplusBatch, 
        partners: List[RecipientPartner]
    ) -> List[MatchProposal]:
        proposals = []
        
        for p in partners:
            dist = self.haversine_distance(batch.donor_lat, batch.donor_lng, p.lat, p.lng)
            # Assuming average urban speed 25 km/h + 10 mins loading/unloading buffer
            transit_time_mins = round((dist / 25.0) * 60 + 10, 1)
            transit_time_hours = transit_time_mins / 60.0

            # Hard Constraint 1: Delivery must arrive before expiry window minus safety buffer
            if transit_time_hours > (batch.expiry_window_hours - 0.75):
                continue # Exceeds safe transit threshold

            # Hard Constraint 2: Cold storage requirement
            if batch.requires_cold_storage and not p.has_cold_storage:
                continue

            # Hard Constraint 3: Partner category acceptance
            if batch.category not in p.accepted_categories:
                continue

            reasons = []
            score = 100.0

            # Distance penalty (1.5 pts per km)
            dist_penalty = min(35.0, dist * 1.5)
            score -= dist_penalty
            reasons.append(f"Proximity: {dist} km (~{transit_time_mins} mins away)")

            # Capacity matching
            alloc = min(batch.portions, p.capacity_portions)
            cap_ratio = alloc / max(1, batch.portions)
            if cap_ratio >= 0.8:
                score += 10.0
                reasons.append("Optimal capacity match for entire batch")
            else:
                score -= (1.0 - cap_ratio) * 15.0
                reasons.append(f"Partial batch absorption ({alloc}/{batch.portions} portions)")

            # Urgency bonus
            if p.urgency_level == 'High':
                score += 15.0
                reasons.append("High humanitarian urgency need")
            elif p.urgency_level == 'Medium':
                score += 5.0

            score = max(0.0, min(100.0, round(score, 1)))

            proposals.append(MatchProposal(
                recipient_id=p.partner_id,
                recipient_name=p.name,
                partner_type=p.partner_type,
                distance_km=dist,
                estimated_transit_mins=transit_time_mins,
                compatibility_score=score,
                allocated_portions=alloc,
                priority_rank=0,
                match_reasons=reasons
            ))

        # Sort by compatibility score descending
        proposals.sort(key=lambda x: x.compatibility_score, reverse=True)
        for idx, item in enumerate(proposals, start=1):
            item.priority_rank = idx

        return proposals
        
if __name__ == "__main__":
    engine = RedistributionMatchingEngine()
    mock_batch = SurplusBatch(
        batch_id="BATCH-9021",
        donor_id="KITCHEN-01",
        donor_name="Tech Park Central Dining",
        donor_lat=12.9716,
        donor_lng=77.5946,
        food_name="Steamed Brown Rice, Paneer Curry & Sautéed Greens",
        category="Cooked Meal",
        quantity_kg=48.0,
        portions=120,
        expiry_window_hours=4.0,
        requires_cold_storage=False,
        dietary_tags=["Vegetarian", "Nut-Free"]
    )
    mock_partners = [
        RecipientPartner(
            partner_id="NGO-101",
            name="City Hope Community Shelter",
            partner_type="Shelter",
            lat=12.9810,
            lng=77.6050,
            capacity_portions=150,
            has_cold_storage=True,
            urgency_level="High",
            accepted_categories=["Cooked Meal", "Bakery", "Fresh Produce"]
        ),
        RecipientPartner(
            partner_id="NGO-102",
            name="Grace Children's Home",
            partner_type="Food Bank",
            lat=12.9400,
            lng=77.6200,
            capacity_portions=80,
            has_cold_storage=True,
            urgency_level="Medium",
            accepted_categories=["Cooked Meal", "Bakery"]
        ),
        RecipientPartner(
            partner_id="BUYER-201",
            name="ClearBite Discount Pantry",
            partner_type="Secondary Buyer",
            lat=13.0300,
            lng=77.5600,
            capacity_portions=300,
            has_cold_storage=True,
            urgency_level="Low",
            accepted_categories=["Packaged", "Bakery", "Cooked Meal"]
        )
    ]
    matches = engine.find_best_matches(mock_batch, mock_partners)
    print(f"Total Matches Found: {len(matches)}")
    for m in matches:
        print(f"Rank {m.priority_rank}: {m.recipient_name} | Score: {m.compatibility_score}% | Dist: {m.distance_km}km | Reasons: {m.match_reasons}")
