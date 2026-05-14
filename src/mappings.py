"""Central mapping definitions for the HKJC dataset.

Single source of truth — imported by notebooks instead of redefining the dicts
in each one. Update values here and every notebook picks them up.
"""

LOCATION_MAPPING = {
    "Happy Valley": 0,
    "Sha Tin": 1,
}

# All-Weather Track surface conditions
AWT_MAPPING = {
    "FAST": 0,
    "GOOD": 1,
    "WET SLOW": 2,
    "SLOW": 3,
    "WET FAST": 4,
    "SEALED": 5,
}

# Turf surface conditions
TURF_MAPPING = {
    "GOOD TO FIRM": 0,
    "GOOD": 1,
    "GOOD TO YIELDING": 2,
    "YIELDING": 3,
    "YIELDING TO SOFT": 4,
    "SOFT": 5,
    "HEAVY": 6,
}

# Race class hierarchy. Lower number = higher tier.
# Fractional offsets (e.g. 5.1, 6.3) keep variants ordered next to their parent class.
CLASS_MAPPING = {
    # Group races (highest tier)
    "Hong Kong Group One": 1.0,
    "Group One": 1.0,
    "Hong Kong Group Two": 2.0,
    "Group Two": 2.0,
    "Hong Kong Group Three": 3.0,
    "Group Three": 3.0,
    # Open class races
    "Class 1": 4.0,
    "Class 2": 5.0,
    "Class 2 (Bonus Prize Money)": 5.1,
    # Age / restricted races between Class 2 and 3
    "4 Year Olds": 5.3,
    "Restricted Race": 5.4,
    "Griffin Race": 5.5,
    # Class 3 variants
    "Class 3": 6.0,
    "Class 3 (Bonus Prize Money)": 6.1,
    "Class 3 (Special Condition)": 6.2,
    "Class 3 (Restricted)": 6.3,
    # Class 4 variants
    "Class 4": 7.0,
    "Class 4 (Special Condition)": 7.1,
    "Class 4 (Bonus Prize Money)": 7.2,
    "Class 4 (Restricted)": 7.3,
    # Lowest tier
    "Class 5": 8.0,
}

# Sentinel used when a race class is not in CLASS_MAPPING (weaker than Class 5).
UNKNOWN_CLASS_VALUE = 8.5
