# -*- coding: utf-8 -*-
from logging import getLogger
from ssl import create_default_context

import certifi

from vpnflow.settings import settings

logger = getLogger(__name__)
ssl_context = create_default_context(cafile=certifi.where())


class Cloudflare:
    """⭐"""

    settings = settings.cloudflare

    is_ready = all(
        (
            settings.email.get_secret_value(),
            settings.api_key.get_secret_value(),
            settings.zone_id.get_secret_value()
            )
        )

    @classmethod
    async def request(
        cls,
        session,
        method,
        path,
        json,
        headers={
            "Content-Type": "application/json",
            "X-Auth-Email": settings.email.get_secret_value(),
            "Authorization": f"Bearer {settings.api_key.get_secret_value()}"
            }
        ):
        """⭐"""
        session_request = session.request(
            method, cls.settings.host_api + path,
            json=json, headers=headers, ssl=ssl_context
            )
        async with session_request as resp:
            if resp.status == 200:
                resp_data = await resp.json()
                return resp_data
            else:
                try:
                    resp_data = await resp.json()
                except Exception:
                    resp_data = await resp.text()
                logger.error(f"Status: {resp.status}. Message: {resp_data}")
                resp.raise_for_status()
