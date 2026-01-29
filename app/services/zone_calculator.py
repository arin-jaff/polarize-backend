"""
Heart rate and power zone calculation with 15+ methods.

All HR zone methods express boundaries as percentages of a threshold value (usually LTHR).
All power zone methods express boundaries as percentages of FTP (or CP/CTS test power).
"""

from app.schemas.zones import Zone, ZoneResult, ZoneMethodInfo

# ============================================================
# HEART RATE ZONE DEFINITIONS
# Format: (method_id, name, threshold_type, zones_list)
# Each zone: (zone_number, name, lower_pct, upper_pct)
# ============================================================

HR_METHODS: dict[str, dict] = {
    "joe_friel_run": {
        "name": "Joe Friel (Running)",
        "threshold_type": "LTHR",
        "zones": [
            (1, "Recovery", 0.00, 0.85),
            (2, "Extensive Endurance", 0.85, 0.89),
            (3, "Intensive Endurance", 0.90, 0.94),
            (4, "Sub-Threshold", 0.95, 0.99),
            (5, "Super-Threshold (5a)", 1.00, 1.02),
            (6, "Aerobic Capacity (5b)", 1.03, 1.06),
            (7, "Anaerobic Capacity (5c)", 1.06, 1.15),
        ],
    },
    "joe_friel_cycle": {
        "name": "Joe Friel (Cycling)",
        "threshold_type": "LTHR",
        "zones": [
            (1, "Recovery", 0.00, 0.81),
            (2, "Extensive Endurance", 0.81, 0.89),
            (3, "Intensive Endurance", 0.90, 0.93),
            (4, "Sub-Threshold", 0.94, 0.99),
            (5, "Super-Threshold (5a)", 1.00, 1.02),
            (6, "Aerobic Capacity (5b)", 1.03, 1.06),
            (7, "Anaerobic Capacity (5c)", 1.06, 1.15),
        ],
    },
    "andy_coggan_hr": {
        "name": "Andy Coggan",
        "threshold_type": "LTHR",
        "zones": [
            (1, "Active Recovery", 0.00, 0.68),
            (2, "Endurance", 0.69, 0.83),
            (3, "Tempo", 0.84, 0.94),
            (4, "Lactate Threshold", 0.95, 1.05),
            (5, "VO2max", 1.06, 1.15),
        ],
    },
    "usac": {
        "name": "USAC",
        "threshold_type": "LTHR",
        "zones": [
            (1, "Active Recovery", 0.40, 0.67),
            (2, "Endurance", 0.68, 0.82),
            (3, "Tempo", 0.83, 0.92),
            (4, "Threshold", 0.93, 1.02),
            (5, "VO2max / Anaerobic", 1.03, 1.15),
        ],
    },
    "usat_cycle": {
        "name": "USAT for Cycling",
        "threshold_type": "LTHR",
        "zones": [
            (1, "Recovery", 0.00, 0.85),
            (2, "Aerobic", 0.85, 0.89),
            (3, "Tempo", 0.90, 0.94),
            (4, "Sub-Threshold", 0.95, 0.99),
            (5, "Threshold", 1.00, 1.05),
            (6, "Above Threshold", 1.05, 1.15),
        ],
    },
    "usat_run": {
        "name": "USAT for Running",
        "threshold_type": "LTHR",
        "zones": [
            (1, "Recovery", 0.00, 0.85),
            (2, "Aerobic", 0.85, 0.89),
            (3, "Tempo", 0.90, 0.94),
            (4, "Sub-Threshold", 0.95, 0.99),
            (5, "Threshold", 1.00, 1.03),
            (6, "Above Threshold", 1.03, 1.15),
        ],
    },
    "cyclesmart": {
        "name": "CycleSmart",
        "threshold_type": "LTHR",
        "zones": [
            (1, "Recovery", 0.00, 0.75),
            (2, "Endurance", 0.75, 0.85),
            (3, "Tempo", 0.85, 0.92),
            (4, "Threshold", 0.92, 1.00),
            (5, "VO2max+", 1.00, 1.15),
        ],
    },
    "durata": {
        "name": "Durata Training",
        "threshold_type": "LTHR",
        "zones": [
            (1, "Recovery", 0.00, 0.72),
            (2, "Easy Endurance", 0.72, 0.78),
            (3, "Moderate Endurance", 0.78, 0.84),
            (4, "Tempo Low", 0.84, 0.88),
            (5, "Tempo High", 0.88, 0.92),
            (6, "Sub-Threshold", 0.92, 0.96),
            (7, "Threshold", 0.96, 1.00),
            (8, "Supra-Threshold", 1.00, 1.04),
            (9, "VO2max", 1.04, 1.08),
            (10, "Anaerobic", 1.08, 1.20),
        ],
    },
    "cts_cycle": {
        "name": "CTS Cycling",
        "threshold_type": "LTHR",
        "zones": [
            (1, "Easy / Recovery", 0.45, 0.73),
            (2, "Endurance", 0.73, 0.80),
            (3, "Tempo", 0.80, 0.85),
            (4, "Steady State", 0.86, 0.90),
            (5, "Climbing Repeat", 0.95, 0.97),
            (6, "Power Interval", 0.97, 1.10),
        ],
    },
    "cts_run": {
        "name": "CTS Run",
        "threshold_type": "LTHR",
        "zones": [
            (1, "Easy / Recovery", 0.00, 0.75),
            (2, "Endurance", 0.75, 0.84),
            (3, "Tempo", 0.84, 0.88),
            (4, "Steady State", 0.88, 0.95),
            (5, "Threshold+", 0.95, 1.10),
        ],
    },
    "8020_run": {
        "name": "80/20 Running",
        "threshold_type": "LTHR",
        "zones": [
            (1, "Low Aerobic", 0.75, 0.80),
            (2, "Moderate Aerobic", 0.81, 0.89),
            (3, "Transition (X)", 0.90, 0.95),
            (4, "Threshold", 0.96, 1.00),
            (5, "Supra-Threshold", 1.00, 1.02),
            (6, "VO2max", 1.02, 1.06),
            (7, "Speed / Anaerobic", 1.06, 1.15),
        ],
    },
    "8020_cycle": {
        "name": "80/20 Cycling",
        "threshold_type": "LTHR",
        "zones": [
            (1, "Low Aerobic", 0.00, 0.81),
            (2, "Moderate Aerobic", 0.81, 0.90),
            (3, "Transition (X)", 0.90, 0.95),
            (4, "Threshold", 0.95, 1.00),
            (5, "Supra-Threshold", 1.00, 1.02),
            (6, "VO2max", 1.03, 1.06),
            (7, "Anaerobic / Sprint", 1.06, 1.15),
        ],
    },
    "myprocoach_run": {
        "name": "MyProCoach Running",
        "threshold_type": "LTHR",
        "zones": [
            (1, "Recovery", 0.00, 0.80),
            (2, "Endurance", 0.80, 0.88),
            (3, "Tempo", 0.88, 0.94),
            (4, "Threshold", 0.94, 1.00),
            (5, "VO2max+", 1.00, 1.15),
        ],
    },
    "myprocoach_cycle": {
        "name": "MyProCoach Cycling",
        "threshold_type": "LTHR",
        "zones": [
            (1, "Recovery", 0.00, 0.78),
            (2, "Endurance", 0.78, 0.86),
            (3, "Tempo", 0.86, 0.93),
            (4, "Threshold", 0.93, 1.00),
            (5, "VO2max+", 1.00, 1.15),
        ],
    },
}

