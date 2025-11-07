"""
Test module for resistor symbols functionality.

This module contains comprehensive tests for the resistor symbol implementations,
including basic resistors, variable resistors, photoresistors, and potentiometers.
"""

# Import JITX components for the design
import jitx.test
from jitx.component import Component
from jitx.circuit import Circuit
from jitx.landpattern import Landpattern, Pad
from jitx.net import Port
from jitx.design import Design
from jitx.shapes.primitive import Polygon, Polyline
from jitx.feature import Silkscreen

# Import our custom resistor symbol
from jitxlib.symbols.context import SymbolStyleContext
from jitxlib.symbols.arrow import ArrowConfig, ArrowStyle
from jitxlib.symbols.label import LabelConfig
from jitxlib.symbols.resistor import (
    PhotoResistorSymbol,
    PhotoResistorConfig,
    PotentiometerSymbol,
    ResistorStyle,
    VariableResistorSymbol,
    VariableResistorConfig,
    ResistorSymbol,
    ResistorConfig,
)

from examples.defaults.board import DefaultBoard, DefaultSubstrate


class ResistorPad(Pad):
    shape = Polygon([(-0.3, -0.4), (0.3, -0.4), (0.3, 0.4), (-0.3, 0.4)])


class ResistorLandpattern(Landpattern):
    pad1 = ResistorPad().at(-1.0, 0)
    pad2 = ResistorPad().at(1.0, 0)

    # Add silkscreen showing resistor body
    silkscreen = Silkscreen(
        Polyline(
            0.1,
            [
                (-0.8, 0.3),
                (-0.4, 0.3),
                (-0.2, -0.3),
                (0.0, 0.3),
                (0.2, -0.3),
                (0.4, 0.3),
                (0.8, 0.3),
            ],
        )
    )

    def __init__(self, tripad: bool):
        if tripad:
            self.pad3 = ResistorPad().at(0.0, 1.0)
            self.silkscreen2 = Silkscreen(Polyline(0.1, [(0.0, 0.7), (0.0, 0.4)]))
            self.silkscreen3 = Silkscreen(
                Polyline(0.1, [(-0.1, 0.5), (0.0, 0.4), (0.1, 0.5)])
            )


class ResistorComponent(Component):
    p = {
        1: Port(),
        2: Port(),
    }

    mpn = "RES"
    manufacturer = "Test Co"
    reference_designator_prefix = "R"

    def __init__(self, symbol: ResistorSymbol):
        is_potentiometer = isinstance(symbol, PotentiometerSymbol)
        self.symbol = symbol
        self.landpattern = ResistorLandpattern(is_potentiometer)


