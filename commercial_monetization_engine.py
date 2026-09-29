"""
Commercial Surplus Marketplace & Food Monetization Engine
Replaces non-profit charity with a for-profit multi-tier secondary food economy:
1. B2C Flash Consumer Marketplace (50-70% off retail meals)
2. B2B Wholesale Secondary Ingredients (Discounted bulk ingredients for ghost kitchens/caterers)
3. Industrial Bio-Feed & Upcycling Monetization (Animal feed & biogas feedstock)
4. Dynamic Pricing Engine & Platform Commission (18-25% Take-Rate)
"""

from dataclasses import dataclass
from typing import List, Dict, Any
import math

@dataclass
class CommercialSurplusListing:
    listing_id: str
    seller_id: str
    seller_name: str
    food_title: str
    category: str              # 'Cooked Meal Portion', 'Bulk Raw Produce', 'Bakery Crates', 'Organic Scrap Feedstock'
    quantity_kg: float
    units_available: int
    original_retail_unit_usd: float
    time_to_expiry_hours: float
    requires_cold_chain: bool

@dataclass
class CommercialBuyer:
    buyer_id: str
    buyer_name: str
    buyer_tier: str            # 'B2C Flash Consumer', 'B2B Cloud Kitchen', 'Discount Grocery Retailer', 'Bio-Feed Processor'
    max_budget_unit_usd: float
    distance_km: float
    target_volume_units: int
    payment_credit_rating: str  # 'AAA', 'AA', 'A'

@dataclass
class TransactionProposal:
    listing_id: str
    buyer_id: str
    buyer_name: str
    buyer_tier: str
    discounted_unit_price_usd: float
    gross_order_value_usd: float
    seller_payout_usd: float
    platform_take_rate_usd: float      # Platform 20% commission
    logistics_fee_usd: float
    projected_roi_pct: float
    clearance_speed_rating: str

class CommercialMonetizationEngine:
    def __init__(self, platform_commission_rate: float = 0.20):
        self.commission_rate = platform_commission_rate

    def calculate_dynamic_flash_price(self, listing: CommercialSurplusListing) -> float:
        """
        Dynamic pricing based on urgency decay curve:
        - > 6 hours: 45% discount
        - 3 - 6 hours: 60% discount
        - < 3 hours: 75% flash discount for instant liquidation
        """
        if listing.time_to_expiry_hours >= 6.0:
            discount_pct = 0.45
        elif listing.time_to_expiry_hours >= 3.0:
            discount_pct = 0.60
        else:
            discount_pct = 0.75

        discounted_price = listing.original_retail_unit_usd * (1.0 - discount_pct)
        return round(max(0.50, discounted_price), 2)

    def match_commercial_buyers(
        self, 
        listing: CommercialSurplusListing, 
        buyers: List[CommercialBuyer]
    ) -> List[TransactionProposal]:
        dynamic_price = self.calculate_dynamic_flash_price(listing)
        proposals = []

        for b in buyers:
            # Check budget feasibility
            if b.max_budget_unit_usd < dynamic_price:
                continue

            allocated_units = min(listing.units_available, b.target_volume_units)
            gross_value = round(allocated_units * dynamic_price, 2)
            
            # Platform Commission (20%)
            platform_fee = round(gross_value * self.commission_rate, 2)
            seller_net = round(gross_value - platform_fee, 2)

            # Cold chain logistics fee ($3.50 base + $0.85/km)
            logistics_fee = round(3.50 + (b.distance_km * 0.85), 2)

            # Clearance speed rating
            if b.distance_km < 4.0 and b.target_volume_units >= listing.units_available:
                speed = "Instant 15-Min Bulk Liquidation"
            elif b.distance_km < 10.0:
                speed = "Standard 45-Min Dispatch"
            else:
                speed = "Scheduled Regional Transport"

            proposals.append(TransactionProposal(
                listing_id=listing.listing_id,
                buyer_id=b.buyer_id,
                buyer_name=b.buyer_name,
                buyer_tier=b.buyer_tier,
                discounted_unit_price_usd=dynamic_price,
                gross_order_value_usd=gross_value,
                seller_payout_usd=seller_net,
                platform_take_rate_usd=platform_fee,
                logistics_fee_usd=logistics_fee,
                projected_roi_pct=round(((gross_value) / max(1.0, gross_value * 0.4)) * 100, 1),
                clearance_speed_rating=speed
            ))

        # Rank by Gross Value and clearance speed
        proposals.sort(key=lambda x: x.gross_order_value_usd, reverse=True)
        return proposals

if __name__ == "__main__":
    engine = CommercialMonetizationEngine()
    sample_listing = CommercialSurplusListing(
        listing_id="COM-9102",
        seller_id="KITCHEN-TECHPARK",
        seller_name="Metropolis Central Culinary Hub",
        food_title="Artisan Salmon Bowls & Truffle Quinoa",
        category="Cooked Meal Portion",
        quantity_kg=35.0,
        units_available=70,
        original_retail_unit_usd=14.50,
        time_to_expiry_hours=3.5,
        requires_cold_chain=True
    )
    sample_buyers = [
        CommercialBuyer("BUYER-B2C", "FoodLoop B2C Flash App Network", "B2C Flash Consumer", 6.50, 2.4, 70, "AAA"),
        CommercialBuyer("BUYER-CLOUDKITCHEN", "GhostKitchens Central Hub", "B2B Cloud Kitchen", 5.00, 4.8, 50, "AAA"),
        CommercialBuyer("BUYER-DISCOUNT", "Urban Outlet Discount Pantry", "Discount Grocery Retailer", 4.20, 8.5, 100, "AA")
    ]
    results = engine.match_commercial_buyers(sample_listing, sample_buyers)
    print("Commercial Liquidation Proposals:")
    for r in results:
        print(f"[{r.buyer_tier}] {r.buyer_name}: Unit Price: ${r.discounted_unit_price_usd} | Gross: ${r.gross_order_value_usd} | Platform Take (20%): ${r.platform_take_rate_usd} | Seller Net: ${r.seller_payout_usd}")
