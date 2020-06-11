#!/usr/bin/env python3
# MIT License
#
# Copyright (c) 2020 Kaede Hoshikawa
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# allcopies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from typing import Dict, Pattern, List, Tuple, Optional, Union, \
    TypeVar, Generic

from ._version import __version__

import abc
import re
import typing

__all__ = [
    "__version__", "InvalidName", "NotMatched", "NoMatchesFound",
    "ReverseError", "NonReversible", "ResolvedPath", "BaseRule",
    "BaseDispatcher", "ReRule", "Dispatcher", "ReSubDispatcher"]


class _RaiseError:
    pass


_RAISE_ERROR = _RaiseError()

_V = TypeVar("_V")


class InvalidName(ValueError):
    """
    This is raised when an invalid name is provided to identify the rule.

    Acceptable Name: :code:`^[a-zA-Z]([a-zA-Z0-9\\_]+)?$`
    """
    pass


class NotMatched(Exception):
    """
    This is raised when the path provided cannot be parsed with the current
    rule.
    """
    pass


class NoMatchesFound(NotMatched, KeyError):
    """
    This is raised when the path provided cannot be resolved by any rules in
    the current dispatcher.
    """
    pass


class ReverseError(Exception):
    """
    This is raised when error occurs during the reversion.
    """
    pass


class NonReversible(ReverseError):
    """
    This is raised when the rule is not reversible.
    """
    pass


class ResolvedPath(Generic[_V]):
    """
    The object returned upon successfully parsing the path.
    """

    def __init__(self, identifier: _V, kwargs: Dict[str, str]) -> None:
        self._identifier = identifier
        self.kwargs = kwargs

    @property
    def identifier(self) -> _V:
        return self._identifier


class BaseRule(Generic[_V]):
    """
    This class defines a series of methods and properties that a rule
    should implement. A dispatcher may only instances of the subclasses of
    this class.
    """
    @property
    @abc.abstractmethod
    def identifier(self) -> _V:  # pragma: no cover
        """
        The identifier of the rule.

        This can be used to help the user to decide the handling process
        after the path being successfully parsed.

        Default: :code:`self` (the current instance of the rule).
        """
        raise NotImplementedError

    @abc.abstractmethod
    def parse(self, __path: str) -> ResolvedPath[_V]:  # pragma: no cover
        """
        Parse the path.

        Upon successful parsing, a :code:`ResolvedPath` is returned, which
        contains the information of the path.

        If the path cannot be parsed with the current rule, a
        :code:`NotMatched` is raised.
        """
        raise NotImplementedError

    def compose(
        self, __name: Optional[str],
            **kwargs: str) -> str:  # pragma: no cover
        """
        Compose the path with the arguments provided.

        If a name is provided and the rule is not subscriptable or the
        corresponding rule not found, a KeyError should be raised.

        .. note::

           Reversion is not mandatory to be implemented.
        """
        raise NotImplementedError("Reversing is not supported.")


class BaseDispatcher(Generic[_V]):
    """
    This class establishes a series of methods and propeties that a
    dispatcher should implement and provides helper method to simplify
    the implemenation process.
    """
    _name_re = re.compile(r"^[a-zA-Z]([a-zA-Z0-9\_]+)?$")

    def _check_name(self, __name: str) -> None:
        """
        Check if a name is valid to be registered to identify a rule.
        In case of an invalid name is provided, an `InvalidName` exception is
        raised.

        Acceptable Name: :code:`^[a-zA-Z]([a-zA-Z0-9\\_]+)?$`
        """
        if re.fullmatch(self._name_re, __name) is None:
            raise InvalidName("{} is not a valid name.".format(__name))

    def _split_name(self, __name: str) -> Tuple[str, Optional[str]]:
        """
        Split the name into two parts. This returns a tuple, contains the
        current name and the rest of the name that may be used for further
        subscription.
        """
        current_name, *name_rest = __name.split(".", 1)

        rest_name = name_rest[0] if name_rest else None

        return current_name, rest_name

    def resolve(self, __path: str) -> ResolvedPath[_V]:
        """
        Iterates over the rules stored to try to find a rule that can
        successfully parse the current path.

        A :code:`NoMatchesFound` exception is raised when the path provided
        cannot be parsed with any rule in the dispatcher.
        """
        if __path.startswith("/"):
            __path = __path[1:]

        return self._resolve(__path)

    @abc.abstractmethod
    def _resolve(self, __path: str, **kwargs: str) -> \
            ResolvedPath[_V]:  # pragma: no cover
        """
        The Implementation of path resolution, override this method to
        implement the path resolution.

        .. important::

            The keyword arguments should be added into the result of the
            resolved path; however, the arguments found in further resolution
            have a higher priority and should override the value with the same
            name in the values provided.
        """
        raise NotImplementedError

    def reverse(self, __name: str, **kwargs: str) -> str:
        """
        Try to compose the rule with the name into a path with the provided
        keyword arguments.
        """
        return "/" + self._reverse(__name, **kwargs)

    def _reverse(self, __name: str, **kwargs: str) -> str:  # pragma: no cover
        """
        The implementation of the path reversion, override this method to
        implement the path reversion.

        .. note::

           Reversion is not mandatory to be implemented.
        """
        raise NotImplementedError("Reversing is not supported.")


