import unittest

from pipecash.secretsManager import SecretsManager

secretsPath = "tests/general_test/test_secretsManager.json"


class SecretsManagerTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_secrets_parsing(self):
        secrets = SecretsManager.loadFromFile(secretsPath)
        names = ['v' + str(i) for i in range(8)]
        self.assertListEqual(secrets.findMissingKeys(*names), [])
        self.assertFalse(secrets.hasKey("v8"))
        values = secrets.get(*names)
        for n in names:
            self.assertEqual(values[n], 42)

    def test_secrets_getSubset(self):
        secrets = SecretsManager.loadFromFile(secretsPath)
        names = ['v' + str(i) for i in range(4)]
        self.assertListEqual(secrets.findMissingKeys(*names), [])
        values = secrets.get(*names)
        for n in names:
            self.assertEqual(values[n], 42)
        self.assertEqual(len(values.keys()), 4)

    def test_secrets_noSuchKey(self):
        secrets = SecretsManager.loadFromFile(secretsPath)
        self.assertListEqual(secrets.findMissingKeys(
            "v1", "noKey", "v2"), ["noKey"])
        with self.assertRaises(KeyError):
            secrets.get("v1", "noKey", "v2")
