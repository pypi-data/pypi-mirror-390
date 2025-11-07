from dataclasses import dataclass


@dataclass
class LeadFillets:
    """SMT Lead to Pad Fillet descriptor"""

    toe: float
    """ Toe Fillet size in mm
    """
    heel: float
    """ Heel Fillet size in mm
    """
    side: float
    """ Side Fillet size in mm
    """
    courtyard_excess: float
    """ Excess courtyard dimension around packages using this lead type in mm.
    """

    def __post_init__(self):
        assert self.courtyard_excess > 0
