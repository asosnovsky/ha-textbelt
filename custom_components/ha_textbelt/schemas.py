import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from homeassistant.const import CONF_API_KEY, CONF_URL, CONF_ENTITY_ID
from .const import PHONE_ENTRY, MESSAGE_ENTRY

USER_INPUT_SCHEMA = vol.Schema(
    {
        vol.Optional(
            PHONE_ENTRY,
        ): cv.string,
        vol.Required(
            CONF_API_KEY,
        ): cv.string,
        vol.Optional(
            CONF_URL,
            default="https://textbelt.com/",
        ): cv.string,
    }
)

SEND_TEXT_SCHEMA = vol.Schema(
    {
        vol.Required(
            MESSAGE_ENTRY,
        ): cv.string,
        vol.Required(
            PHONE_ENTRY,
        ): cv.string,
    },
    extra=vol.ALLOW_EXTRA,
)
