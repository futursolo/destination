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

from destination import ReRule, Dispatcher, ReSubDispatcher, NotMatched

import pytest


class ReRuleTestCase:
    def test_parse(self):
        rule_a = ReRule(r"^(?P<filename>.*)$")

        resolved = rule_a.parse("test.htm")

        assert resolved.identifier == rule_a

        assert resolved.kwargs["filename"] == "test.htm"

    def test_not_matched(self):
        rule_a = ReRule(r"^(?P<filename>[0-9]+)\.jpg$")

        with pytest.raises(NotMatched):
            rule_a.parse("test.png")

    def test_compose(self):
        rule_a = ReRule(r"^(?P<filename>[0-9]+)\.jpg$")

        assert rule_a.compose(None, filename="1234567890") == "1234567890.jpg"
