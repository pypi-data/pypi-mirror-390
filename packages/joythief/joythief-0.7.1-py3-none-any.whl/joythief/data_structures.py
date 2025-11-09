import typing as tp
from collections.abc import Hashable, Mapping

from .core import Matcher


class DictContaining(Matcher[Mapping[Hashable, tp.Any]], dict[Hashable, tp.Any]):
    """Match the specified keys in a mapping, ignoring any extra keys.


    :param \\*args: sequence of key-value pairs to include in the comparison

    :param \\**kwargs: mapping of key-value pairs to include in the comparison

    :raises ValueError: if no keys are specified (use
        :py:class:`~joythief.objects.InstanceOf` with :py:class:`dict` instead).

    .. code-block:: python

        assert (
            actual
            == DictContaining([("foo", 123), ("bar", 456)], baz=InstanceOf(int)
        )

    **Note**: this subclasses :py:class:`dict` so that ``pytest`` will show the
    common and differing items, e.g.:

    .. code-block:: python

        >       assert mapping == dict(foo=123, bar=456)
        E       AssertionError: assert DictContaining(**{'foo': 123, 'bar': 0, 'baz': 789}) == {'foo': 123, 'bar': 456}
        E
        E         Common items:
        E         {'foo': 123}
        E         Differing items:
        E         {'bar': 0} != {'bar': 456}
        E         Left contains 1 more item:
        E         {'baz': 789}
        # ...

    """

    def __init__(self, *args: tp.Any, **kwargs: tp.Any) -> None:
        if not args and not kwargs:
            raise ValueError("an empty DictContaining matches any mapping")
        super().__init__(*args, **kwargs)

    def compare(self, other: tp.Any) -> bool:
        if not isinstance(other, Mapping):
            return self.not_implemented
        is_equal: bool = True
        for key in self:
            if key not in other or self[key] != other[key]:
                is_equal = False
        return is_equal

    def represent(self) -> str:
        return f"DictContaining(**{dict.__repr__(self)})"
