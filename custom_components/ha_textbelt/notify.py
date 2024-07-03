import logging

from homeassistant.components.notify import NotifyEntity, NotifyEntityFeature
from homeassistant.core import (
    HomeAssistant,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN
from .textbelt_api import TextbeltAPI
from .types import TextbeltConfigEntry

log = logging.getLogger(DOMAIN)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TextbeltConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    notifier = SendTextMessage(
        name=entry.runtime_data.phone,
        phone_number=entry.runtime_data.phone,
        textbelt=entry.runtime_data.client,
    )
    async_add_entities([notifier])


class SendTextMessage(NotifyEntity):
    _attr_supported_features = NotifyEntityFeature.TITLE
    _attr_name = "Send Text via Textbelt"
    _attr_has_entity_name = True
    _attr_icon = "mdi:cellphone-charging"

    def __init__(self, name: str, phone_number: str, textbelt: TextbeltAPI) -> None:
        super().__init__()
        self.phone_number = phone_number
        self.textbelt = textbelt
        self._attr_name += f" ({name})"
        self._attr_unique_id = "_".join(
            [
                DOMAIN,
                "notify",
                name,
            ]
        )

    async def async_send_message(self, message: str, **kwargs) -> None:
        """Send a message."""
        resp = await self._send_text(self.phone_number, message=message)
        self._attr_state = resp["textId"]
        return resp

    async def _send_text(self, phone: str, message: str):
        err, resp = await self.textbelt.send_text(
            msg=message,
            phone=phone,
        )
        if err is None:
            return resp
        else:
            raise HomeAssistantError(err, translation_domain=DOMAIN)
