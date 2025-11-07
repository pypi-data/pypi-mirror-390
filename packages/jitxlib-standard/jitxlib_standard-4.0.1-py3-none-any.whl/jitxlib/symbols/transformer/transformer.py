"""
Transformer symbol for JITX Standard Library

This module provides the transformer symbol definition, which is composed
of multiple inductor-like coils.
"""

from __future__ import annotations
from collections.abc import Sequence
from dataclasses import dataclass, replace, field
import math
import warnings

from jitx._structural import Container
from jitx.container import Composite
from jitx.shapes import Shape
from jitx.shapes.primitive import Circle, Polyline
from jitx.symbol import Direction, Pin
from jitx.transform import GridPoint, Point, Transform, transform_grid_point
from ..common import DEF_LONG_PIN_LENGTH, DEF_PAD_NAME_SIZE
from ..inductor import (
    InductorConfig,
    InductorCoreStyle,
    InductorSymbol,
)
from ..label import LabelConfigurable, LabelledSymbol


@dataclass
class CoilConfig:
    """Configuration for a single transformer coil"""

    config: InductorConfig
    """
    Inductor parameters for the coil.
    'core_style' is ignored and should instead be specified at the Transformer level.
    'polarized' is ignored and should instead be specified at this CoilConfig level.
    """
    direction: Direction
    """The direction of the coil, either Direction.Left or Direction.Right."""
    taps: tuple[int, ...] = ()
    """
    Optional tap locations for this coil.
    The indices in this list are dependent on the number of 'periods' in the coil's 'config'.
    The max number of taps is one less than the number of periods.
    These indices are 0-based.
    """
    polarized: Direction | None = None
    """
    Optional polarization marker that adds a dot near either the top or bottom of the coil.
    The direction specified should be either Direction.Up or Direction.Down, if not None.
    """

    def __post_init__(self):
        # Override core_style and polarized from InductorConfig
        self.config = replace(
            self.config, core_style=InductorCoreStyle.NO_CORE, polarized=False
        )


# TransformerConfig constants
DEF_TRANS_PITCH = 2.0
DEF_TRANS_TAP_LENGTH = 2


@dataclass
class TransformerConfig(LabelConfigurable):
    """Configuration for a transformer symbol."""

    coils: list[CoilConfig] = field(default_factory=list)
    """The coils are an ordered list of CoilConfig objects, rendered in order depending on their Left/Right direction."""
    core_style: InductorCoreStyle = InductorCoreStyle.NO_CORE
    """
    Style for the graphical representation of the transformer's core.
    This is typically used to indicate features like "Air Core", "Iron Core", or "Ferrite Core", etc.
    """
    tap_length: int = DEF_TRANS_TAP_LENGTH
    """
    The extra line added in the X direction to extend the connection points away from the winding.
    This value is optional but can be useful for clearer symbols when using windings with one or more taps.
    This extends the tap position line either to the left or right depending on the coil configuration.
    Integral values are required to fit to the schematic grid.
    """
    pin_pitch: float = DEF_TRANS_PITCH
    """The size of the winding half-circle shapes."""
    pin_length: int = DEF_LONG_PIN_LENGTH
    """The length of the pins extending out from the winding."""
    pad_name_size: float = 2 * DEF_PAD_NAME_SIZE
    """The text size for the pad reference labels shown on each pin."""


