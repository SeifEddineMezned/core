"""Config flow for NYT Games."""

from collections.abc import Mapping
from typing import Any

from nyt_games import NYTGamesAuthenticationError, NYTGamesClient, NYTGamesError
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_TOKEN
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .const import DOMAIN, LOGGER


class NYTGamesConfigFlow(ConfigFlow, domain=DOMAIN):
    """NYT Games config flow."""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a flow initialized by the user."""
        errors: dict[str, str] = {}
        if user_input:
            session = async_create_clientsession(self.hass)
            token = user_input[CONF_TOKEN].strip()
            client = NYTGamesClient(token, session=session)
            try:
                user_id = await client.get_user_id()
            except NYTGamesAuthenticationError:
                errors["base"] = "invalid_auth"
            except NYTGamesError:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                LOGGER.exception("Unexpected error")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(str(user_id))
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title="NYT Games", data={CONF_TOKEN: token}
                )
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_TOKEN): str}),
            errors=errors,
        )

    async def async_step_reauth(
        self, entry_data: Mapping[str, Any]
    ) -> ConfigFlowResult:
        """Handle reauthentication."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm reauthentication."""
        errors: dict[str, str] = {}
        if user_input:
            session = async_create_clientsession(self.hass)
            token = user_input[CONF_TOKEN].strip()
            client = NYTGamesClient(token, session=session)
            try:
                user_id = await client.get_user_id()
            except NYTGamesAuthenticationError:
                errors["base"] = "invalid_auth"
            except NYTGamesError:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                LOGGER.exception("Unexpected error")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(str(user_id))
                self._abort_if_unique_id_mismatch(reason="wrong_account")
                return self.async_update_reload_and_abort(
                    self._get_reauth_entry(),
                    data_updates={CONF_TOKEN: token},
                )
        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({vol.Required(CONF_TOKEN): str}),
            errors=errors,
        )