class _ReMatchGroup:
    """
    Represent a match group from a regular expression.
    """
    _named_group_re = re.compile(r"^\?P<(.*)>(.*)$")

    def __init__(self, __group_str: str) -> None:
        matched = self._named_group_re.fullmatch(__group_str)

        if matched:
            self._name, pattern = matched.groups()

            self._pattern = re.compile(pattern)

        else:
            raise NonReversible("Non-named Groups are not Reversible.")

    @property
    def name(self) -> str:
        return self._name

    @property
    def pattern(self) -> Pattern[str]:
        return self._pattern


class ReRule(BaseRule[_V], Generic[_V]):
    """
    This class is an implementation of :code:`BaseRule` that uses regular
    expressions to parse the path.
    """
    _TReRule = TypeVar("_TReRule", bound="ReRule[_V]")

    _unescaped_pattern = re.compile(
        r"([^\\]|^)([\.\^\$\*\+\?\{\[\|]|\\[0-9AbBdDsSwWZuU])")

    _escaped_pattern = re.compile(
        r"\\([\.\^\$\*\+\?\{\[\(\|]|\\[0-9AbBdDsSwWZuU])")

    @typing.overload
    def __init__(
        self: "ReRule[_TReRule]",
            __path_re: Union[str, Pattern[str]]) -> None:
        ...

    @typing.overload
    def __init__(
        self, __path_re: Union[str, Pattern[str]],
            identifier: _V) -> None:
        ...

    def __init__(
        self, __path_re: Union[str, Pattern[str]],
            identifier: Optional[_V] = None) -> None:
        self._path_re = re.compile(__path_re)

        if not self._path_re.pattern.startswith("^"):
            raise ValueError(
                "A path pattern must match from the beginning.")

        self._identifier = identifier or self  # type: _V  # type: ignore

        if not self._path_re.pattern.endswith("$") and \
                not isinstance(self, BaseDispatcher):
            raise ValueError(
                "This path pattern is not instintated "
                "with a subclass of BaseDispatcher; hence, the pattern must "
                "match the end.")

    @property
    def identifier(self) -> _V:
        return self._identifier

    def parse(self, __path: str) -> ResolvedPath[_V]:
        parsed = self._path_re.match(__path)

        if parsed is None:
            raise NotMatched("The path does not match the rule.")

        return ResolvedPath(
            identifier=self._identifier,
            kwargs=dict(parsed.groupdict()))

    def _justify_pattern_frag(self, pattern_frag: str) -> str:
        if self._unescaped_pattern.search(pattern_frag):
            raise NonReversible("Pattern outside brackets.")

        unescaped_pattern_frag = []

        pos = 0

        for matched in self._escaped_pattern.finditer(pattern_frag):
            start_pos, end_pos = pos, matched.start()

            unescaped_pattern_frag.append(pattern_frag[start_pos:end_pos])

            pos = end_pos + 1

        unescaped_pattern_frag.append(pattern_frag[pos:])

        return "".join(unescaped_pattern_frag)

    @property
    def _reverse_groups(self) -> List[Union[str, _ReMatchGroup]]:
        if not hasattr(self, "_cached_reverse_groups"):
            groups = []  # type: List[Union[str, _ReMatchGroup]]

            rest_pattern_str = self._path_re.pattern

            if rest_pattern_str.startswith("^"):
                rest_pattern_str = rest_pattern_str[1:]

            if rest_pattern_str.endswith("$"):
                rest_pattern_str = rest_pattern_str[:-1]

            while True:
                begin_pos = rest_pattern_str.find("(")

                if begin_pos == -1:  # No more groups.
                    groups.append(self._justify_pattern_frag(rest_pattern_str))
                    rest_pattern_str = ""
                    break

                groups.append(
                    self._justify_pattern_frag(rest_pattern_str[:begin_pos]))

                rest_pattern_str = rest_pattern_str[begin_pos + 1:]

                end_pos = rest_pattern_str.find(")")
                groups.append(_ReMatchGroup(rest_pattern_str[:end_pos]))

                rest_pattern_str = rest_pattern_str[end_pos + 1:]

            self._cached_reverse_groups = groups

        return self._cached_reverse_groups

    def compose(self, __name: Optional[str], **kwargs: str) -> str:
        if __name is not None:
            raise TypeError("A ReRule is not subscriptable.")

        result = []

        for group in self._reverse_groups:
            if isinstance(group, str):
                result.append(group)

            elif group.pattern.fullmatch(kwargs[group.name]) is None:
                raise ReverseError(
                    "The content to be filled into the "
                    "pattern is not valid.")

            else:
                result.append(kwargs[group.name])

        return "".join(result)


