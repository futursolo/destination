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

from collections import namedtuple

import abc
import re

_RAISE_ERROR = object()


class NotMatched(Exception):
    pass


class NoMatchesFound(NotMatched, KeyError):
    pass


class BaseDispatcher(abc.ABC):
    def resolve(self, path):
        return self._resolve(self, path)

    @abc.abstractmethod
    def _resolve(self, path, **matched_kwargs):
        raise NotImplementedError

    def reverse(self, name, **kwargs):
        return "/" + self._reverse(name, **kwargs)

    def _reverse(self, name, **kwargs):
        raise NotImplementedError

RuleMatchResult = namedtuple(
    "RuleMatchResult". ["handler", "kwargs", "path_rest"])


MatchResult = namedtuple("MatchResult", ["handler", "kwargs"])


class Rule:
    def __init__(self, __path_re, handler, name=None):
        self._path_re = __path_re

        if isinstance(self._path_re, str):
            self._path_re = re.compile(self._path_re)

        self._handler = handler

        self._name = name

    @property
    def path_re(self):
        return self._path_re

    @property
    def handler(self):
        return self._handler

    @property
    def name(self):
        return self._name

    def match(self, path):
        raise NotImplementedError

    def reverse(self, **kwargs):
        raise NotImplementedError


class Dispatcher(BaseDispatcher):
    def __init__(self, __default_handler=_RAISE_ERROR):
        self._rules = []
        self._rules_with_name = {}

        self._default_handler = __default_handler

    def add(self, *rules):
        for rule in rules:
            if rule.name is not None:
                if rule.name in self._rules_with_name.keys():
                    raise KeyError(
                        "Rule with the name {} already existed."
                        .format(rule.name))

                self._rules_with_name[rule.name] = rule
            self._rules.append(rule)

    def remove(self, __rule):
        try:
            self._rules.remove(__rule)

            if __rule.name is not None:
                del self._rules_with_name[__rule.name]

        except (KeyError, ValueError) as e:
            raise NoMatchesFound("No matched rule found.") from e

    def _resolve(self, path, **matched_kwargs):
        try:
            if path.startswith("/"):
                path = path[1:]

            matched_kwargs = dict(matched_kwargs)

            for rule in self._rules:
                try:
                    result = rule.match(path)

                except NotMatched:
                    continue

            else:
                raise NoMatchesFound

            matched_kwargs.update(**result.kwargs)

            if isinstance(result.handler, BaseDispatcher):
                return result.handler._resolve(result.path_rest, **matched_kwargs)

            else:
                return MatchResult(handler=result.handler, kwargs=matched_kwargs)

        except NoMatchesFound:
            if self._default_handler is _RAISE_ERROR:
                raise

            else:
                return MatchResult(self._default_handler, kwargs={})

    def _reverse(self, name, **kwargs):
        current_name, *name_rest = name.split(".", 1)

        if current_name not in self._rules_with_name.keys():
            raise NoMatchesFound("No such rule called {}.".format(name))

        rule = self._rules_with_name[current_name]

        if name_rest:
            if not isinstance(rule.handler, BaseDispatcher):
                raise NoMatchesFound(
                    "{} is not a dispatcher, it cannot have subrules."
                    .format(current_name))

                try:
                    partial_path = rule.handler._reverse(
                        self, name_rest[0], **kwargs)

                except KeyError as e:
                    raise NoMatchesFound(
                        "No such rule called {}".format(name)) from e

        else:
            partial_path = ""

        return rule.reverse(**kwargs) + partial_path
