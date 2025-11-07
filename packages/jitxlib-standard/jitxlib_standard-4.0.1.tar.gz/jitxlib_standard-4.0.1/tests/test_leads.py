import jitx
from jitx.toleranced import Toleranced
import jitx.test

from jitxlib.landpatterns.leads import SMDLead, LeadProfile
from jitxlib.landpatterns.ipc import DensityLevel
from jitxlib.landpatterns.leads.protrusions import SmallGullWingLeads


class SMDLeadTestCase(jitx.test.TestCase):
    def test_basic(self):
        uut = SMDLead(
            length=Toleranced.min_typ_max(0.35, 0.4, 0.45),
            width=Toleranced.min_typ_max(0.25, 0.3, 0.35),
            lead_type=SmallGullWingLeads,
        )

        res = uut.compute_constraints(
            Toleranced.min_typ_max(3.9, 4.0, 4.1), DensityLevel.A
        )

        self.assertAlmostEqual(res.Gmin, 2.276393, places=5)
        self.assertAlmostEqual(res.Zmax, 5.2, places=5)
        self.assertAlmostEqual(res.Xmin, 0.37, places=5)


class LeadProfileTestCase(jitx.test.TestCase):
    def test_basic(self):
        uut = LeadProfile(
            span=Toleranced.min_typ_max(4.5, 4.75, 5.0),
            pitch=0.5,
            type=SMDLead(
                length=Toleranced.min_typ_max(0.35, 0.4, 0.45),
                width=Toleranced.min_typ_max(0.25, 0.3, 0.35),
                lead_type=SmallGullWingLeads,
            ),
        )

        placements = uut.compute_placements(DensityLevel.B)
        self.assertAlmostEqual(placements.pad_size[0], 1.30495, places=5)
        self.assertAlmostEqual(placements.pad_size[1], 0.31, places=5)
        self.assertAlmostEqual(placements.center, 4.39505, places=5)
        self.assertAlmostEqual(placements.pitch, 0.5, places=5)
