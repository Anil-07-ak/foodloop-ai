"""
AI Quality Assessment & OpenCV Multi-Sensor Freshness Service
Integrates OpenCV image processing (Color thresholding, contour defect segmentation,
browning index, and Laplacian texture analysis) with IoT environmental telemetry
to quantify food decay and calculate remaining shelf life.
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Tuple
import datetime
import math

try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

@dataclass
class IoTSensorTelemetry:
    ambient_temp_c: float
    relative_humidity_pct: float
    ethylene_gas_ppm: float
    tvoc_gas_ppm: float
    storage_duration_hours: float

@dataclass
class VisionQualityInspection:
    item_category: str  # 'Fruits/Vegetables', 'Cooked Meal', 'Bakery', 'Dairy'
    visual_freshness_score: float  # 0.0 - 100.0
    detected_defects: List[str]    # e.g., ['Surface browning: 14%', 'Bruise contours: 3']
    color_degradation_index: float # 0.0 - 1.0
    defect_surface_area_pct: float # 0.0 - 100.0

@dataclass
class FreshnessAssessmentResult:
    composite_health_score: float  # 0 - 100
    grade: str                     # 'Grade A (Fresh)', 'Grade B (Fast-Track)', 'Grade C (Secondary Upcycle)', 'Grade D (Expired/Compost)'
    estimated_shelf_life_hours: float
    recommended_action: str
    safety_certification_passed: bool
    risk_factors: List[str]
    opencv_metrics: Dict[str, Any]

class OpenCVFreshnessAnalyzer:
    """
    OpenCV-based computer vision analyzer for produce & food freshness assessment.
    """
    @staticmethod
    def analyze_image_buffer(image_np_array) -> Dict[str, Any]:
        """
        Runs OpenCV pipeline:
        1. Color Space Conversion (BGR to HSV & Gray)
        2. Browning & Decay Mask Segmentation
        3. Contour Detection for Blemishes and Spoilage Spots
        4. Laplacian Surface Texture & Shriveling Analysis
        """
        if not OPENCV_AVAILABLE or image_np_array is None:
            # Fallback heuristic simulation when raw numpy array isn't passed
            return {
                "browning_area_pct": 3.4,
                "contour_defect_count": 2,
                "texture_shrivel_variance": 142.5,
                "freshness_index": 92.6,
                "opencv_status": "Simulated Heuristic (Install cv2 for live camera array)"
            }

        # 1. Convert to HSV color space for robust color segmentation
        hsv = cv2.cvtColor(image_np_array, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(image_np_array, cv2.COLOR_BGR2GRAY)

        # 2. Browning & Bruise Color Range in HSV (Hue: 10-30, Saturation: 50-200, Value: 30-160)
        lower_brown = np.array([10, 45, 30])
        upper_brown = np.array([30, 220, 165])
        brown_mask = cv2.inRange(hsv, lower_brown, upper_brown)

        # Calculate percentage of brown/decay pixels over foreground
        total_pixels = image_np_array.shape[0] * image_np_array.shape[1]
        decay_pixels = cv2.countNonZero(brown_mask)
        decay_ratio_pct = round((decay_pixels / max(1, total_pixels)) * 100.0, 2)

        # 3. Contour Detection for Defect Patches
        contours, _ = cv2.findContours(brown_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        significant_defects = [c for c in contours if cv2.contourArea(c) > 50]
        defect_count = len(significant_defects)

        # 4. Laplacian Variance (Surface Texture / Shriveling index)
        laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())

        # Freshness Score computation based on OpenCV metrics
        freshness_score = max(0.0, min(100.0, 100.0 - (decay_ratio_pct * 2.8) - (defect_count * 3.5)))

        return {
            "browning_area_pct": decay_ratio_pct,
            "contour_defect_count": defect_count,
            "texture_shrivel_variance": round(laplacian_var, 2),
            "freshness_index": round(freshness_score, 1),
            "opencv_status": "Active OpenCV Pipeline"
        }

        class FoodQualityAssessmentEngine:
    def __init__(self):
        self.cv_analyzer = OpenCVFreshnessAnalyzer()
        
    def evaluate_freshness(
        self, 
        telemetry: IoTSensorTelemetry, 
        vision: VisionQualityInspection,
        image_array=None
    ) -> FreshnessAssessmentResult:
        risk_factors = []
        
      # Run OpenCV analysis
        cv_metrics = self.cv_analyzer.analyze_image_buffer(image_array)
        effective_vision_score = vision.visual_freshness_score if image_array is None else cv_metrics["freshness_index"]

        # Sensor penalty calculations
        temp_penalty = 0.0
        if telemetry.ambient_temp_c > 12.0 and vision.item_category in ['Cooked Meal', 'Dairy']:
            temp_penalty = min(40.0, (telemetry.ambient_temp_c - 12.0) * 4.5)
            risk_factors.append(f"Temperature abuse detected: {telemetry.ambient_temp_c}°C (Threshold < 4-8°C)")
        elif telemetry.ambient_temp_c > 18.0:
            temp_penalty = min(25.0, (telemetry.ambient_temp_c - 18.0) * 2.0)
            risk_factors.append(f"High storage temperature: {telemetry.ambient_temp_c}°C")

        # Ethylene penalty for produce ripening/senescence
        ethylene_penalty = 0.0
        if telemetry.ethylene_gas_ppm > 2.5:
            ethylene_penalty = min(30.0, (telemetry.ethylene_gas_ppm - 2.5) * 8.0)
            risk_factors.append(f"High ethylene concentration: {telemetry.ethylene_gas_ppm} ppm")

        # TVOC penalty (microbial spoilage volatiles)
        tvoc_penalty = 0.0
        if telemetry.tvoc_gas_ppm > 1.2:
            tvoc_penalty = min(35.0, (telemetry.tvoc_gas_ppm - 1.2) * 15.0)
            risk_factors.append(f"Volatile organic compounds elevated: {telemetry.tvoc_gas_ppm} ppm (Microbial activity)")
        # Vision score component (60% weight) and Sensor score component (40% weight)

        sensor_score = max(0.0, 100.0 - (temp_penalty + ethylene_penalty + tvoc_penalty))
        composite_score = round(0.6 * effective_vision_score + 0.4 * sensor_score, 1)

        # Defect inspections
        if any("mold" in d.lower() for d in vision.detected_defects) or cv_metrics.get("browning_area_pct", 0) > 35:
            composite_score = min(composite_score, 20.0)
            risk_factors.append("Visible fungal spores or critical decay threshold detected by OpenCV.")

        # Determine grade and remaining shelf life
        if composite_score >= 85:
            grade = "Grade A (Prime / Kitchen Ready)"
            shelf_life_hours = max(24.0, 72.0 - telemetry.storage_duration_hours)
            action = "Retain for prime dining prep & standard cafeteria menu."
            safe = True
        elif composite_score >= 65:
            grade = "Grade B (Good / Fast-Track Donation)"
            shelf_life_hours = max(6.0, 18.0 - telemetry.storage_duration_hours * 0.5)
            action = "Dispatch immediately to nearest verified community shelter/NGO within 4-hour window."
            safe = True
        elif composite_score >= 40:
            grade = "Grade C (Secondary Upcycling / Processing)"
            shelf_life_hours = max(2.0, 6.0)
            action = "Route to centralized processing kitchen for soup base, puree, or dehydration."
            safe = True
        else:
            grade = "Grade D (Spoiled / Biomass Composting)"
            shelf_life_hours = 0.0
            action = "Reject from human consumption. Route to on-site aerobic composter / biogas digester."
            safe = False

        return FreshnessAssessmentResult(
            composite_health_score=composite_score,
            grade=grade,
            estimated_shelf_life_hours=round(shelf_life_hours, 1),
            recommended_action=action,
            safety_certification_passed=safe,
            risk_factors=risk_factors,
            opencv_metrics=cv_metrics
        )

if __name__ == "__main__":
    engine = FoodQualityAssessmentEngine()
    mock_sensor = IoTSensorTelemetry(
        ambient_temp_c=4.5,
        relative_humidity_pct=82.0,
        ethylene_gas_ppm=0.6,
        tvoc_gas_ppm=0.2,
        storage_duration_hours=12.0
    )
    mock_vision = VisionQualityInspection(
        item_category="Fruits/Vegetables",
        visual_freshness_score=91.0,
        detected_defects=["Minor superficial spot: 1.8%"],
        color_degradation_index=0.08,
        defect_surface_area_pct=1.8
    )
    result = engine.evaluate_freshness(mock_sensor, mock_vision)
    print("OpenCV & Multi-Sensor Freshness Assessment Result:")
    print(f"Health Score: {result.composite_health_score}/100")
    print(f"Grade: {result.grade}")
    print(f"Shelf Life: {result.estimated_shelf_life_hours} Hours")
    print(f"Recommended Action: {result.recommended_action}")
    print(f"OpenCV Metrics: {result.opencv_metrics}")
