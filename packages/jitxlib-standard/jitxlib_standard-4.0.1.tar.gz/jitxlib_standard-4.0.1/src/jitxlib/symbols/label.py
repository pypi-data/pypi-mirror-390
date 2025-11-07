"""
Labels module for JITX Standard Library

This module provides configurations for reference designator and value labels in symbols
"""

from __future__ import annotations
from dataclasses import dataclass
from functools import reduce

from jitx.anchor import Anchor
from jitx.inspect import extract
from jitx.shapes import Shape
from jitx.shapes.primitive import Polyline, Text
from jitx.symbol import Direction, Pin, Symbol
from jitx.transform import Transform


# LabelConfig constants
DEF_REF_LABEL_SIZE = 1.0
DEF_VALUE_LABEL_SIZE = 1.0


@dataclass
class LabelConfig:
    """Configuration for reference desigantor and value labels in symbols"""

    ref_size: float = DEF_REF_LABEL_SIZE
    """Reference designator label size"""
    value_size: float | None = DEF_VALUE_LABEL_SIZE
    """Value label size, can be set to None to avoid creating a value label"""

    def __post_init__(self):
        if self.ref_size <= 0:
            raise ValueError(
                f"Reference designator label size {self.ref_size} must be positive"
            )

        if self.value_size is not None and self.value_size <= 0:
            raise ValueError(
                f"Value label size {self.ref_size} must be positive if provided"
            )


@dataclass
class LabelConfigurable:
    """Label configuration wrapper, useful for handling defaults"""

    label_config: LabelConfig | None = None

    def __init__(self, label_config: LabelConfig | None = None):
        self.label_config = label_config

    def get_label_config(self) -> LabelConfig:
        """
        Returns the label configuration.

        If an label config is specified, it will be used.
        Otherwise, the config will be pulled from the context.
        If no context is available, a default config will be used.
        """
        from .context import SymbolStyleContext

        context = SymbolStyleContext.get()

        if self.label_config is None:
            if context is None:
                return LabelConfig()
            else:
                return context.label_config
        else:
            return self.label_config


class LabelledSymbol(Symbol):
    """Base class for symbols with reference designator and/or value labels

    Subclasses must have a 'config' property that extends LabelConfigurable to provide
    label configuration.
    """

    reference: Shape[Text]
    value: Shape[Text]

    @property
    def label_config(self) -> LabelConfigurable:
        """Configuration object that provides label configuration

        Subclasses must override this property to provide their configuration.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement the 'config' property "
            f"returning a LabelConfigurable instance"
        )

    def _build_labels(
        self,
        *,
        ref: Direction | None = None,
        value: Direction | None = None,
        margin: float = 0.5,
    ) -> None:
        """Build reference designator labels for the symbol."""
        shapes = list(extract(self, Shape))
        for pin in extract(self, Pin):
            start = pin.at
            if pin.direction == Direction.Up:
                end = (start[0], start[1] + pin.length)
            elif pin.direction == Direction.Down:
                end = (start[0], start[1] - pin.length)
            elif pin.direction == Direction.Right:
                end = (start[0] + pin.length, start[1])
            elif pin.direction == Direction.Left:
                end = (start[0] - pin.length, start[1])
            else:
                raise ValueError(f"Invalid direction: {pin.direction}")
            # This width chosen to match the pin width in the schematic visualizer.
            # The value really just needs to be a small positive value.
            shapes.append(Polyline(0.15 / 1.27, [start, end]))
        bounds = reduce(
            lambda a, b: a.union(b), [s.to_shapely() for s in shapes]
        ).bounds
        label_config = self.label_config.get_label_config()
        ref_size = label_config.ref_size
        value_size = label_config.value_size
        show_value = value_size is not None
        avg_size = (ref_size + value_size) / 2 if show_value else ref_size
        if ref:
            if ref == Direction.Up:
                offset = (0.0, bounds[3] + margin)
                anchor = Anchor.S
            elif ref == Direction.Down:
                offset = (0.0, bounds[1] - margin)
                anchor = Anchor.N
            elif ref == Direction.Right:
                offset = (bounds[2] + margin, 0.0)
                anchor = Anchor.W
            else:
                offset = (bounds[0] - margin, 0.0)
                anchor = Anchor.E
            if ref == value and show_value:
                if ref == Direction.Up:
                    offset = (offset[0], offset[1] + (value_size or 0))
                elif ref == Direction.Down:
                    pass
                else:
                    offset = (offset[0], offset[1] + avg_size / 2)
            self.reference = Transform(offset) * Text(
                string=">REF",
                size=ref_size,
                anchor=anchor,
            )
        if value and show_value:
            if value == Direction.Up:
                offset = (0.0, bounds[3] + margin)
                anchor = Anchor.S
            elif value == Direction.Down:
                offset = (0.0, bounds[1] - margin)
                anchor = Anchor.N
            elif value == Direction.Right:
                offset = (bounds[2] + margin, 0.0)
                anchor = Anchor.W
            else:
                offset = (bounds[0] - margin, 0.0)
                anchor = Anchor.E
            if ref == value:
                if ref == Direction.Up:
                    pass
                elif ref == Direction.Down:
                    offset = (offset[0], offset[1] - ref_size)
                else:
                    offset = (offset[0], offset[1] - avg_size / 2)
            self.value = Transform(offset) * Text(
                string=">VALUE",
                size=value_size,
                anchor=anchor,
            )
