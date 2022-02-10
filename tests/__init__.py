from aiohttp.test_utils import AioHTTPTestCase

from app import setup_app
import json


class MyAppTestCase(AioHTTPTestCase):

    async def get_application(self):
        return setup_app()

    async def test_root(self):
        async with self.client.request("GET", "/") as resp:
            self.assertEqual(resp.status, 200)
            text = await resp.text()
        self.assertIn("html", text)
        self.assertIn("btnStart", text)
        self.assertIn("btnStop", text)
        self.assertIn("btnRestart", text)

    async def test_save1(self):
        data = {'value': True}
        async with self.client.post("/save", data=json.dumps(data)) as resp:
            self.assertEqual(resp.status, 200)
            response_data = json.loads(await resp.text())
            self.assertEqual(response_data, data)

    async def test_save2(self):
        data = {'value': False}
        async with self.client.post("/save", data=json.dumps(data)) as resp:
            self.assertEqual(resp.status, 200)
            response_data = json.loads(await resp.text())
            self.assertEqual(response_data, data)

    async def test_status(self):
        possible_keys = {'name', 'status', 'enabled'}
        async with self.client.post("/status", data=json.dumps({})) as resp:
            self.assertEqual(resp.status, 200)
            response_data = json.loads(await resp.text())
            self.assertEqual(set(response_data.keys()), possible_keys)

    async def test_start(self):
        possible_keys = {'name', 'status'}
        async with self.client.post("/start", data=json.dumps({})) as resp:
            self.assertEqual(resp.status, 200)
            response_data = json.loads(await resp.text())
            self.assertEqual(set(response_data.keys()), possible_keys)

    async def test_restart(self):
        possible_keys = {'name', 'status'}
        async with self.client.post("/restart", data=json.dumps({})) as resp:
            self.assertEqual(resp.status, 200)
            response_data = json.loads(await resp.text())
            self.assertEqual(set(response_data.keys()), possible_keys)

    async def test_stop(self):
        possible_keys = {'name', 'status'}
        async with self.client.post("/stop", data=json.dumps({})) as resp:
            self.assertEqual(resp.status, 200)
            response_data = json.loads(await resp.text())
            self.assertEqual(set(response_data.keys()), possible_keys)
