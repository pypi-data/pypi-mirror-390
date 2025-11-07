import itertools
from collections.abc import Sequence

from jitx.container import Container
from jitx.net import Port, Provide


class GatePort(Port):
    """N-Input Logic Gate Bundle

    This is the base bundle implementation for a logic gate and is intended to
    drive the interface for gate bundle definitions.

    This definition is not specific to the function of the gate. It is
    compatible with AND, OR, and other gates, as long as the gate has one
    output. This is sufficient for most applications.

    Args:
        num_inputs: number of input pins to the gate
    """

    def __init__(self, num_inputs: int):
        self.inputs = [Port() for _ in range(1, num_inputs + 1)]
        """Gate Inputs"""
        self.output = Port()
        """Gate Output"""


class GateProvides[T: Port](Container):
    """Gate Bundle Provider

    This is a container to add provides for a gate bundle.
    >>> self.gate_provides = GateProvides(self.output, self.inputs)
    >>> gate_port = self.require(GatePort(len(self.inputs))))
    """

    def __init__(self, output: T, inputs: Sequence[T]):
        width = len(inputs)
        self.options = Provide(GatePort(width))

        @self.options.one_of
        def provide(bundle: GatePort):
            return [
                tuple(
                    itertools.chain(
                        ((bundle.output, output),),
                        ((bundle.inputs[i], p) for i, p in enumerate(permutation)),
                    )
                )
                for permutation in itertools.permutations(inputs)
            ]
