from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any, override
from jitx.landpattern import Pad
from jitx.transform import Transform
from jitx._structural import Structurable, Ref

from . import LandpatternProvider, LandpatternGenerator


@dataclass(frozen=True)
class GridPosition:
    """Grid Position

    This class represents a position in a grid of pads as well as a pose for
    the pad at that position. This is used by the :py:class:`~GridLandpatternGenerator`
    classes during the construction of a landpattern.
    """

    row: int
    """The row of the grid position, zero-indexed."""

    column: int
    """The column of the grid position, zero-indexed."""

    pose: Transform
    """The pose of the pad at the grid position."""

    def __post_init__(self):
        assert self.row >= 0
        assert self.column >= 0


class GridLayout:
    _num_rows: int = 0
    _num_cols: int = 0


class GridLayoutInterface(GridLayout, LandpatternProvider):
    def _generate_layout(self) -> Iterable[GridPosition]:
        """Generate a sequence of all the grid positions in the landpattern in
        the order they should be traversed. Note that the numbering scheme will
        likely ignore the order of the sequence, but it may be used to determine
        pin 1, etc."""
        raise NotImplementedError(f"{self.__class__.__name__}._generate_layout")

    def _transform_layout(self, pos: GridPosition) -> GridPosition:
        """Transform a grid position. This can be used to transform the
        landpattern to a different coordinate system, such as a different origin
        or orientation."""
        return pos

    def _map_position(self, pos: GridPosition) -> tuple[int, int]:
        """Map a grid position to a row and column. This is primarily used to
        eliminate unused rows or columns or offset indexing. Care should be
        taken to not generate collisions. The resulting row and column will be
        used to determine the pad numbering and does not affect anything else.
        Subclasses should call ``super()._map_position`` to ensure that other
        mixins will be able to influence the position mapping as well."""
        return pos.row, pos.column

    def _assign_pad(self, r: int, c: int, pad: Pad):
        """Assign a pad to the specified grid position."""
        raise NotImplementedError(
            f"Missing {self.__class__.__name__}._assign_pad. The landpattern generator must specify a numbering scheme."
        )

    def _get_pad(self, r: int, c: int) -> Pad:
        """Get the pad at the specified row and column."""
        raise NotImplementedError(
            f"Missing {self.__class__.__name__}._get_pad. The landpattern generator must specify a numbering scheme."
        )

    def _get_grid_position(self, pos: GridPosition) -> Pad:
        """Get the pad at the specified grid position."""
        return self._get_pad(*self._map_position(pos))

    def _active_pad(self, pos: GridPosition) -> bool:
        """Determine if a pad is active. Will be queried during construction of
        the landpattern to filter out grid locations that should not generate
        pads."""
        return True

    def _create_pad(self, pos: GridPosition) -> Pad:
        """Create a pad at the specified grid position."""
        raise ValueError("No applicable pad generator found")

    @override
    def _build(self):
        super()._build()
        for pos in self._generate_layout():
            if self._active_pad(pos):
                self._assign_pad(
                    *self._map_position(self._transform_layout(pos)),
                    self._create_pad(pos),
                )


class A1(GridLayoutInterface):
    """Simple utility mixin to offset the minor index to start at 1 instead of
    0, e.g.  A[1]. Note that this offsets the minor index, which is typically
    but not always the column, and the order matters if using a numbering mixin
    that changes that, going before such mixins as
    :py:class:`~ColumnMajorOrder`."""

    @override
    def _map_position(self, pos: GridPosition) -> tuple[int, int]:
        r, c = super()._map_position(pos)
        return r, c + 1


class ColumnMajorOrder(GridLayoutInterface):
    """Simple utility mixin to index the grid in column-major order instead
    of row-major order."""

    @override
    def _map_position(self, pos: GridPosition) -> tuple[int, int]:
        r, c = super()._map_position(pos)
        return c, r


_ROW_LOOKUP = "ABCDEFGHJKLMNPRTUVWY"
_ROW_RADIX = len(_ROW_LOOKUP)


def to_bga_row_ref(row: int) -> str:
    """Convert a row number into a alpha row reference

    This function converts a zero-indexed row ordinal to a BGA-style alpha row
    reference string. The letters I, O, Q, S, X, and Z are skipped.

    For example:
      0   -> "A"
      1   -> "B"
      19  -> "Y"
      20  -> "AA"
      39  -> "AY"
      40  -> "BA"
      419 -> "YY"
      420 -> "AAA"
    """
    if row < 0:
        raise ValueError(f"Row index must be non-negative: {row}")
    ref = ""
    while row >= 0:
        rem = row % _ROW_RADIX
        row = row // _ROW_RADIX - 1
        ref += _ROW_LOOKUP[rem]
    return ref[::-1]


