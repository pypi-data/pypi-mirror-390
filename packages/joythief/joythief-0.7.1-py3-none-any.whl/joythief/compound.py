import typing as tp
import warnings
from abc import ABC

from .core import Matcher

T = tp.TypeVar("T")


class PointlessCompound(UserWarning):
    """Emitted if you create a compound matcher with a single child matcher."""

    MESSAGE: tp.ClassVar[str] = (
        "a compound matcher with a single child matcher can be trivially replaced by that child"
    )


class ZeroMatchers(TypeError):
    """Thrown if you try to create a compound matcher with no child matchers."""

    MESSAGE: tp.ClassVar[str] = "compound matchers require at least one child matcher"

    def __init__(self) -> None:
        super().__init__(self.MESSAGE)


class _Compound(Matcher[T], tp.Generic[T], ABC):

    _matchers: tuple[Matcher[T], ...]

    def __init__(self, *matchers: Matcher[T]):
        if not matchers:
            raise ZeroMatchers
        if len(matchers) == 1:
            warnings.warn(PointlessCompound.MESSAGE, PointlessCompound, stacklevel=2)
        super().__init__()
        self._matchers = matchers

    def represent(self) -> str:
        return f"{type(self).__name__}({', '.join(repr(m) for m in self._matchers)})"


class AllOf(_Compound[T]):
    """Matches values which match all of the child matchers.

    .. note:: Unlike :py:func:`all` this comparison is not lazy; all matchers
        are compared, whether or not any are unequal.
    """

    def compare(self, other: tp.Any) -> bool:
        equal: bool = True
        for matcher in self._matchers:
            if matcher != other:
                equal = False
        return equal


class AnyOf(_Compound[T]):
    """Matches values which match any of the child matchers.

    .. note:: Unlike :py:func:`any` this comparison is not lazy; all matchers
        are compared, whether or not any are equal.
    """

    def compare(self, other: tp.Any) -> bool:
        equal: bool = False
        for matcher in self._matchers:
            if matcher == other:
                equal = True
        return equal
