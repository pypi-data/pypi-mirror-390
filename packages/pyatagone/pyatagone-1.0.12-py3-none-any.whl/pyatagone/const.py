#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: atagone.py
#
# Copyright 2018-2025 Wim van den Herik
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.
#

""" a python interface to the ATAG One Thermostat """

import logging
from enum import Enum, StrEnum
from typing import Dict, Final


_LOGGER = logging.getLogger(__package__)

HEADERS: Final[Dict[str, str]] = {
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
'X-OneApp-Version': 'R34 (18781)',
'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
}

DEFAULT_TIMEOUT = 30
DEFAULT_MIN_TEMP = 4
DEFAULT_MAX_TEMP = 27
DEFAULT_PORT = 10000