class TransformerSymbol(LabelledSymbol):
    """Transformer symbol with coil graphics and pins."""

    config: TransformerConfig
    inductor_composites: tuple[Composite, ...]
    core_bars: tuple[Polyline, Polyline] | Polyline | None = None

    def __init__(self, config: TransformerConfig | None = None, **kwargs):
        """
        Initialize transformer symbol

        Args:
            config: Config object, or None to use context defaults
            **kwargs: Individual parameters to override defaults
        """
        if config is None:
            config = TransformerConfig()

        config = replace(config, **kwargs)

        self.config = config
        self.pad_name_size = self.config.pad_name_size

        if len(self.coils) < 2:
            raise ValueError("Transformer must have at least two coils.")

        if not all(
            c.direction in (Direction.Left, Direction.Right) for c in self.coils
        ):
            raise ValueError("All coils must be directed left or right.")

        if not any(c.direction == Direction.Left for c in self.coils) and not any(
            c.direction == Direction.Right for c in self.coils
        ):
            raise ValueError(
                "Transformer must have at least one left and one right coil."
            )

        self._build_artwork()
        self._build_pins()
        self._build_labels(ref=Direction.Up, value=Direction.Down)

    def _build_artwork(self):
        """Build the artwork for the transformer symbol."""
        height_spans = []
        inductor_composites = []
        for side in (Direction.Left, Direction.Right):
            coils = self._get_coils_for_side(side)
            offsets, start_y, end_y = self._compute_coil_offsets(coils)
            for coil, offset in zip(coils, offsets, strict=False):
                transform = Transform(
                    translate=(0, 0), scale=(-1 if side is Direction.Left else 1, 1)
                ) * Transform(offset)
                inductor, shapes = self._build_coil(coil)
                composite = Composite(transform)
                composite.inductor = inductor
                composite.artwork = tuple(shapes)
                inductor_composites.append(composite)
            height_spans.append((start_y, end_y))

        self.inductor_composites = tuple(inductor_composites)

        max_start = max(span[0] for span in height_spans)
        min_end = min(span[1] for span in height_spans)

        # Core bars
        lw = 0.1
        if self.core_style == InductorCoreStyle.SINGLE_BAR_CORE:
            self.core_bars = Polyline(lw, [(0, max_start), (0, min_end)])
        elif self.core_style == InductorCoreStyle.DOUBLE_BAR_CORE:
            x_offset = lw * 3.0
            self.core_bars = (
                Polyline(lw, [(x_offset, max_start), (x_offset, min_end)]),
                Polyline(lw, [(-x_offset, max_start), (-x_offset, min_end)]),
            )

    def _get_coils_for_side(self, side: Direction) -> tuple[CoilConfig, ...]:
        """
        Get the coils for a given side of the transformer.
        Returns a list of tuples, where the first element is the 0-based index of the coil,
        and the second element is the coil configuration.
        """
        return tuple(c for c in self.coils if c.direction == side)

    def _compute_coil_offsets(
        self, coils: Sequence[CoilConfig]
    ) -> tuple[tuple[Point, ...], float, float]:
        """
        Compute the offsets for the coils.
        Returns a tuple of:
        - A tuple of points, one for the center of each coil.
        - The total height of the coils.
        - The total width of the coils.
        """
        coil_heights = [self._compute_ind_pitch(c) for c in coils]
        coil_padding = 2
        total_height = sum(coil_heights) + (coil_padding * (len(coil_heights) - 1))

        # Space out the coils on this side so that they are centered around Y = 0.
        y_start_off_grid = total_height / 2

        # Floor so that the coil-end wires and taps start on the grid.
        y_start_origin = math.floor(y_start_off_grid)
        y_start = y_start_origin

        # If the user makes the pin_length larger, then we need more space in the X direction.
        x_offset = max(1, self.pin_pitch)
        offsets: list[Point] = []
        for coil_height in coil_heights:
            o = (x_offset, y_start - (coil_height / 2))
            y_start -= coil_height + coil_padding
            offsets.append(o)
        return (tuple(offsets), y_start_origin, y_start_origin - total_height)

    def _compute_ind_pitch(self, coil: CoilConfig) -> float:
        """Compute the end to end distance of the inductor symbol that makes up this coil."""
        return (coil.config.periods * self.pin_pitch) + (coil.config.porch_width * 2.0)

    def _build_coil(self, coil: CoilConfig) -> tuple[InductorSymbol, tuple[Shape]]:
        """Build the artwork for a transformer coil."""

        inductor_config = replace(coil.config, pitch=self._compute_ind_pitch(coil))
        inductor = InductorSymbol(config=inductor_config, partial_symbol=True)
        shapes = []

        ip2 = self._compute_ind_pitch(coil) / 2

        # Construct the end and tap lines if present
        lw = coil.config.line_width
        tl = self.tap_length
        if tl > 0:
            shapes.append(Polyline(lw, [(0, ip2), (tl, ip2)]))
            shapes.append(Polyline(lw, [(0, -ip2), (tl, -ip2)]))

            # Add the tap lines off of specific winding positions.
            # Be careful about whether there is a porch-width specified because this will throw
            # off the calculationg from the grid.
            tap_pts = self._compute_tap_endpoints(coil)
            for pt in tap_pts:
                shapes.append(Polyline(lw, [(0, pt[1]), pt]))

        # Add the polarization dot if present
        if coil.polarized:
            pol_size = self.pin_pitch * 0.4
            dot_y = ip2 - coil.config.porch_width - self.pin_pitch / 2
            if coil.polarized == Direction.Up:
                shapes.append(Transform((0, dot_y)) * Circle(diameter=pol_size))
            else:
                shapes.append(Transform((0, -dot_y)) * Circle(diameter=pol_size))

        return (inductor, tuple(shapes))

    def _compute_tap_endpoints(self, coil: CoilConfig) -> list[GridPoint]:
        """Compute the endpoints for a tap line."""
        pw = coil.config.porch_width
        pin_pitch = self.pin_pitch
        tl = self.tap_length
        p2 = self._compute_ind_pitch(coil) / 2
        pts = []
        for tap in coil.taps:
            y = pw + (tap + 1) * pin_pitch
            pts.append((tl, p2 - y))
        if any(not (p[0].is_integer() and p[1].is_integer()) for p in pts):
            warnings.warn(
                f"Tap points for coil {coil.direction} are not on the grid: {pts}. This will cause the pins to be misaligned.",
                stacklevel=3,
            )
        return pts

    def _build_pins(self):
        # Pin container, one entry per coil with a leading False to skip index 0.
        self.N = {}

        # Compute offsets for each side
        left_coils = [
            (i, c) for i, c in enumerate(self.coils) if c.direction == Direction.Left
        ]
        right_coils = [
            (i, c) for i, c in enumerate(self.coils) if c.direction == Direction.Right
        ]
        left_offsets, _, _ = self._compute_coil_offsets([c[1] for c in left_coils])
        right_offsets, _, _ = self._compute_coil_offsets([c[1] for c in right_coils])

        # Create mapping of indices to offsets
        offset_map = {
            i: offset for (i, _), offset in zip(left_coils, left_offsets, strict=False)
        }
        offset_map.update(
            {
                i: offset
                for (i, _), offset in zip(right_coils, right_offsets, strict=False)
            }
        )

        # Build pins in original order
        for i, coil in enumerate(self.coils):
            side = coil.direction
            offset = offset_map[i]

            transform = Transform(
                translate=(0, 0), scale=(-1 if side is Direction.Left else 1, 1)
            ) * Transform(offset)

            # Endpoint pins of the transformer
            h = self._compute_ind_pitch(coil)
            if not h.is_integer() or h % 2 != 0:
                warnings.warn(
                    f"Height of coil {i} is not an even integer: {h}. Rounding down to prevent pin misalignment.",
                    stacklevel=3,
                )
            h2 = math.floor(h / 2.0)
            top_pos = transform_grid_point(transform, (self.tap_length, h2))
            bot_pos = transform_grid_point(transform, (self.tap_length, -h2))

            # Take the polarization direction into account so that
            # p[1] is the positive (side with the dot) and p[2] is the negative.
            if coil.polarized is None:
                pos_order = (top_pos, bot_pos)
            elif coil.polarized == Direction.Up:
                pos_order = (top_pos, bot_pos)
            else:
                pos_order = (bot_pos, top_pos)

            container = CoilPortContainer()
            container.p = {
                j + 1: Pin(
                    at=pos,
                    length=self.pin_length,
                    direction=side,
                )
                for j, pos in enumerate(pos_order)
            }

            # Tap point pins
            tap_pts = self._compute_tap_endpoints(coil)
            container.tap = {
                j + 1: Pin(
                    at=transform_grid_point(transform, pos),
                    length=self.pin_length,
                    direction=side,
                )
                for j, pos in enumerate(tap_pts)
            }
            self.N[i + 1] = container

    # Convenience properties
    @property
    def coils(self) -> list[CoilConfig]:
        """See :attr:`~.TransformerConfig.coils`."""
        return self.config.coils

    @property
    def core_style(self) -> InductorCoreStyle:
        """See :attr:`~.TransformerConfig.core_style`."""
        return self.config.core_style

    @property
    def tap_length(self) -> int:
        """See :attr:`~.TransformerConfig.tap_length`."""
        return self.config.tap_length

    @property
    def pin_pitch(self) -> float:
        """See :attr:`~.TransformerConfig.pin_pitch`."""
        return self.config.pin_pitch

    @property
    def pin_length(self) -> int:
        """See :attr:`~.TransformerConfig.pin_length`."""
        return self.config.pin_length

    @property
    def label_config(self) -> LabelConfigurable:
        """Configuration object that provides label configuration"""
        return self.config


# Used to store the pins and taps for each coil, aiding in their precise naming.
class CoilPortContainer(Container):
    def __init__(self):
        self.p = {}
        self.tap = {}