# ============================================================
# POWER ZONE DEFINITIONS
# ============================================================

POWER_METHODS: dict[str, dict] = {
    "andy_coggan": {
        "name": "Andy Coggan",
        "threshold_type": "FTP",
        "zones": [
            (1, "Active Recovery", 0.00, 0.55),
            (2, "Endurance", 0.56, 0.75),
            (3, "Tempo", 0.76, 0.90),
            (4, "Lactate Threshold", 0.91, 1.05),
            (5, "VO2max", 1.06, 1.20),
            (6, "Anaerobic Capacity", 1.21, 1.50),
        ],
    },
    "durata_power": {
        "name": "Durata Training",
        "threshold_type": "FTP",
        "zones": [
            (1, "Recovery", 0.00, 0.50),
            (2, "Easy Endurance", 0.50, 0.64),
            (3, "Moderate Endurance", 0.65, 0.75),
            (4, "Tempo", 0.76, 0.87),
            (5, "Sweet Spot", 0.88, 0.94),
            (6, "Threshold", 0.95, 1.05),
            (7, "VO2max", 1.06, 1.20),
            (8, "Anaerobic", 1.20, 2.00),
        ],
    },
    "cts_power": {
        "name": "CTS",
        "threshold_type": "FTP",
        "zones": [
            (1, "Easy / Recovery", 0.00, 0.45),
            (2, "Endurance Miles", 0.45, 0.73),
            (3, "Tempo", 0.80, 0.85),
            (4, "Steady State", 0.86, 0.90),
            (5, "Climbing Repeat", 0.95, 1.00),
            (6, "Power Interval", 1.00, 1.50),
        ],
    },
    "usat_cycle_power": {
        "name": "USAT for Cycling",
        "threshold_type": "FTP",
        "zones": [
            (1, "Recovery", 0.00, 0.55),
            (2, "Aerobic Endurance", 0.56, 0.75),
            (3, "Tempo", 0.76, 0.90),
            (4, "Sub-Threshold", 0.91, 1.00),
            (5, "Threshold / VO2max", 1.01, 1.15),
            (6, "Anaerobic", 1.15, 2.00),
        ],
    },
    "8020_run_power": {
        "name": "80/20 Running",
        "threshold_type": "rFTP",
        "zones": [
            (1, "Low Aerobic", 0.00, 0.80),
            (2, "Moderate Aerobic", 0.80, 0.88),
            (3, "Transition (X)", 0.88, 0.95),
            (4, "Threshold", 0.95, 1.00),
            (5, "Supra-Threshold", 1.00, 1.05),
            (6, "VO2max", 1.05, 1.15),
            (7, "Speed", 1.15, 1.50),
        ],
    },
    "8020_cycle_power": {
        "name": "80/20 Cycling",
        "threshold_type": "FTP",
        "zones": [
            (1, "Low Aerobic", 0.00, 0.55),
            (2, "Moderate Aerobic", 0.55, 0.75),
            (3, "Transition (X)", 0.75, 0.90),
            (4, "Threshold", 0.90, 1.00),
            (5, "Supra-Threshold", 1.00, 1.05),
            (6, "VO2max", 1.05, 1.20),
            (7, "Anaerobic", 1.20, 1.50),
        ],
    },
    "myprocoach_cycle_power": {
        "name": "MyProCoach Cycling",
        "threshold_type": "FTP",
        "zones": [
            (1, "Recovery", 0.00, 0.55),
            (2, "Endurance", 0.55, 0.75),
            (3, "Tempo", 0.76, 0.90),
            (4, "Threshold", 0.91, 1.05),
            (5, "VO2max+", 1.05, 1.50),
        ],
    },
    "myprocoach_run_power": {
        "name": "MyProCoach Running",
        "threshold_type": "rFTP",
        "zones": [
            (1, "Recovery", 0.00, 0.78),
            (2, "Endurance", 0.78, 0.88),
            (3, "Tempo", 0.88, 0.95),
            (4, "Threshold", 0.95, 1.05),
            (5, "VO2max+", 1.05, 1.50),
        ],
    },
    "stryd_run": {
        "name": "Stryd Running",
        "threshold_type": "CP",
        "zones": [
            (1, "Easy", 0.00, 0.80),
            (2, "Light", 0.80, 0.90),
            (3, "Moderate", 0.90, 1.00),
            (4, "Threshold", 1.00, 1.15),
            (5, "High Intensity", 1.15, 2.00),
        ],
    },
}


