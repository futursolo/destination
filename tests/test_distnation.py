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

from typing import Any

import pytest

from destination import (
    Dispatcher,
    NoMatchesFound,
    NonReversible,
    NotMatched,
    ReRule,
    ReSubDispatcher,
    ReverseError,
)


def test_parse() -> None:
    rule_a = ReRule(r"^(?P<filename>.*)$")

    resolved = rule_a.parse("test.htm")

    assert resolved.identifier == rule_a

    assert resolved.kwargs["filename"] == "test.htm"


def test_not_matched() -> None:
    rule_a = ReRule(r"^(?P<filename>[0-9]+)\.jpg$")

    with pytest.raises(NotMatched):
        rule_a.parse("test.png")


def test_compose() -> None:
    rule_a = ReRule(r"^(?P<filename>[0-9]+)\.jpg$")

    assert rule_a.compose(None, filename="1234567890") == "1234567890.jpg"


def test_partial_re() -> None:
    with pytest.raises(ValueError):
        ReRule(r"index\.htm")

    with pytest.raises(ValueError):
        ReRule(r"^index\.htm")


def test_compose_invalid_value() -> None:
    rule_a = ReRule(r"^(?P<filename>[0-9]+)\.htm$")

    with pytest.raises(ReverseError):
        rule_a.compose(None, filename="test")


def test_justify_reverse_pattern() -> None:
    rule_a = ReRule(r"^(?P<filename>.*).htm$")

    with pytest.raises(NonReversible):
        rule_a.compose(None, filename="test")


def test_reverse_non_named_group() -> None:
    rule_a = ReRule(r"^(.*).htm$")

    with pytest.raises(NonReversible):
        rule_a.compose(None)


def test_resolve() -> None:
    dispatcher: Dispatcher[Any] = Dispatcher()
    dispatcher.add(ReRule(r"^(?P<pagename>.*)\.htm$"), name="page")
    dispatcher.add(ReRule(r"^(?P<imagename>.*)\.jpg$"), name="image")

    resolved_page = dispatcher.resolve("/test.htm")
    resolved_image = dispatcher.resolve("/test.jpg")

    assert resolved_page.kwargs["pagename"] == "test"
    assert resolved_image.kwargs["imagename"] == "test"

    with pytest.raises(NoMatchesFound):
        dispatcher.resolve("/test.mp3")


def test_reverse() -> None:
    dispatcher: Dispatcher[Any] = Dispatcher()
    dispatcher.add(ReRule(r"^(?P<pagename>.*)\.htm$"), name="page")
    dispatcher.add(ReRule(r"^(?P<imagename>.*)\.jpg$"), name="image")

    assert dispatcher.reverse("page", pagename="test") == "/test.htm"
    assert dispatcher.reverse("image", imagename="test") == "/test.jpg"


def test_remove() -> None:
    dispatcher: Dispatcher[Any] = Dispatcher()
    image_rule = ReRule(r"^(?P<imagename>.*)\.jpg$")
    dispatcher.add(image_rule, name="image")

    resolved_image = dispatcher.resolve("/test.jpg")

    assert resolved_image.kwargs["imagename"] == "test"

    dispatcher.remove(image_rule)

    with pytest.raises(NoMatchesFound):
        dispatcher.resolve("/test.jpg")


def test_sub_resolve() -> None:
    dispatcher: Dispatcher[Any] = Dispatcher()
    dispatcher.add(ReRule(r"^(?P<pagename>.*)\.htm$"), name="page")

    api_dispatcher: ReSubDispatcher[Any] = ReSubDispatcher(r"^api/")
    dispatcher.add(api_dispatcher, name="api")

    resolved_page = dispatcher.resolve("/test.htm")
    assert resolved_page.kwargs["pagename"] == "test"

    with pytest.raises(NoMatchesFound):
        dispatcher.resolve("/test.mp3")

    class LoginHandler:
        pass

    api_dispatcher.add(
        ReRule(
            "^login/(?P<user_id>[0-9a-zA-Z]{2,30})$",
            identifier=LoginHandler,
        ),
        name="login",
    )

    resolved_login = dispatcher.resolve("/api/login/jctre9owy4q39p4")

    assert resolved_login.kwargs["user_id"] == "jctre9owy4q39p4"
    assert resolved_login.identifier is LoginHandler


def test_sub_reverse() -> None:
    dispatcher: Dispatcher[Any] = Dispatcher()
    dispatcher.add(ReRule(r"^(?P<pagename>.*)\.htm$"), name="page")

    api_dispatcher: ReSubDispatcher[Any] = ReSubDispatcher(r"^api/")
    dispatcher.add(api_dispatcher, name="api")

    api_dispatcher.add(
        ReRule("^login/(?P<user_id>[0-9a-zA-Z]{2,30})$"), name="login"
    )

    assert (
        dispatcher.reverse("api.login", user_id="jctre9owy4q39p4")
        == "/api/login/jctre9owy4q39p4"
    )
