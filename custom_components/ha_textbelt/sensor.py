"""Platform for sensor integration."""

from __future__ import annotations

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .textbelt_api import TextbeltAPI
from .types import TextbeltConfigEntry
from .const import DOMAIN

log = logging.getLogger(DOMAIN)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TextbeltConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    sensor = CreditBalanceSensor(
        name=entry.runtime_data.phone,
        phone_number=entry.runtime_data.phone,
        textbelt=entry.runtime_data.client,
    )
    async_add_entities([sensor], True)


class CreditBalanceSensor(SensorEntity):
    _attr_name = "Credit Balance for API KEY"
    _attr_icon = "mdi:credit-card-multiple"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.TOTAL
    _attr_unit_of_measurement = "msgs"
    _attr_should_poll = True

    def __init__(self, name: str, phone_number: str, textbelt: TextbeltAPI) -> None:
        super().__init__()
        self.textbelt = textbelt
        self.phone_number = phone_number
        self._attr_name += f" ({name})"
        self._attr_unique_id = "_".join(
            [
                DOMAIN,
                "credit_balance",
                name,
            ]
        )

    async def async_update(self) -> None:
        err, resp = await self.textbelt.get_balance()
        if err is None:
            self._attr_available = True
            self._attr_native_value = resp
        else:
            self._attr_available = False
            self._attr_native_value = 0
            raise HomeAssistantError(f"Textbelt ERROR {err}", translation_domain=DOMAIN)