class AlphaDictNumberingBase(GridLayoutInterface):
    """Base class to provide a BGA-style alpha-numeric dictionary numbering
    scheme. The row is referred to by a letter as a member field, and the
    column is referred to by a number inside the dictionary at that field. No
    predefined rows are provided, and the intent is that this class is
    subclassed with declarations for all used rows. Note that the row letters
    skip the letters I, O, Q, S, X, and Z. If the exact rows are not
    known, then the :py:class:`~AlphaDictNumbering` class can be used instead to
    at least provide some type safety for the first 20 rows.

    >>> class My4RowNumbering(AlphaDictNumberingBase):
    ...     A: dict[int, Pad]
    ...     B: dict[int, Pad]
    ...     C: dict[int, Pad]
    ...     D: dict[int, Pad]
    """

    class _DictRefs(Ref):
        # keep track of dictionaries that needt beo cleaned up
        def __init__(self):
            self.dict: list[dict[int, Pad]] = []

    __dicts = _DictRefs()

    def _build(self):
        for d in self.__dicts.dict:
            for pad in d.values():
                Structurable._dispose(pad)
            d.clear()
        super()._build()

    @override
    def _assign_pad(self, r: int, c: int, pad: Pad):
        row = to_bga_row_ref(r)
        d = getattr(self, row, None)
        if d is None:
            d = {}
            setattr(self, row, d)
        d[c] = pad

    @override
    def _get_pad(self, r: int, c: int) -> Pad:
        row = to_bga_row_ref(r)
        d = getattr(self, row, None)
        if d is None:
            raise ValueError(f"Row {row} does not exist")
        return d[c]


class AlphaDictNumbering(AlphaDictNumberingBase):
    """Assign numbers to pads using an alpha-numeric dictionary. The row is
    referred to by a letter as a member field, and the column is referred to by
    a number inside the dictionary at that field. The row letters skip the
    letters I, O, Q, S, X, and Z. Note that the type checker is only aware of
    the first 20 rows, so will not provide type safety beyond that. From row 20
    each row will be referred to by two letters, row 20 will be referred to as
    "AA", row 21 as "AB", and so on.

    .. note::
        Only used rows will have their fields set, but please note that the type
        checker will not flag access to rows even though they may not be set at
        runtime, resulting in an attribute error. When in doubt, use
        :py:mod:`~jitx.inspect` functions instead.
    """

    A: dict[int, Pad]
    B: dict[int, Pad]
    C: dict[int, Pad]
    D: dict[int, Pad]
    E: dict[int, Pad]
    F: dict[int, Pad]
    G: dict[int, Pad]
    H: dict[int, Pad]
    J: dict[int, Pad]
    K: dict[int, Pad]
    L: dict[int, Pad]
    M: dict[int, Pad]
    N: dict[int, Pad]
    P: dict[int, Pad]
    R: dict[int, Pad]
    T: dict[int, Pad]
    U: dict[int, Pad]
    V: dict[int, Pad]
    W: dict[int, Pad]
    Y: dict[int, Pad]

    # tell the type checker that there may be dynamic attributes
    def __setattr__(self, name: str, value: Any) -> None:
        super().__setattr__(name, value)


class AlphaNumericNumberingBase(GridLayoutInterface):
    """Base class to provide a BGA-style alpha-numeric numbering
    scheme. Pads are referred by a unique name consisting of the row letter and
    a number.  It's advisable to create a subclass with declarations for all
    used pads. Note that the row letters skip the letters I, O, Q, S, X, and Z.
    The column indicies start at 0 unless offset using, for example,
    :py:class:`~A1`, and are not zero-padded.

    If pads are not known in advance, then introspection can be used to access
    pads with type safety, but without language server support. In this case
    it's recommended to use something like the
    :py:class:`~AlphaNumericNumbering` class instead.

    >>> class My9PadBGANumbering(AlphaNumericNumberingBase, A1):
    ...     A1: Pad
    ...     A2: Pad
    ...     A3: Pad
    ...     B1: Pad
    ...     B2: Pad
    ...     B3: Pad
    ...     C1: Pad
    ...     C2: Pad
    ...     C3: Pad
    """

    class _FieldRefs(Ref):
        # keep track of dictionaries that needt beo cleaned up
        def __init__(self):
            self.dict: list[dict[str, Pad]] = []

    __fields = _FieldRefs()

    def _build(self):
        for d in self.__fields.dict:
            for field, pad in d.items():
                setattr(self, field, None)
                Structurable._dispose(pad)
        super()._build()

    @override
    def _assign_pad(self, r: int, c: int, pad: Pad):
        row = to_bga_row_ref(r)
        field = f"{row}{c}"
        setattr(self, field, pad)

    @override
    def _get_pad(self, r: int, c: int) -> Pad:
        row = to_bga_row_ref(r)
        field = f"{row}{c}"
        d = getattr(self, field, None)
        if d is None:
            raise ValueError(f"Pad {field} does not exist")
        return d[c]


class LinearNumbering(GridLayoutInterface):
    """Assign numbers to pads using a linear numbering scheme, starting at pad
    number 1, accessed through ``p[1]``. Row and column indicies are ignored
    and pads are assigned in the generated order."""

    # yes, these are mutable, but will be reset before use
    p: dict[int, Pad] = {}
    __pad_positions: dict[tuple[int, int], int] = {}

    @override
    def _assign_pad(self, r: int, c: int, pad: Pad):
        idx = len(self.p) + 1
        self.p[idx] = pad
        self.__pad_positions[(r, c)] = idx

    @override
    def _get_pad(self, r: int, c: int) -> Pad:
        return self.p[self.__pad_positions[(r, c)]]

    @override
    def _build(self):
        for pad in self.p.values():
            Structurable._dispose(pad)
        self.p = {}
        self.__pad_positions = {}
        super()._build()


class GridLandpatternGenerator(LandpatternGenerator, GridLayoutInterface):
    pass
