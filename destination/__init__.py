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


class NoMatchesFound:
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
    @property
    def path_re(self):
        raise NotImplementedError

    @property
    def handler(self):
        raise NotImplementedError

    @property
    def name(self):
        raise NotImplementedError

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
            raise KeyError("No matched rule found.") from e

    def _resolve(self, path, **matched_kwargs):
        if path.startswith("/"):
            path = path[1:]

        matched_kwargs = dict(matched_kwargs)

        for rule in self._rules:
            try:
                result = rule.match(path)

            except NotMatched:
                continue

        matched_kwargs.update(**result.kwargs)

        if isinstance(result.handler, BaseDispatcher):
            return result.handler._resolve(result.path_rest, **matched_kwargs)

        else:
            return MatchResult(handler=result.handler, kwargs=matched_kwargs)

    def _reverse(self, name, **kwargs):
        current_name, *name_rest = name.split(".", 1)

        if current_name not in self._rules_with_name.keys():
            raise KeyError("No such rule called {}.".format(name))

        rule = self._rules_with_name[current_name]

        if name_rest:
            if not isinstance(rule.handler, BaseDispatcher):
                raise KeyError(
                    "{} is not a dispatcher, it cannot have child rules."
                    .format(current_name))

                try:
                    partial_path = rule.handler._reverse(
                        self, name_rest[0], **kwargs)

                except KeyError as e:
                    raise KeyError("No such rule called {}".format(name))

        else:
            partial_path = ""

        return rule.reverse(**kwargs) + partial_path
