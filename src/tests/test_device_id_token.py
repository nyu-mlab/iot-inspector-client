import os
import sys
import unittest
from unittest import mock

# device_id_api_thread imports `common` as a top-level module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "iot_inspector"))

from iot_inspector.background import device_id_api_thread as dev_id  # noqa: E402


class TestInstallToken(unittest.TestCase):

    def setUp(self):
        self.config = {}
        patches = [
            mock.patch.object(dev_id.common, "config_get", side_effect=lambda k, d=None: self.config.get(k, d)),
            mock.patch.object(dev_id.common, "config_set", side_effect=self.config.__setitem__),
            mock.patch.dict(os.environ, {}, clear=False),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)
        os.environ.pop("API_KEY", None)

    def test_mints_and_persists_token_on_first_use(self):
        token = dev_id._get_install_token()
        self.assertTrue(token.startswith("ins_"))
        self.assertEqual(self.config[dev_id.INSTALL_TOKEN_KEY], token)

    def test_reuses_persisted_token(self):
        first = dev_id._get_install_token()
        self.assertEqual(dev_id._get_install_token(), first)

    def test_tokens_differ_across_installs(self):
        first = dev_id._get_install_token()
        self.config.clear()
        self.assertNotEqual(dev_id._get_install_token(), first)

    def test_api_key_env_overrides_and_is_not_persisted(self):
        os.environ["API_KEY"] = "research-key"
        self.assertEqual(dev_id._get_install_token(), "research-key")
        self.assertNotIn(dev_id.INSTALL_TOKEN_KEY, self.config)


if __name__ == "__main__":
    unittest.main()
