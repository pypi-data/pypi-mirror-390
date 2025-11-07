from dataclasses import dataclass

from ..ipc import DensityLevel
from .fillets import LeadFillets


@dataclass(frozen=True)
class LeadProtrusion:
    """Lead Protrusion Specification

    This class specifies the protrusion features for a specific SMT package
    style. See :py:mod:`jitxlib.landpatterns.leads.protrusions` for a set of
    predefined protrusion types.
    """

    name: str
    """Name for this protrusion type"""

    fillets: dict[DensityLevel, LeadFillets]
    """Lookup for the standard fillet sizes based on density level"""
