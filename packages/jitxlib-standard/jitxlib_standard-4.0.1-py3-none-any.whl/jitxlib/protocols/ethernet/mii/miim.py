from jitx.net import Port


class MIIM(Port):
    """
    Media Independent Interface Management (MIIM) bundle

    This is a typical management interface for PHYs and other
    similar ethernet devices.

    This interface is also known as Management Data Input/Output (MDIO)
    or the Serial Management Interface (SMI).

    see `https://en.wikipedia.org/wiki/Management_Data_Input/Output`
    """

    mdc = Port()
    "Clock Line for the Serial Interface"
    mdio = Port()
    "Bidirectional Data Line for the Serial Interface"
