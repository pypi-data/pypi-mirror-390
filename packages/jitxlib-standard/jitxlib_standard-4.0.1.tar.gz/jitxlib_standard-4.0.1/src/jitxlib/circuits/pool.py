from jitx.circuit import Circuit
from jitx.net import Provide
from jitx.inspect import decompose


class CircuitPool(Circuit):
    """Circuit Pool aggregates a collection of Provide ports
    from a set of circuit instances.

    The conceptual idea here is that we define a circuit
    that introduces a set of "Provide" ports. Then you
    pass that circuit to the CircuitPool and we create multiple
    instances of that circuit. The `CircuitPool` then proxies
    all of the provide ports from the individual circuits and
    pools them together. This allows for provides across
    different circuits to be used as if they were one big
    circuit.
    """

    def __init__(self, circuitDef: type[Circuit], count: int):
        assert count > 0
        self.circuits = [circuitDef() for _ in range(count)]

        # Introspect all Provide of subcircuits, and create a new equivalent
        # Provide for each one.
        self.provides = [
            # one_of or all_of both work here, since there's only one option for each,
            # but one_of is a simpler structure, so we use that.
            Provide(p.bundle).one_of(lambda b, c=c, p=p: [{b: c.require(p.bundle)}])
            for c in self.circuits
            for p in decompose(c, Provide)
        ]
