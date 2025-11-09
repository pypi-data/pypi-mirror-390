from __future__ import annotations

import unittest
from pathlib import Path

try:
    from cool_open_client.cool_automation_client import CoolAutomationClient, InvalidTokenException
    from cool_open_client.utils.singleton import SingletonMeta
    from cool_open_client.client.models.device_response_data import DeviceResponseData
    from cool_open_client.client.models.user_response_data import UserResponseData
except ModuleNotFoundError as exc:
    if exc.name == "websocket":
        raise unittest.SkipTest("websocket-client dependency missing")
    raise


TOKEN_PATH = Path("token.txt")
BAD_TOKEN_PATH = Path("bad_token.txt")


def read_fixture(path: Path) -> str:
    with path.open("r", encoding="utf-8") as token_file:
        return token_file.read().strip()


@unittest.skipUnless(TOKEN_PATH.exists(), "token.txt fixture missing; integration tests skipped")
class CoolAutomationClientIntegrationTest(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.token = read_fixture(TOKEN_PATH)

    async def asyncSetUp(self):
        self.client = await CoolAutomationClient.create(token=self.token)

    async def asyncTearDown(self):
        await self.client.api_client.close()
        SingletonMeta._instances.pop(CoolAutomationClient, None)

    async def test_get_me_returns_user_data(self):
        response = await self.client.get_me()
        self.assertIsInstance(response, UserResponseData)
        self.assertTrue(getattr(response, "id", None))

    async def test_dictionary_mapping_roundtrip(self):
        modes = self.client.operation_modes.data
        self.assertTrue(modes)
        mode_id, mode_name = next(iter(modes.items()))
        self.assertIsInstance(mode_id, int)
        self.assertIsInstance(mode_name, str)
        self.assertEqual(self.client.operation_modes.get(mode_id), mode_name)
        self.assertEqual(self.client.operation_modes.get_inverse(mode_name), mode_id)

    async def test_get_devices_returns_connected_models(self):
        devices = await self.client.get_devices()
        for device in devices:
            self.assertIsInstance(device, DeviceResponseData)
            self.assertTrue(device.is_connected)

    async def test_get_dictionary_fetches_types(self):
        dictionaries = await self.client.get_dictionary()
        self.assertIsNotNone(dictionaries)
        self.assertTrue(self.client.operation_statuses.data)

    @unittest.skipUnless(BAD_TOKEN_PATH.exists(), "bad_token.txt fixture missing; invalid-token test skipped")
    async def test_create_with_bad_token_raises(self):
        invalid_token = read_fixture(BAD_TOKEN_PATH)
        with self.assertRaises(InvalidTokenException):
            bad_client = await CoolAutomationClient.create(token=invalid_token)


if __name__ == "__main__":
    unittest.main()
