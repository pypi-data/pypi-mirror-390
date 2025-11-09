from __future__ import annotations

import unittest
from pathlib import Path

try:
    from cool_open_client.hvac_units_factory import HVACUnitsFactory
    from cool_open_client.cool_automation_client import CoolAutomationClient
    from cool_open_client.utils.singleton import SingletonMeta
    from cool_open_client.unit import HVACUnit
except ModuleNotFoundError as exc:
    if exc.name == "websocket":
        raise unittest.SkipTest("websocket-client dependency missing")
    raise


TOKEN_PATH = Path("token.txt")


def read_fixture(path: Path) -> str:
    with path.open("r", encoding="utf-8") as token_file:
        return token_file.read().strip()


@unittest.skipUnless(TOKEN_PATH.exists(), "token.txt fixture missing; integration tests skipped")
class HVACUnitsFactoryIntegrationTest(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.token = read_fixture(TOKEN_PATH)

    async def asyncSetUp(self):
        self.factory = await HVACUnitsFactory.create(self.token)

    async def asyncTearDown(self):
        await self.factory._client.api_client.close()
        SingletonMeta._instances.pop(CoolAutomationClient, None)

    async def test_generate_units_from_api(self):
        units = await self.factory.generate_units_from_api()
        self.assertIsInstance(units, list)
        for unit in units:
            self.assertIsInstance(unit, HVACUnit)
            self.assertIsNotNone(unit.name)
            self.assertIsInstance(unit.operation_modes, list)
            if unit.operation_modes:
                self.assertIsInstance(unit.operation_modes[0], str)


if __name__ == "__main__":
    unittest.main()
