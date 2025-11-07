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
"""High level client for interacting with the ATAG One thermostat."""

from __future__ import annotations

from typing import Optional, Union

from .atagoneapi import AtagOneApi
from .const import DEFAULT_MAX_TEMP, DEFAULT_MIN_TEMP, DEFAULT_PORT


class AtagOne(AtagOneApi):
    """High-level Atag One client that exposes user-friendly helpers."""

    def __init__(self, host: Optional[str] = None, port: int = DEFAULT_PORT) -> None:
        super().__init__(host=host, port=port)

    async def async_discover(self) -> Optional[str]:
        """Discover the thermostat and remember the host that answered."""
        addr = await super().async_discover()
        if addr:
            self.host = addr
        return addr

    async def async_ch_mode_temp(self, temperature: Union[int, float]) -> bool:
        """Set the CH target temperature after validating allowed range."""
        target = float(temperature)
        if target < DEFAULT_MIN_TEMP or target > DEFAULT_MAX_TEMP:
            raise ValueError(
                f"Target temperature must be between {DEFAULT_MIN_TEMP} and {DEFAULT_MAX_TEMP}"
            )
        return await self.send_dynamic_change("ch_mode_temp", target)

    async def async_ch_mode(self, mode: int) -> bool:
        """Set the CH preset mode (manual/auto/etc.)."""
        return await self.send_dynamic_change("ch_mode", mode)
