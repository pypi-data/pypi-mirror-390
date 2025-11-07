"""
Physics Utility Definitions and Functions
"""

import math


PERMITTIVITY_VAC = 8.85418782e-12  #  (F / m), also (s^4 * A^2) / (kg * m^3)
"""Permittivity of Free Space (Vacuum)
see `https://en.wikipedia.org/wiki/Vacuum_permittivity`
"""
E0 = PERMITTIVITY_VAC

PERMEABILITY_VAC = math.pi * 4.0e-7  # H / m
"""Permeability of Free Space (Vacuum)
see `https://en.wikipedia.org/wiki/Vacuum_permeability`
"""
M0 = PERMEABILITY_VAC


def wave_impedance(eps_r: float, mu_r: float):
    """Compute the Wave Impedance for a specific medium.
    The wave impedance is the ratio of the electric field to the magnetic field.

    Args:
        eps_r: Relative Permittivity of the Medium. This value should be greater than or equal to 1.0
        mu_r: Relative Magnetic Permeability of the Medium. This value should be greater than or equal to 1.0.

    Returns:
        The wave impedance in Ohms.
    """
    assert eps_r >= 1.0
    assert mu_r >= 1.0
    return math.sqrt((M0 * mu_r) / (E0 * eps_r))


def phase_velocity(eps_r: float, mu_r: float = 1.0):
    """Compute the Phase Velocity for a specific medium.

    The phase velocity is the signal propagation velocity in a particular
    medium. This function assumes that the medium of propagation is homogeneous.
    For non-homogeneous medium, the user should compute the effective relative permittivity
    and then pass it to this function.

    Args:
        eps_r: Relative Permittivity of the Medium. This value should be greater than or equal to 1.0
        mu_r:  Relative Magnetic Permeability of the Medium. This value should be greater than or equal to 1.0.
            The default value for this parameter is 1.0 - this is a typical default for non-magnetic materials.

    Returns:
        The signal propagation velocity in mm / s.
    """
    assert eps_r >= 1.0
    assert mu_r >= 1.0
    return 1000.0 / math.sqrt((M0 * mu_r) * (E0 * eps_r))


SPEED_OF_LIGHT_VAC = phase_velocity(1)
"""Speed of Light in Free Space (Vacuum) in mm / s"""


def guide_wavelength(f: float, eps_r: float, mu_r: float = 1.0):
    """Compute the Guide Wavelength for a specific frequency in a medium.
    The guide wavelength is the wavelength of a TEM wave in a specific medium.

    Args:
        f: Frequency in Hz
        eps_r: Relative Permittivity of the Medium. This value should be greater than or equal to 1.0
        mu_r: Relative Magnetic Permeability of the Medium. This value should be
            greater than or equal to 1.0.

    Returns:
        Guide Wavelength at `f` in mm.
    """
    assert f > 0, "frequency must be positive"
    assert eps_r >= 1.0
    assert mu_r >= 1.0
    return phase_velocity(eps_r, mu_r) / f
