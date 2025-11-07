# Auto-Generated File

from ..ipc import DensityLevel
from .fillets import LeadFillets
from .protrusion import LeadProtrusion

SmallFlatRibbonLLeads = LeadProtrusion(
    "SmallFlatRibbonLLeads",
    {
        DensityLevel.A: LeadFillets(0.55, 0.45, 0.01, 0.5),
        DensityLevel.B: LeadFillets(0.35, 0.35, -0.02, 0.25),
        DensityLevel.C: LeadFillets(0.15, 0.25, -0.04, 0.1),
    },
)
BigFlatRibbonLLeads = LeadProtrusion(
    "BigFlatRibbonLLeads",
    {
        DensityLevel.A: LeadFillets(0.55, 0.45, 0.05, 0.5),
        DensityLevel.B: LeadFillets(0.35, 0.35, 0.03, 0.25),
        DensityLevel.C: LeadFillets(0.15, 0.25, 0.01, 0.1),
    },
)
SmallGullWingLeads = LeadProtrusion(
    "SmallGullWingLeads",
    {
        DensityLevel.A: LeadFillets(0.55, 0.45, 0.01, 0.5),
        DensityLevel.B: LeadFillets(0.35, 0.35, -0.02, 0.25),
        DensityLevel.C: LeadFillets(0.15, 0.25, -0.04, 0.1),
    },
)
BigGullWingLeads = LeadProtrusion(
    "BigGullWingLeads",
    {
        DensityLevel.A: LeadFillets(0.55, 0.45, 0.05, 0.5),
        DensityLevel.B: LeadFillets(0.35, 0.35, 0.03, 0.25),
        DensityLevel.C: LeadFillets(0.15, 0.25, 0.01, 0.1),
    },
)
JLeads = LeadProtrusion(
    "JLeads",
    {
        DensityLevel.A: LeadFillets(0.55, 0.1, 0.05, 0.5),
        DensityLevel.B: LeadFillets(0.35, 0.0, 0.03, 0.25),
        DensityLevel.C: LeadFillets(0.15, -0.1, 0.01, 0.1),
    },
)
BigRectangularLeads = LeadProtrusion(
    "BigRectangularLeads",
    {
        DensityLevel.A: LeadFillets(0.55, 0.0, 0.05, 0.5),
        DensityLevel.B: LeadFillets(0.35, 0.0, 0.0, 0.25),
        DensityLevel.C: LeadFillets(0.15, 0.0, -0.05, 0.1),
    },
)
SmallRectangularLeads = LeadProtrusion(
    "SmallRectangularLeads",
    {
        DensityLevel.A: LeadFillets(0.3, 0.0, 0.05, 0.2),
        DensityLevel.B: LeadFillets(0.2, 0.0, 0.0, 0.15),
        DensityLevel.C: LeadFillets(0.1, 0.0, -0.05, 0.1),
    },
)
LeadlessConcaveCastellated = LeadProtrusion(
    "LeadlessConcaveCastellated",
    {
        DensityLevel.A: LeadFillets(0.25, 0.65, 0.05, 0.5),
        DensityLevel.B: LeadFillets(0.15, 0.45, 0.0, 0.25),
        DensityLevel.C: LeadFillets(0.05, 0.45, 0.0, 0.1),
    },
)
CylindricalLeads = LeadProtrusion(
    "CylindricalLeads",
    {
        DensityLevel.A: LeadFillets(0.6, 0.2, 0.1, 0.5),
        DensityLevel.B: LeadFillets(0.4, 0.1, 0.05, 0.25),
        DensityLevel.C: LeadFillets(0.2, 0.02, 0.01, 0.1),
    },
)
LeadlessChipCarrierLeads = LeadProtrusion(
    "LeadlessChipCarrierLeads",
    {
        DensityLevel.A: LeadFillets(0.65, 0.25, 0.05, 0.5),
        DensityLevel.B: LeadFillets(0.55, 0.15, -0.05, 0.25),
        DensityLevel.C: LeadFillets(0.45, 0.05, -0.15, 0.1),
    },
)
ConcaveChipArrayLeads = LeadProtrusion(
    "ConcaveChipArrayLeads",
    {
        DensityLevel.A: LeadFillets(0.55, -0.05, -0.05, 0.5),
        DensityLevel.B: LeadFillets(0.45, -0.07, -0.07, 0.25),
        DensityLevel.C: LeadFillets(0.35, -0.2, -0.1, 0.1),
    },
)
ConvexChipArrayLeads = LeadProtrusion(
    "ConvexChipArrayLeads",
    {
        DensityLevel.A: LeadFillets(0.55, -0.05, -0.05, 0.5),
        DensityLevel.B: LeadFillets(0.45, -0.07, -0.07, 0.25),
        DensityLevel.C: LeadFillets(0.35, -0.2, -0.1, 0.1),
    },
)
FlatChipArrayLeads = LeadProtrusion(
    "FlatChipArrayLeads",
    {
        DensityLevel.A: LeadFillets(0.55, -0.05, -0.05, 0.5),
        DensityLevel.B: LeadFillets(0.45, -0.07, -0.07, 0.25),
        DensityLevel.C: LeadFillets(0.35, -0.2, -0.1, 0.1),
    },
)
ButtJointLeads = LeadProtrusion(
    "ButtJointLeads",
    {
        DensityLevel.A: LeadFillets(1.0, 1.0, 0.3, 1.5),
        DensityLevel.B: LeadFillets(0.8, 0.8, 0.2, 0.8),
        DensityLevel.C: LeadFillets(0.6, 0.6, 0.1, 0.2),
    },
)
InwardFlatRibbonLLeads = LeadProtrusion(
    "InwardFlatRibbonLLeads",
    {
        DensityLevel.A: LeadFillets(0.25, 0.8, 0.01, 0.5),
        DensityLevel.B: LeadFillets(0.15, 0.5, -0.05, 0.25),
        DensityLevel.C: LeadFillets(0.07, 0.2, -0.1, 0.1),
    },
)
FlatLugLeads = LeadProtrusion(
    "FlatLugLeads",
    {
        DensityLevel.A: LeadFillets(0.55, 0.45, 0.05, 0.5),
        DensityLevel.B: LeadFillets(0.35, 0.35, 0.03, 0.25),
        DensityLevel.C: LeadFillets(0.15, 0.25, 0.01, 0.1),
    },
)
QuadFlatNoLeads = LeadProtrusion(
    "QuadFlatNoLeads",
    {
        DensityLevel.A: LeadFillets(0.4, 0.0, -0.04, 0.5),
        DensityLevel.B: LeadFillets(0.3, 0.0, -0.04, 0.25),
        DensityLevel.C: LeadFillets(0.2, 0.0, -0.04, 0.1),
    },
)
SmallOutlineNoLeads = LeadProtrusion(
    "SmallOutlineNoLeads",
    {
        DensityLevel.A: LeadFillets(0.3, 0.0, 0.05, 0.2),
        DensityLevel.B: LeadFillets(0.2, 0.0, 0.0, 0.15),
        DensityLevel.C: LeadFillets(0.1, 0.0, -0.05, 0.1),
    },
)
SmallOutlineFlatLeads = LeadProtrusion(
    "SmallOutlineFlatLeads",
    {
        DensityLevel.A: LeadFillets(0.3, 0.0, 0.05, 0.2),
        DensityLevel.B: LeadFillets(0.2, 0.0, 0.0, 0.15),
        DensityLevel.C: LeadFillets(0.1, 0.0, -0.05, 0.1),
    },
)
ShortTwoPinCrystalLeads = LeadProtrusion(
    "ShortTwoPinCrystalLeads",
    {
        DensityLevel.A: LeadFillets(0.7, 0.0, 0.5, 1.0),
        DensityLevel.B: LeadFillets(0.5, -0.1, 0.4, 0.5),
        DensityLevel.C: LeadFillets(0.3, -0.2, 0.3, 0.25),
    },
)
ShortAluminumElectrolyticLeads = LeadProtrusion(
    "ShortAluminumElectrolyticLeads",
    {
        DensityLevel.A: LeadFillets(0.7, 0.0, 0.5, 1.0),
        DensityLevel.B: LeadFillets(0.5, -0.1, 0.4, 0.5),
        DensityLevel.C: LeadFillets(0.3, -0.2, 0.3, 0.25),
    },
)
TallTwoPinCrystalLeads = LeadProtrusion(
    "TallTwoPinCrystalLeads",
    {
        DensityLevel.A: LeadFillets(1.0, 0.0, 0.6, 1.0),
        DensityLevel.B: LeadFillets(0.7, -0.05, 0.5, 0.5),
        DensityLevel.C: LeadFillets(0.4, -0.1, 0.4, 0.25),
    },
)
TallAluminumElectrolyticLeads = LeadProtrusion(
    "TallAluminumElectrolyticLeads",
    {
        DensityLevel.A: LeadFillets(1.0, 0.0, 0.6, 1.0),
        DensityLevel.B: LeadFillets(0.7, -0.05, 0.5, 0.5),
        DensityLevel.C: LeadFillets(0.4, -0.1, 0.4, 0.25),
    },
)
