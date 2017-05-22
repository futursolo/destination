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


class BaseDispatcher(abc.ABC):
    def resolve(self, path):
        return self._resolve(self, path)

    @abc.abstractmethod
    def _resolve(self, path, *matched_args, **matched_kwargs):
        raise NotImplementedError

    def reverse(self, name, *args, **kwargs):
        raise NotImplementedError


Rule = nametuple('Rule', ["path_re", "handler", "name"])


class Dispatcher(BaseDispatcher):
    def __init__(self, __DefaultHandler=_RAISE_ERROR):
        self._rules = []
        self._name_dict = {}

        self._DefaultHandler = __DefaultHandler

    def add(self, *rules):
        for rule in rules:
            if rule.name is not None:
                if rule.name in self._name_dict.keys():
                    raise KeyError(
                        "Rule with the name {} already existed."
                        .format(rule.name))

                self._name_dict[rule.name] = rule
            self._rules.append(rule)

    def remove(self, __rule):
        if isinstance(name_or_path_re, re._pattern_type):
            try:
                self._rules.remove(__rule)

                if __rule.name is not None:
                    del self._name_dict[__rule.name]

            except KeyError as e:
                raise KeyError("No matched rule found.") from e
