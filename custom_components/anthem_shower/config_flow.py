"""Config flow for Anthem Shower."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.components import zeroconf
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import AnthemApiClient, AnthemAuthError, AnthemConnectionError
from .const import (
    CONF_HOST,
    CONF_PIN,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_PIN): str,
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
            int, vol.Range(min=10, max=300)
        ),
    }
)


class AnthemShowerConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Anthem Shower."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            pin = user_input.get(CONF_PIN) or None  # Convert empty string to None

            # Prevent duplicate entries for the same host
            self._async_abort_entries_match({CONF_HOST: host})

            session = async_get_clientsession(self.hass)
            client = AnthemApiClient(host, pin, session)

            try:
                await client.async_test_connection()
            except AnthemAuthError:
                errors["base"] = "invalid_auth"
            except AnthemConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected error during config flow")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=f"Anthem Shower ({host})",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_zeroconf(
        self, discovery_info: zeroconf.ZeroconfServiceInfo
    ) -> ConfigFlowResult:
        """Handle zeroconf discovery."""
        # Extract host from discovery info
        host = discovery_info.host

        # Prevent duplicate entries for the same host
        await self.async_set_unique_id(host)
        self._abort_if_unique_id_configured()

        # Store the discovered host for confirmation step
        self.context["title_placeholders"] = {"host": host}

        # Verify we can reach the device
        session = async_get_clientsession(self.hass)
        client = AnthemApiClient(host, None, session)

        try:
            await client.async_test_connection()
        except (AnthemAuthError, AnthemConnectionError):
            return self.async_abort(reason="cannot_connect")
        except Exception:
            _LOGGER.exception("Unexpected error during discovery")
            return self.async_abort(reason="unknown")

        # Show confirmation dialog to user
        return await self.async_step_zeroconf_confirm()

    async def async_step_zeroconf_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle user confirmation of discovered device."""
        host = self.context["title_placeholders"]["host"]

        if user_input is not None:
            pin = user_input.get(CONF_PIN) or None
            scan_interval = user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

            # If PIN was provided, test it
            if pin:
                session = async_get_clientsession(self.hass)
                client = AnthemApiClient(host, pin, session)

                try:
                    await client.async_test_connection()
                except AnthemAuthError:
                    return self.async_show_form(
                        step_id="zeroconf_confirm",
                        data_schema=vol.Schema({
                            vol.Optional(CONF_PIN): str,
                            vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
                                int, vol.Range(min=10, max=300)
                            ),
                        }),
                        errors={"base": "invalid_auth"},
                        description_placeholders={"host": host},
                    )
                except Exception:
                    _LOGGER.exception("Unexpected error during PIN validation")

            return self.async_create_entry(
                title=f"Anthem Shower ({host})",
                data={
                    CONF_HOST: host,
                    CONF_PIN: pin,
                    CONF_SCAN_INTERVAL: scan_interval,
                },
            )

        return self.async_show_form(
            step_id="zeroconf_confirm",
            data_schema=vol.Schema({
                vol.Optional(CONF_PIN): str,
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
                    int, vol.Range(min=10, max=300)
                ),
            }),
            description_placeholders={"host": host},
        )

    async def async_step_reauth(
        self, entry_data: dict[str, Any]
    ) -> ConfigFlowResult:
        """Handle re-auth triggered from a repair."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Let the user re-enter the PIN."""
        errors: dict[str, str] = {}

        reauth_entry = self._get_reauth_entry()

        if user_input is not None:
            host = reauth_entry.data[CONF_HOST]
            new_pin = user_input[CONF_PIN]

            session = async_get_clientsession(self.hass)
            client = AnthemApiClient(host, new_pin, session)

            try:
                await client.async_test_connection()
            except AnthemAuthError:
                errors["base"] = "invalid_auth"
            except AnthemConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected error during reauth")
                errors["base"] = "unknown"
            else:
                return self.async_update_reload_and_abort(
                    reauth_entry,
                    data={**reauth_entry.data, CONF_PIN: new_pin},
                )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({vol.Required(CONF_PIN): str}),
            errors=errors,
            description_placeholders={
                "host": reauth_entry.data[CONF_HOST],
            },
        )
