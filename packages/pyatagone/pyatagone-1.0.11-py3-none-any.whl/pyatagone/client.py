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
from .const import DEFAULT_MAX_TEMP, DEFAULT_MIN_TEMP, DEFAULT_PORT, Schedule


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

    async def async_ch_mode(self, mode: int) -> bool:
        """Set the CH preset mode (manual/auto/etc.)."""
        return await self.send_dynamic_change("ch_mode", mode)

    async def async_set_temperature(self, temperature: Union[int, float]) -> bool:
        """Set new target temperature."""

        target = float(temperature)
        if target < DEFAULT_MIN_TEMP or target > DEFAULT_MAX_TEMP:
            raise ValueError(
                f"Target temperature must be between {DEFAULT_MIN_TEMP} and {DEFAULT_MAX_TEMP}"
            )
        return await self.send_dynamic_change("ch_mode_temp", target)

    async def async_ch_control_mode(self, hvac_mode: int) -> bool:
        """Set the CH control mode (on/off)."""
        return await self.send_dynamic_change("ch_mode", hvac_mode)
          
    async def async_dhw_temp_setp(self, target_temp: float) -> bool:
        """Set new DHW target temperature."""
        return await self.send_dynamic_change("dhw_mode_temp", target_temp)
    
    async def async_dhw_schedule(self, schedule: Schedule) -> bool:
        """Set new DHW schedule."""
        return await self.send_dynamic_change("dhw_schedule", schedule)
    
    async def async_ch_schedule(self, schedule: Schedule) -> bool:
        """Set new CH schedule."""
        return await self.send_dynamic_change("ch_schedule", schedule)

    async def async_dhw_mode(self, mode: int) -> bool:
        """Set the DHW preset mode (manual/auto/etc.)."""
        return await self.send_dynamic_change("dhw_mode", mode)
    
    async def async_create_vacation(self, start_dt_epoch: int, heat_temp: float, duration: int ) -> bool:
        """Create a vacation."""
        return await self.send_dynamic_change(
            "create_vacation",
            {
                "start_vacation": start_dt_epoch,
                "ch_vacation_temp": heat_temp,
                "vacation_duration": duration,
            },
        ) 

    async def async_cancel_vacation(self) -> bool:
        """Cancel the current vacation."""
        return await self.send_dynamic_change("cancel_vacation", {})
    
    async def async_outs_temp_offs(self, correction: float) -> bool:
        """Set the outside temperature offset correction."""
        return await self.send_dynamic_change("outs_temp_offs", correction)

    async def async_room_temp_offs(self, correction: float) -> bool:
        """Set the room temperature offset correction."""
        return await self.send_dynamic_change("room_temp_offs", correction)
    
    async def async_summer_eco_mode(self, mode: int) -> bool:
        """Set the summer eco mode (on/off)."""
        return await self.send_dynamic_change("summer_eco_mode", mode)
    
    async def async_summer_eco_temp(self, eco_temp: float) -> bool:
        """Set the summer eco temperature."""
        return await self.send_dynamic_change("summer_eco_temp", eco_temp)
    
    async def async_ch_vacation_temp(self, heat_temp: float) -> bool:
        """Set the CH vacation temperature."""
        return await self.send_dynamic_change("ch_vacation_temp", heat_temp)
      
    async def async_ch_building_size(self, building_size: int) -> bool:
        """Set the CH building size."""
        return await self.send_dynamic_change("ch_building_size", building_size)
    
    async def async_ch_isolation(self, isolation: int) -> bool:
        """Set the CH isolation."""
        return await self.send_dynamic_change("ch_isolation", isolation)
        
    async def async_ch_heating_type(self, heating_type: int) -> bool:
        """Set the CH heating type."""
        return await self.send_dynamic_change("ch_heating_type", heating_type)
    
    async def async_wdr_temps_influence(self, influence: int) -> bool:
        """Set the WDR temps influence."""
        return await self.send_dynamic_change("wdr_temps_influence", influence) 
    
    async def async_frost_prot_enabled(self, enabled: int) -> bool:
        """Set the frost protection enabled."""
        return await self.send_dynamic_change("frost_prot_enabled", enabled)