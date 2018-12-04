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

import os
import re

_DEV_RE = re.compile(r"_dev\s*?=\s*?.*", flags=re.M)
_TAG_VERSION_RE = re.compile(r"_tag_version\s*?=\s*?.*", flags=re.M)


def modify(project_folder: str) -> None:
    tag = os.environ.get("TRAVIS_TAG", None)

    if tag:
        dev_no = "None"

        tag = tag.lower()
        if tag.startswith("v"):
            tag = tag[1:]

    else:
        dev_no = str(os.environ.get("TRAVIS_BUILD_NUMBER", "0"))
        tag = "0.0.0"

    with open("{}/_version.py".format(project_folder), "r+") as f:
        f_str = f.read()
        f_str = re.sub(_DEV_RE, f"_dev = {dev_no}", f_str)
        f_str = re.sub(_TAG_VERSION_RE, f"_tag_version = \"{tag}\"", f_str)

        f.seek(0)
        f.truncate()
        f.write(f_str)
        f.flush()