class Dispatcher(BaseDispatcher[_V], Generic[_V]):
    """
    This class is an implementation of :code:`BaseDispatcher` that is
    compatible with :code:`BaseRule`. Before :code:`Dispatcher.resolve()`
    is invoked, rules should be added using :code:`Dispatcher.add()`.
    """

    def __init__(self) -> None:
        self._rules = []  # type: List[BaseRule[_V]]
        self._rules_with_name = {}  # type: Dict[str, BaseRule[_V]]

    def add(self, rule: BaseRule[_V], *, name: Optional[str] = None) -> None:
        """
        Add a :code:`BaseRule` to the :code:`Dispatcher`.

        If a name is provided and the rule is reversible, then it can be
        reversed by `Dispatcher.reverse()` using the name.
        """
        assert isinstance(rule, BaseRule), \
            ("You can only add instances of the subclasses of BaseRule "
             "to this dispatcher")
        if name is not None:
            if name in self._rules_with_name.keys():
                raise KeyError(
                    "Rule with the name {} already existed."
                    .format(name))

            self._check_name(name)
            self._rules_with_name[name] = rule
        self._rules.append(rule)

    def remove(self, __rule: BaseRule[_V]) -> None:
        """
        Remove a rule from the dispatcher.
        """
        try:
            self._rules.remove(__rule)

            if __rule not in self._rules_with_name.values():
                return

            self._rules_with_name = \
                {k: v for k, v in self._rules_with_name.items() if v != __rule}

        except (KeyError, ValueError) as e:
            raise NoMatchesFound("No matched rule found.") from e

    def _resolve(self, __path: str, **matched_kwargs: str) -> ResolvedPath[_V]:
        for rule in self._rules:
            try:
                result = rule.parse(__path)

            except NotMatched:
                continue

            else:
                break

        else:
            raise NoMatchesFound

        matched_kwargs = dict(matched_kwargs)
        matched_kwargs.update(result.kwargs)

        return ResolvedPath(
            identifier=result.identifier, kwargs=matched_kwargs)

    def _reverse(self, __name: str, **kwargs: str) -> str:
        current_name, rest_name = self._split_name(__name)

        try:
            rule = self._rules_with_name[current_name]
            return rule.compose(rest_name, **kwargs)

        except (KeyError, ValueError, TypeError) as e:
            raise KeyError(
                "No such rule called {}.".format(__name)) from e


class ReSubDispatcher(Dispatcher[_V], ReRule[_V], Generic[_V]):
    """
    A implementation of :code:`BaseDispatcher` and :code:`BaseRule` using
    :code:`Dispatcher` and :code:`ReRule`. This class is used to further
    parsing the url by shaving off the matched fragment.
    """

    def __init__(
            self, __path_re: str, identifier: Optional[_V] = None) -> None:
        ReRule.__init__(self, __path_re, identifier)  # type: ignore
        Dispatcher.__init__(self)

    def parse(self, __path: str) -> ResolvedPath[_V]:
        parsed = self._path_re.match(__path)

        if parsed is None:
            raise NotMatched("The path does not match the rule.")

        return self._resolve(
            __path[parsed.span()[1]:], **parsed.groupdict())

    def compose(self, __name: Optional[str], **kwargs: str) -> str:
        if __name is None:
            raise ValueError(
                "A ReSubDispatcher is not revisible on its own, "
                "please provide a subrule name.")

        result = []

        for group in self._reverse_groups:
            if isinstance(group, str):
                result.append(group)

            elif group.pattern.fullmatch(kwargs[group.name]) is None:
                raise ReverseError(
                    "The content to be filled into the "
                    "pattern is not valid.")

            else:
                result.append(kwargs[group.name])

        partial_path = "".join(result)

        return partial_path + self._reverse(__name, **kwargs)
