"""Example of a custom component exposing a service."""

from __future__ import annotations

import logging
from functools import partial
from homeassistant.const import CONF_API_KEY, CONF_URL, Platform, CONF_ENTITY_ID
from homeassistant.core import (
    HomeAssistant,
    SupportsResponse,
    ServiceCall,
    ServiceResponse,
    HassJobType,
)
from homeassistant.exceptions import HomeAssistantError
from homeassistant.config_entries import ConfigEntryState
from homeassistant.helpers.entity_component import EntityComponent

from .const import DOMAIN, SERVICES_SEND_TEXT, PHONE_ENTRY, MESSAGE_ENTRY
from .textbelt_api import TextbeltAPI
from .schemas import SEND_TEXT_SCHEMA
from .types import TextbeltConfigEntry, TextbeltData
from .sensor import CreditBalanceSensor

log = logging.getLogger(DOMAIN)
PLATFORMS = [Platform.SENSOR, Platform.NOTIFY]


async def async_setup(hass: HomeAssistant, config: TextbeltConfigEntry):
    hass.data[DOMAIN] = EntityComponent[CreditBalanceSensor](log, DOMAIN, hass)
    hass.services.async_register(
        DOMAIN,
        SERVICES_SEND_TEXT,
        partial(send_text, hass=hass),
        schema=SEND_TEXT_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
        job_type=HassJobType.Coroutinefunction,
    )
    return True


async def async_setup_entry(hass: HomeAssistant, config: TextbeltConfigEntry) -> bool:
    textbelt = TextbeltAPI(config.data[CONF_API_KEY], config.data[CONF_URL])
    config.runtime_data = TextbeltData(textbelt, config.data[PHONE_ENTRY])
    await hass.config_entries.async_forward_entry_setups(config, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: TextbeltConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    loaded_entries = [
        entry
        for entry in hass.config_entries.async_entries(DOMAIN)
        if entry.state == ConfigEntryState.LOADED
    ]
    if len(loaded_entries) == 1:
        hass.services.async_remove(DOMAIN, SERVICES_SEND_TEXT)

    return unload_ok


async def send_text(call: ServiceCall, hass: HomeAssistant) -> ServiceResponse:
    entity_ids = call.data[CONF_ENTITY_ID]
    message = call.data[MESSAGE_ENTRY]
    phone = call.data[PHONE_ENTRY]
    p: EntityComponent[CreditBalanceSensor] = hass.data[Platform.SENSOR]
    resp = {}
    success = 0
    for entity_id in entity_ids:
        e = p.get_entity(entity_id)
        if isinstance(e, CreditBalanceSensor):
            err, r = await e.textbelt.send_text(msg=message, phone=phone)
            if err is not None:
                log.warning(f"Failed to send text to {entity_id} due to {err}")
                resp[entity_id] = {"success": False, "error": err}
            else:
                success += 1
                resp[entity_id] = r
        else:
            log.warning(f"invalid entity {entity_id} cannot be used for text messages")
    if success == 0:
        raise HomeAssistantError(
            f"Failed to send text due to {resp}",
            translation_domain=DOMAIN,
        )
    return resp