def calculate_hr_zones(
    method: str,
    activity: str = "running",
    threshold_hr: int | None = None,
    max_hr: int | None = None,
    resting_hr: int | None = None,
) -> ZoneResult:
    """Calculate heart rate zones for a given method."""
    # Resolve method key (handle generic names)
    method_key = _resolve_hr_method(method, activity)
    if method_key not in HR_METHODS:
        raise ValueError(f"Unknown HR zone method: {method}")

    method_def = HR_METHODS[method_key]

    if not threshold_hr:
        raise ValueError("Threshold heart rate (LTHR) is required")

    zones = []
    for zone_num, name, lower_pct, upper_pct in method_def["zones"]:
        zones.append(
            Zone(
                zone_number=zone_num,
                name=name,
                lower=round(threshold_hr * lower_pct),
                upper=round(threshold_hr * upper_pct),
            )
        )

    return ZoneResult(
        method=method_def["name"],
        activity=activity,
        threshold_type=method_def["threshold_type"],
        threshold_value=threshold_hr,
        zones=zones,
    )


def calculate_power_zones(
    method: str,
    activity: str = "cycling",
    threshold_power: int | None = None,
    running_threshold_power: int | None = None,
    critical_power: int | None = None,
) -> ZoneResult:
    """Calculate power zones for a given method."""
    if method not in POWER_METHODS:
        raise ValueError(f"Unknown power zone method: {method}")

    method_def = POWER_METHODS[method]

    # Determine which threshold to use
    threshold_type = method_def["threshold_type"]
    if threshold_type == "CP":
        threshold = critical_power
    elif threshold_type == "rFTP":
        threshold = running_threshold_power
    else:
        threshold = threshold_power

    if not threshold:
        raise ValueError(f"{threshold_type} is required for {method_def['name']}")

    zones = []
    for zone_num, name, lower_pct, upper_pct in method_def["zones"]:
        zones.append(
            Zone(
                zone_number=zone_num,
                name=name,
                lower=round(threshold * lower_pct),
                upper=round(threshold * upper_pct),
            )
        )

    return ZoneResult(
        method=method_def["name"],
        activity=activity,
        threshold_type=threshold_type,
        threshold_value=threshold,
        zones=zones,
    )


