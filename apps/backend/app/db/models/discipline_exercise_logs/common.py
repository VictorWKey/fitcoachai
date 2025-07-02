"""
Common enums for fitness discipline models.
"""

import enum

class WeightUnit(enum.Enum):
    """Weight units for strength exercises."""
    KG = "kg"
    LB = "lb"

class TempoPhase(enum.Enum):
    """Tempo phases for movement execution."""
    ECCENTRIC = "eccentric"
    PAUSE_BOTTOM = "pause_bottom"
    CONCENTRIC = "concentric"
    PAUSE_TOP = "pause_top"

class RangeOfMotion(enum.Enum):
    """Range of motion options."""
    FULL = "full"
    PARTIAL_TOP = "partial_top"
    PARTIAL_BOTTOM = "partial_bottom"
    QUARTER = "quarter"
    HALF = "half"

class SurfaceType(enum.Enum):
    """Surface types for balance exercises."""
    STABLE = "stable"
    BOSU = "bosu"
    SLACKLINE = "slackline"
    FOAM_PAD = "foam_pad"
    UNSTABLE = "unstable"

class StretchType(enum.Enum):
    """Types of stretching."""
    STATIC = "static"
    DYNAMIC = "dynamic"
    PNF = "pnf"
    BALLISTIC = "ballistic" 