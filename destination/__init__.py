#!/usr/bin/env python3
# MIT License
#
# Copyright (c) 2017 Kaede Hoshikawa
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

from typing import Any, NamedTuple, Dict, Pattern, List, Tuple, Optional, Union

from ._version import __version__

import abc
import re

__all__ = [
    "__version__", "InvalidName", "NotMatched", "NoMatchesFound",
    "ReverseError", "NonReversible", "ResolvedPath", "BaseRule",
    "BaseDispatcher", "ReRule", "Dispatcher", "ReSubDispatcher"]

_RAISE_ERROR = object()


class InvalidName(ValueError):
    pass


class NotMatched(Exception):
    pass


class NoMatchesFound(NotMatched, KeyError):
    pass


class ReverseError(Exception):
    pass


class NonReversible(ReverseError):
    pass


ResolvedPath = NamedTuple(
    'ResolvedPath', [('identifier', Any), ('kwargs', Dict[str, str])])


class BaseRule(abc.ABC):
    @property
    @abc.abstractmethod
    def identifier(self) -> Any:
        raise NotImplementedError

    @abc.abstractmethod
    def parse(self, __path: str) -> ResolvedPath:
        raise NotImplementedError

    def compose(self, __name: Optional[str], **kwargs: str) -> str:
        raise NotImplementedError("Reversing is not supported.")


class BaseDispatcher(abc.ABC):
    _name_re = re.compile(r"^[a-zA-Z]([a-zA-Z0-9\_]+)?$")

    def _check_name(self, __name: str) -> None:
        if re.fullmatch(self._name_re, __name) is None:
            raise InvalidName("{} is not a valid name.".format(__name))

    def resolve(self, __path: str) -> ResolvedPath:
        if __path.startswith("/"):
            __path = __path[1:]

        return self._resolve(__path)

    @abc.abstractmethod
    def _resolve(self, __path: str, **kwargs: str) -> ResolvedPath:
        raise NotImplementedError

    def _split_name(self, __name: str) -> Tuple[str, Optional[str]]:
        current_name, *name_rest = __name.split(".", 1)

        rest_name = name_rest[0] if name_rest else None

        return current_name, rest_name

    def reverse(self, __name: str, **kwargs: str) -> str:
        return "/" + self._reverse(__name, **kwargs)

    def _reverse(self, __name: str, **kwargs: str) -> str:
        raise NotImplementedError("Reversing is not supported.")


class _ReMatchGroup:
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
    def pattern(self) -> Pattern:
        return self._pattern


class ReRule(BaseRule):
    _unescaped_pattern = re.compile(
        r"([^\\]|^)([\.\^\$\*\+\?\{\[\|]|\\[0-9AbBdDsSwWZuU])")

    _escaped_pattern = re.compile(
        r"\\([\.\^\$\*\+\?\{\[\(\|]|\\[0-9AbBdDsSwWZuU])")

    def __init__(
        self, __path_re: Union[str, Pattern[str]],
            identifier: Any=None) -> None:
        if isinstance(__path_re, str):
            self._path_re = re.compile(__path_re)

        else:
            self._path_re = __path_re

        if not self._path_re.pattern.startswith("^"):
            raise ValueError(
                "A path pattern must match from the beginning.")

        self._identifier = identifier or self

        if not self._path_re.pattern.endswith("$") and \
                not isinstance(self, BaseDispatcher):
            raise ValueError(
                "This path pattern is not instintated "
                "with a subclass of BaseDispatcher; hence, the pattern must "
                "match the end.")

    @property
    def identifier(self) -> Any:
        return self._identifier

    def parse(self, __path: str) -> ResolvedPath:
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


class Dispatcher(BaseDispatcher):
    def __init__(self) -> None:
        self._rules = []  # type: List[BaseRule]
        self._rules_with_name = {}  # type: Dict[str, BaseRule]

    def add(self, rule: BaseRule, *, name: Optional[str]=None) -> None:
        if name is not None:
            if name in self._rules_with_name.keys():
                raise KeyError(
                    "Rule with the name {} already existed."
                    .format(name))

            self._check_name(name)
            self._rules_with_name[name] = rule
        self._rules.append(rule)

    def remove(self, __rule: BaseRule) -> None:
        try:
            self._rules.remove(__rule)

            if __rule not in self._rules_with_name.values():
                return

            self._rules_with_name = \
                {k: v for k, v in self._rules_with_name.items() if v != __rule}

        except (KeyError, ValueError) as e:
            raise NoMatchesFound("No matched rule found.") from e

    def _resolve(self, __path: str, **matched_kwargs: str) -> ResolvedPath:
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
            raise NoMatchesFound(
                "No such rule called {}.".format(__name)) from e


class ReSubDispatcher(Dispatcher, ReRule):
    def __init__(self, __path_re: str, identifier: Any=None) -> None:
        ReRule.__init__(self, __path_re, identifier)
        Dispatcher.__init__(self)

    def parse(self, __path: str) -> ResolvedPath:
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
