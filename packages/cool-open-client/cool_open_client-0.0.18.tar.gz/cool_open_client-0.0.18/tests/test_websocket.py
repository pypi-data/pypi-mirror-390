from __future__ import annotations

import unittest
from pathlib import Path
import logging
import sys
from time import sleep
import asyncio

try:
    from cool_open_client.cool_automation_client import CoolAutomationClient
    from cool_open_client.utils.singleton import SingletonMeta
except ModuleNotFoundError as exc:
    if exc.name == "websocket":
        raise unittest.SkipTest("websocket-client dependency missing")
    raise


TOKEN_PATH = Path("token.txt")


@unittest.skipUnless(TOKEN_PATH.exists(), "token.txt fixture missing; websocket test skipped")
class TestWebSocket(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with TOKEN_PATH.open("r", encoding="utf-8") as token_file:
            cls.token = token_file.read().strip()

    async def asyncSetUp(self):
        self._LOGGER = logging.getLogger(__package__)
        self._LOGGER.addHandler(logging.StreamHandler(sys.stdout))
        self._LOGGER.setLevel(logging.DEBUG)
        self.client = await CoolAutomationClient.create(self.token, self._LOGGER)

    async def asyncTearDown(self):
        await self.client.api_client.close()
        SingletonMeta._instances.pop(CoolAutomationClient, None)

    async def test_websocket(self):
        self.client.open_socket()
        await asyncio.sleep(5)


if __name__ == "__main__":
    unittest.main()
