from typing import Any

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.const import CONF_API_KEY

from .const import DOMAIN
from .schemas import USER_INPUT_SCHEMA


class TextbeltFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        errors = {}
        if user_input is not None:
            self.context["title_placeholders"] = {"name": user_input[CONF_API_KEY]}
            return self.async_create_entry(title=DOMAIN, data=user_input)
        return self.async_show_form(
            step_id="user",
            data_schema=USER_INPUT_SCHEMA,
            errors=errors,
            description_placeholders={
                k.schema: k.description for k in USER_INPUT_SCHEMA.schema.keys()
            },
        )
