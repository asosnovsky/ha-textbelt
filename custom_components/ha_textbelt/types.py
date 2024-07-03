from __future__ import annotations

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry

from .textbelt_api import TextbeltAPI


@dataclass
class TextbeltData:
    """Adguard data type."""

    client: TextbeltAPI
    phone: str


type TextbeltConfigEntry = ConfigEntry[TextbeltData]