class ResistorCircuit(Circuit):
    # =================================================================
    # Demonstration of Different Configuration Methods
    # =================================================================

    # Method 1: Default constructors (using context or built-in defaults)
    default_resistor = ResistorComponent(symbol=ResistorSymbol())
    default_variable = ResistorComponent(symbol=VariableResistorSymbol())
    default_photo = ResistorComponent(symbol=PhotoResistorSymbol())
    default_potentiometer = ResistorComponent(symbol=PotentiometerSymbol())

    # Method 2: Individual parameter overrides using kwargs
    kwargs_resistor = ResistorComponent(
        symbol=ResistorSymbol(pitch=6.0, amplitude=0.4, line_width=0.3)
    )
    kwargs_variable = ResistorComponent(
        symbol=VariableResistorSymbol(pitch=3.0, amplitude=0.6, arrow_span=2.0)
    )
    kwargs_photo = ResistorComponent(
        symbol=PhotoResistorSymbol(
            pitch=3.5,
            amplitude=0.5,
            arrow_margin=0.5,
            arrow_pitch=0.8,
            arrow_angle=60.0,
            line_width=0.1,
        )
    )

    # Method 3: Using configuration objects
    config_resistor = ResistorComponent(
        symbol=ResistorSymbol(
            config=ResistorConfig(
                pitch=5.0,
                amplitude=0.3,
                periods=2.5,
                line_width=0.25,
                label_config=LabelConfig(ref_size=0.5),
            )
        )
    )
    config_variable = ResistorComponent(
        symbol=VariableResistorSymbol(
            config=VariableResistorConfig(
                pitch=4.0,
                amplitude=0.4,
                periods=3.5,
                arrow_span=2.5,
                label_config=LabelConfig(ref_size=1.5),
            )
        )
    )
    config_photo = ResistorComponent(
        symbol=PhotoResistorSymbol(
            config=PhotoResistorConfig(
                pitch=4.5,
                amplitude=0.45,
                periods=3.0,
                arrow_margin=0.3,
                arrow_pitch=0.9,
                arrow_angle=30.0,
                line_width=0.15,
            )
        )
    )

    # Method 4: Config object + kwargs overrides (kwargs take precedence)
    config_plus_kwargs_resistor = ResistorComponent(
        symbol=ResistorSymbol(
            config=ResistorConfig(pitch=3.0, amplitude=0.2),  # Base config
            pitch=7.0,  # Override pitch via kwargs (takes precedence!)
            line_width=0.4,  # Override line_width via kwargs
        )
    )
    config_plus_kwargs_variable = ResistorComponent(
        symbol=VariableResistorSymbol(
            config=VariableResistorConfig(pitch=2.5, arrow_span=1.5),  # Base config
            amplitude=0.7,  # Override amplitude via kwargs
            periods=4.5,  # Override periods via kwargs
            line_width=0.1,
        )
    )

    # Method 5: Edge cases and special configurations
    # Demonstrating extreme parameter values and special behaviors
    minimal_resistor = ResistorComponent(
        symbol=ResistorSymbol(pitch=2.0, amplitude=0.1, periods=1.0)
    )
    wide_line_resistor = ResistorComponent(
        symbol=ResistorSymbol(line_width=0.6, amplitude=0.8)
    )

    # Method 6: Custom ArrowConfig for Variable Resistor
    # First, define a custom arrow configuration.
    custom_arrow_config = ArrowConfig(
        style=ArrowStyle.CLOSED_ARROW,
        head_dims=(1.0, 1.0),
        line_width=0.25,
    )
    # Using a full VariableResistorConfig object
    var_res_with_custom_arrow_config = ResistorComponent(
        symbol=VariableResistorSymbol(
            config=VariableResistorConfig(
                pitch=5.0,
                arrow_span=2.0,
                arrow_config=custom_arrow_config,
            )
        )
    )
    # Using kwargs to pass the arrow config directly
    var_res_with_custom_arrow_kwarg = ResistorComponent(
        symbol=VariableResistorSymbol(
            pitch=5.0,
            arrow_span=2.0,
            arrow_config=custom_arrow_config,
        )
    )

    def __init__(self):
        self.test_nets = [
            # Parallel connection: All first terminals together
            self.default_resistor.p[1] + self.kwargs_resistor.p[1],
            self.kwargs_resistor.p[1] + self.config_resistor.p[1],
            self.config_resistor.p[1] + self.config_plus_kwargs_resistor.p[1],
            self.config_plus_kwargs_resistor.p[1] + self.minimal_resistor.p[1],
            self.minimal_resistor.p[1] + self.wide_line_resistor.p[1],
            self.wide_line_resistor.p[1] + self.default_variable.p[1],
            self.default_variable.p[1] + self.kwargs_variable.p[1],
            # self.kwargs_variable.p[1] + self.config_variable.p[1],
            self.config_variable.p[1] + self.config_plus_kwargs_variable.p[1],
            self.config_plus_kwargs_variable.p[1] + self.default_photo.p[1],
            self.default_photo.p[1] + self.kwargs_photo.p[1],
            self.kwargs_photo.p[1] + self.config_photo.p[1],
            self.config_photo.p[1] + self.default_potentiometer.p[1],
            self.default_potentiometer.p[1]
            + self.var_res_with_custom_arrow_config.p[1],
            self.var_res_with_custom_arrow_config.p[1]
            + self.var_res_with_custom_arrow_kwarg.p[1],
            # self.default_potentiometer.p[1] # Parallel connection: All second terminals together
            self.default_resistor.p[2] + self.kwargs_resistor.p[2],
            self.kwargs_resistor.p[2] + self.config_resistor.p[2],
            self.config_resistor.p[2] + self.config_plus_kwargs_resistor.p[2],
            self.config_plus_kwargs_resistor.p[2] + self.minimal_resistor.p[2],
            self.minimal_resistor.p[2] + self.wide_line_resistor.p[2],
            self.wide_line_resistor.p[2] + self.default_variable.p[2],
            self.default_variable.p[2] + self.kwargs_variable.p[2],
            # self.kwargs_variable.p[2] + self.config_variable.p[2],
            self.config_variable.p[2] + self.config_plus_kwargs_variable.p[2],
            self.config_plus_kwargs_variable.p[2] + self.default_photo.p[2],
            self.default_photo.p[2] + self.kwargs_photo.p[2],
            self.kwargs_photo.p[2] + self.config_photo.p[2],
            self.config_photo.p[2] + self.default_potentiometer.p[2],
            self.default_potentiometer.p[2]
            + self.var_res_with_custom_arrow_config.p[2],
            self.var_res_with_custom_arrow_config.p[2]
            + self.var_res_with_custom_arrow_kwarg.p[2],
        ]


class ResistorDesign(Design):
    board = DefaultBoard()
    substrate = DefaultSubstrate()
    symbol_style_context = SymbolStyleContext(
        resistor_style=ResistorStyle.TRIANGLE_WAVE,
        # resistor_style=ResistorStyle.OPEN_RECTANGLE,
        resistor_config=ResistorConfig(
            pitch=4,
            porch_width=0.1,
            amplitude=1,
            periods=3,
            line_width=0.25,
        ),
        photo_resistor_config=PhotoResistorConfig(
            arrow_margin=0.25,
            arrow_pitch=1.5,
            arrow_angle=43,
        ),
        variable_resistor_config=VariableResistorConfig(arrow_span=5),
        arrow_config=ArrowConfig(
            style=ArrowStyle.OPEN_ARROW,
            head_dims=(0.4, 0.4),
            shaft_length=1.0,
            line_width=0.075,
        ),
    )

    def __init__(self):
        self.circuit = ResistorCircuit()


class ResistorSymbolTest(jitx.test.TestCase):
    def test_instantiate_and_translate_design(self):
        design = ResistorDesign()

        import jitx._translate.design

        jitx._translate.design.package_design(design)
