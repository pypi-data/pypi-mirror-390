"""The JITX Standard Library Landpattern Generator Framework.

This package contains a framework for generating various component
landpatterns. It is provided through the ``jitxlib-standard`` library.

The framework is designed to generated the landpattern whenever an element of
the landpattern is referenced, including during introspection. This allows the
landpattern to be up to date with any changes to the design tree, but this
comes with the caveat that the landpattern may yield different results
depending on when it's inspected, as well as the fact that the landpattern may
be generated multiple times which may be relevant if the landpattern is
expensive to generate.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import ClassVar, Self, TYPE_CHECKING, cast, overload

from jitx.container import Composite, Ref
from jitx.context import Context
from jitx.feature import Feature
from jitx.inspect import extract, visit
from jitx.landpattern import Landpattern, Pad, PadShape
from jitx.memo import dememoize
from jitx.placement import Positionable
from jitx.shapes import Shape
from jitx.shapes.composites import Bounds, bounds_union
from jitx.transform import IDENTITY, Transform
from jitx._structural import Structurable
import jitx


type GeometrySource = Composite | Positionable


class ApplyToMixin:
    class _GeometrySourceRef(Ref):
        def __init__(self, target: Iterable[GeometrySource]):
            self.objects = target

    __target: _GeometrySourceRef | None = None

    @overload
    def apply_to(self, *target: GeometrySource) -> Self: ...
    @overload
    def apply_to(self, target: Iterable[GeometrySource]) -> Self: ...

    def apply_to(
        self,
        target: GeometrySource | Iterable[GeometrySource],
        *additional: GeometrySource,
    ):
        """Apply the generator to a target object or objects that is not this
        object itself. Note that this only affects what the generator looks at,
        the output will still be stored in this object. This is useful when
        making composite landpatterns, and you need a separate object to
        generate information based on other objects in the landpattern. For
        example, if composing a landpattern where a stand-alone silkscreen
        outline generator is desired, the generator can be instantiated
        separately and this method is then used to designate the object(s) to
        which the generator applies. It's not advisable to call this method on
        a non-composite landpattern.  If this method is not called, the
        generators will introspect the object itself (including child-objects),
        which is typically what is desired for standard use cases.

        Args:
            target: the object(s) to which the generator applies, can be
                supplied as an iterable or as varargs.

        Returns:
            self for method chaining
        """
        if isinstance(target, Iterable):
            target = tuple(target) + additional
        else:
            target = (target,) + additional
        self.__target = self._GeometrySourceRef(target)
        return self

    def _applies_to_objects[T](self, types: type[T]) -> Iterable[T]:
        if self.__target is None:
            target = (self,)
        else:
            target = self.__target.objects
        for ob in target:
            yield from extract(ob, types)

    def _applies_to_transformed_objects[T](
        self, types: type[T] | tuple[type[T], ...]
    ) -> Iterable[tuple[Transform, T]]:
        if self.__target is None:
            target = (self,)
            inv = IDENTITY
        else:
            target = self.__target.objects
            if isinstance(self, Positionable | Composite) and self.transform:
                inv = self.transform.inverse()
            else:
                inv = IDENTITY

        def xform(source: GeometrySource | Self) -> Transform:
            if source is self:
                # don't transform with self.transform, objects are already relative to self.
                # there also won't be a relevant inverse (it's set to IDENTITY above)
                return IDENTITY
            if isinstance(source, Positionable | Composite) and source.transform:
                return inv * source.transform
            return inv

        return (
            # transform should never be unset here really
            (trace.transform or IDENTITY, found)
            for ob in target
            for trace, found in visit(ob, types, transform=xform(ob))
        )

    def _applies_to_shapes[T: Feature | Pad](
        self, types: type[T] | tuple[type[T], ...]
    ) -> Iterable[Shape]:
        for xform, feat in self._applies_to_transformed_objects(types):
            if isinstance(feat, Pad):
                if isinstance(feat.shape, PadShape):
                    yield xform * feat.shape.shape
                else:
                    yield xform * feat.shape
            else:
                yield xform * feat.shape

    def _applies_to_bounds[T: Feature | Pad](
        self, types: type[T] | tuple[type[T], ...], additional: Shape | None = None
    ) -> Bounds:
        bounds = bounds_union(
            shape.to_shapely().bounds for shape in self._applies_to_shapes(types)
        )
        if additional is not None:
            bounds = bounds_union((bounds, additional.to_shapely().bounds))
        return bounds


class _LineWidthDefault:
    @property
    def line_width(self) -> float:
        return jitx.current.substrate.constraints.min_silkscreen_width


@dataclass(frozen=True)
class LineWidthContext(Context):
    _global_default: ClassVar[_LineWidthDefault] = _LineWidthDefault()
    line_width: float

    @classmethod
    def get(cls) -> LineWidthContext:
        """Get the current line width context, if unset it defaults to the
        minimum silkscreen width in the substrate constraints."""
        # pretend it's a context even though it's practically mutable, the
        # lookup on the substrate will still make the correct context based
        # memoization.
        return super().get() or cast(LineWidthContext, cls._global_default)


class LineWidthMixin(Structurable):
    __line_width: float | None = None
    __line_width_ctx: float

    if not TYPE_CHECKING:
        # This is removed from type checking to keep pyright from infering that
        # the signature for the class is *args, **kwargs, since this init
        # function is only here to help initialize the mixin. The code is still
        # reachable and executed at runtime.
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.__line_width_ctx = LineWidthContext.get().line_width

    def line_width(self, line_width: float) -> Self:
        """Set the line width to use for the generator. If not set, the
        current value from the design context will be used.

        Args:
            line_width: the line width to use

        Returns:
            self for method chaining
        """
        self.__line_width = line_width
        return self

    @property
    def _line_width(self) -> float:
        return self.__line_width or self.__line_width_ctx


@dataclass(frozen=True)
class SoldermaskRegistrationContext(Context):
    _global_default: ClassVar[SoldermaskRegistrationContext]
    soldermask_registration: float

    @classmethod
    def get(cls) -> SoldermaskRegistrationContext:
        return super().get() or SoldermaskRegistrationContext._global_default


SoldermaskRegistrationContext._global_default = SoldermaskRegistrationContext(0.1)


class LandpatternProvider:
    """Base mixin class for landpattern generators that produce elements for the
    landpattern."""

    def _build(self):
        """Build the landpattern. Mixins should override this method and ensure
        to call ``super()._build()`` to make sure the mro is traversed and all
        mixins are called.

        This method will be called repeatedly whenever the landpattern is
        invalidated, it's advisable to do any cleanups before calling
        ``super()._build()`` and generator logic afterwards. This is to ensure
        that other generators will get a consistent state when introspecting,
        that does not depend on the number of times the landpattern has been
        rebuilt.

        ... note: Do not call this method directly. It will likely trigger a
                build recursion."""
        self.__build_chained = True

    def _build_decorate(self):
        """Decorate the landpattern. This is called after :py:meth:`_build`,
        allowing the implementation to be sure all :py:meth:`_build`
        construction has been completed, which typically includes all pads.

        Mixins that override this method must call
        ``super()._build_decorate()`` to make sure the mro is traversed and all
        mixins are called.

        It's advisable to also implement the :py:meth:`_build` method just to
        do cleanups, as outlined in the :py:meth:`_build` documentation.

        ... note: Do not call this method directly. It will likely trigger a
                build recursion."""
        self.__build_chained = True

    __invalid = True
    __building = False
    __build_chained = False

    def __build(self):
        if self.__building:
            raise RuntimeError("Reentrant call to _build")
        self.__building = True
        try:
            self.__build_chained = False
            self._build()
            if not self.__build_chained:
                raise RuntimeError(
                    "Build chain interrupted, likely due to a missing call to super()._build()"
                )
            self.__build_chained = False
            self._build_decorate()
            if not self.__build_chained:
                raise RuntimeError(
                    "Build chain interrupted, likely due to a missing call to super()._decorate()"
                )
            self.__invalid = False
        finally:
            self.__building = False

    def __ensure_valid(self):
        # considered valid while building to prevent infinite recursion, thus
        # introspection _during_ building could get an incomplete state.
        if self.__invalid and not self.__building:
            self.__build()

    def rebuild(self, force: bool = False):
        """Trigger a rebuild of the landpattern. Normally this is not necessary,
        as the landpattern is built on demand. However, if it appears that the
        landpattern fails to detect a change, or if it needs to be built at a
        specific time, this method can be called to force a rebuild."""
        if force:
            self.invalidate()
        self.__ensure_valid()

    def invalidate(self):
        """Invalidate the landpattern. This is useful if the landpattern is
        invalidated by a change to a parameter."""
        self.__invalid = True

    # trigger build here, but need to be careful since this call needs to
    # get attributes to check if a build is needed.
    if not TYPE_CHECKING:
        # This is a runtime-only check, so pretend it does not exist while type
        # checking. Otherwise pyright infers that _any_ attribute is possible.
        # For some reason pyright flags this code as unreachable, which is
        # backwards (TYPE_CHECKING is always False at runtime).
        def __getattribute__(self, name):
            import sys

            exc_type, _exc_value, _exc_traceback = sys.exc_info()
            # don't trigger during exception handling
            if (
                name[0] != "_"
                and not exc_type
                and not isinstance(getattr(self.__class__, name, None), Callable)
            ):
                self.__ensure_valid()
            return super().__getattribute__(name)

        def __setattr__(self, name, value):
            if name != "_LandpatternProvider__invalid" and not self.__building:
                self.invalidate()
            object.__setattr__(self, name, value)

    def __dir__(self):
        # called during introspection, use it to trigger a build
        self.__ensure_valid()
        return super().__dir__()


@dememoize
class LandpatternGenerator(Landpattern, LandpatternProvider):
    __init = False

    def __init__(self):
        super().__init__()
        self.__base_init__()
        if not self.__init:
            raise RuntimeError(
                "Landpattern initialization chain interrupted, likely due to a missing call to super().__base_init__()"
            )

    def _build(self):
        if not self.__init:
            raise RuntimeError(
                "Landpattern build chain has not been initialized, likely due to a missing call to super().__init__()"
            )
        return super()._build()

    def __base_init__(self):
        """Called by the :py:class:`LandpatternGenerator` base class
        initializer to allow mixins to initialize themselves without having to
        override the constructor and interfering with landpattern constructor
        arguments."""
        self.__init = True
