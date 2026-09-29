"""
Food Processing Line Monitoring & Telemetry Inefficiency Detector
Tracks processing equipment telemetry (Steam cookers, Packaging machines,
Walk-in freezers, Peeling/Chopping lines) to compute OEE (Overall Equipment Effectiveness),
raw material losses, downtime, and excessive energy anomalies.
"""

from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class EquipmentTelemetry:
    machine_id: str
    machine_name: str
    machine_type: str        # 'Industrial Steamer', 'Cold Storage Unit', 'Automated Chopper', 'Packaging Conveyor'
    active_power_kw: float
    rated_power_kw: float
    temperature_c: float
    target_temperature_c: float
    throughput_units_per_hr: int
    target_throughput_per_hr: int
    scrap_reject_units: int
    total_processed_units: int
    running_state: str       # 'Running', 'Idle', 'Fault', 'Maintenance'
    uptime_minutes: int
    planned_minutes: int

@dataclass
class InefficiencyReport:
    machine_id: str
    machine_name: str
    oee_pct: float
    availability_pct: float
    performance_pct: float
    quality_pct: float
    energy_intensity_kwh_per_unit: float
    anomalies: List[str]
    potential_raw_material_loss_kg: float

class ProcessingTelemetryEngine:
    def analyze_equipment(self, telemetry: EquipmentTelemetry) -> InefficiencyReport:
        # Availability = Run Time / Planned Time
        availability = (telemetry.uptime_minutes / max(1, telemetry.planned_minutes)) * 100.0
        availability = min(100.0, availability)

        # Performance = Actual Output / (Target Output Rate * Run Time Hours)
        run_hours = telemetry.uptime_minutes / 60.0
        expected_output = telemetry.target_throughput_per_hr * run_hours
        performance = (telemetry.total_processed_units / max(1.0, expected_output)) * 100.0 if expected_output > 0 else 0.0
        performance = min(100.0, performance)

        # Quality = Good Units / Total Processed
        good_units = max(0, telemetry.total_processed_units - telemetry.scrap_reject_units)
        quality = (good_units / max(1, telemetry.total_processed_units)) * 100.0

        # OEE = Availability * Performance * Quality
        oee = (availability * performance * quality) / 10000.0

        # Energy Intensity
        energy_kwh = telemetry.active_power_kw * run_hours
        energy_intensity = energy_kwh / max(1, telemetry.total_processed_units)

        anomalies = []

        # Temperature drift anomaly
        temp_delta = abs(telemetry.temperature_c - telemetry.target_temperature_c)
        if temp_delta > 4.0:
            anomalies.append(f"Temperature deviation: {telemetry.temperature_c}°C vs setpoint {telemetry.target_temperature_c}°C (Risk of thermal spoilage)")

        # Power anomaly
        if telemetry.running_state == 'Idle' and telemetry.active_power_kw > (0.3 * telemetry.rated_power_kw):
            anomalies.append(f"Excessive idle power consumption: {telemetry.active_power_kw} kW while in idle state.")

        # Scrap rate anomaly (> 4%)
        scrap_rate = (telemetry.scrap_reject_units / max(1, telemetry.total_processed_units)) * 100
        if scrap_rate > 4.0:
            anomalies.append(f"High raw material scrap rate: {scrap_rate:.1f}% rejected at line inspection.")

        # Estimate raw material loss (assuming average unit weight 0.25 kg)
        material_loss_kg = round(telemetry.scrap_reject_units * 0.25, 2)

        return InefficiencyReport(
            machine_id=telemetry.machine_id,
            machine_name=telemetry.machine_name,
            oee_pct=round(oee, 1),
            availability_pct=round(availability, 1),
            performance_pct=round(performance, 1),
            quality_pct=round(quality, 1),
            energy_intensity_kwh_per_unit=round(energy_intensity, 4),
            anomalies=anomalies,
            potential_raw_material_loss_kg=material_loss_kg
        )

if __name__ == "__main__":
    engine = ProcessingTelemetryEngine()
    mock_machine = EquipmentTelemetry(
        machine_id="LINE-CHO-02",
        machine_name="High-Speed Vegetable Dicer & Prep Unit",
        machine_type="Automated Chopper",
        active_power_kw=14.2,
        rated_power_kw=15.0,
        temperature_c=14.5,
        target_temperature_c=10.0,
        throughput_units_per_hr=420,
        target_throughput_per_hr=500,
        scrap_reject_units=48,
        total_processed_units=850,
        running_state="Running",
        uptime_minutes=110,
        planned_minutes=120
    )
    report = engine.analyze_equipment(mock_machine)
    print(f"Machine: {report.machine_name}")
    print(f"Overall OEE: {report.oee_pct}% (Avail: {report.availability_pct}%, Perf: {report.performance_pct}%, Qual: {report.quality_pct}%)")
    print(f"Material Scrap Loss: {report.potential_raw_material_loss_kg} kg")
    print(f"Detected Anomalies: {report.anomalies}")