def get_available_hr_methods() -> list[ZoneMethodInfo]:
    """Return all available HR zone methods."""
    return [
        ZoneMethodInfo(
            method_id=key,
            name=m["name"],
            zone_count=len(m["zones"]),
            threshold_type=m["threshold_type"],
            supports=_hr_method_supports(key),
        )
        for key, m in HR_METHODS.items()
    ]


def get_available_power_methods() -> list[ZoneMethodInfo]:
    """Return all available power zone methods."""
    return [
        ZoneMethodInfo(
            method_id=key,
            name=m["name"],
            zone_count=len(m["zones"]),
            threshold_type=m["threshold_type"],
            supports=_power_method_supports(key),
        )
        for key, m in POWER_METHODS.items()
    ]


def _resolve_hr_method(method: str, activity: str) -> str:
    """Resolve a generic method name to a specific key based on activity."""
    if method in HR_METHODS:
        return method

    # Handle generic names like "joe_friel" -> "joe_friel_run" or "joe_friel_cycle"
    suffix = "_cycle" if activity == "cycling" else "_run"
    candidate = method + suffix
    if candidate in HR_METHODS:
        return candidate

    return method


def _hr_method_supports(key: str) -> list[str]:
    if "run" in key:
        return ["running"]
    if "cycle" in key:
        return ["cycling"]
    return ["running", "cycling", "rowing", "other"]


def _power_method_supports(key: str) -> list[str]:
    if "run" in key:
        return ["running"]
    if "cycle" in key:
        return ["cycling"]
    return ["cycling", "rowing", "other"]
