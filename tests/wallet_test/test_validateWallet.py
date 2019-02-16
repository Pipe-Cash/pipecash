import unittest
import traceback

from pipecash.walletWrapper import WalletWrapper
from pipecash.secretsManager import SecretsManager

from tests import utils


def TestWalletFactory(membersToInclude):

    class WalletMock():
        pass

    w = WalletMock()

    membersDefaults = {
        "checkBalance": utils.methodMock(w, lambda: None, "checkBalance"),
        "check_dependencies_missing": utils.methodMock(w, lambda: None, "check_dependencies_missing"),
        "default_options": {},
        "description": "",
        "secrets": {},
        "getLatestTransactions": utils.methodMock(w, lambda: None, "getLatestTransactions"),
        "getReceiveAddress": utils.methodMock(w, lambda: None, "getReceiveAddress"),
        "start": utils.methodMock(w, lambda: None, "start"),
        "options": {},
        "send": utils.methodMock(w, lambda: None, "send"),
        "uses_secret_variables": lambda: True,
        "validate_options": utils.methodMock(w, lambda: None, "validate_options"),
    }

    unknownMembers = [i for i in membersToInclude if i not in membersDefaults]
    if len(unknownMembers) > 0:
        raise KeyError("Unknown wallet field : " + str(unknownMembers))

    for m in membersDefaults:
        if(m in membersToInclude):
            specified = membersToInclude[m]
            val = specified if specified is not None else membersDefaults[m]
            setattr(w, m, val)
    return w


class WalletValidationTest(unittest.TestCase):

    def __shouldPassValidation(self, members, config, secrets):
        wallet = TestWalletFactory(members)
        msg = "\n--------\nDetails:\n> With Members:\n%s\n> Config\n%s\n> Env\n%s" % (
            repr(members), repr(config), repr(secrets))
        try:
            walletWrapper = WalletWrapper(
                wallet, config, SecretsManager(secrets))
            return walletWrapper
        except Exception as ex:
            tb = traceback.format_exc()
            self.fail("Expected wallet validation to pass, but it failed :\n%s%s\n%s" % (
                str(ex), msg, tb)
            )

    def __shouldFailValidation(self, members, config, secrets):
        wallet = TestWalletFactory(members)
        msg = "\n--------\nDetails:\n> With Members:\n%s\n> Config\n%s\n> Env\n%s" % (
            repr(members), repr(config), repr(secrets))

        return utils.expectError(
            lambda: WalletWrapper(wallet, config, SecretsManager(secrets)),
            "Wallet validation was expected to fail but didn't : " + msg)

    def test_walletWrapper_validation_minimalWallet(self):

        members = {"start": None,
                   "checkBalance": None, "send": None,
                   "getReceiveAddress": None,
                   "getLatestTransactions": None
                   }
        secrets = {}
        config = {
            "name": "Wallet Name",
        }

        self.__shouldPassValidation(members, config, secrets)

    def test_walletWrapper_validation_without_init_shouldFail(self):
        self.walletWrapper_validation_withoutMember_shouldFail(
            "start", "should have member : start")

    def test_walletWrapper_validation_without_checkBalance_shouldFail(self):
        self.walletWrapper_validation_withoutMember_shouldFail(
            "checkBalance", "should have member : checkBalance")

    def test_walletWrapper_validation_without_send_shouldFail(self):
        self.walletWrapper_validation_withoutMember_shouldFail(
            "send", "should have member : send")

    def test_walletWrapper_validation_without_getReceiveAddress_shouldFail(self):
        self.walletWrapper_validation_withoutMember_shouldFail(
            "getReceiveAddress", "should have member : getReceiveAddress")

    def test_walletWrapper_validation_without_getLatestTransactions_shouldFail(self):
        self.walletWrapper_validation_withoutMember_shouldFail(
            "getLatestTransactions", "should have member : getLatestTransactions")

    def walletWrapper_validation_withoutMember_shouldFail(self, exclude, errMsg):

        members = {"start": None,
                   "checkBalance": None, "send": None,
                   "getReceiveAddress": None,
                   "getLatestTransactions": None
                   }
        secrets = {}
        config = {
            "name": "Wallet Name",
        }

        del members[exclude]

        ex, tb = self.__shouldFailValidation(members, config, secrets)

        self.assertEqual(str(ex)[-len(errMsg):], errMsg,
                         str(ex) + " did not match " + errMsg + "\n\n Occured in: \n" + tb)

    def test_walletWrapper_validation_minimalWithDefaultOptions(self):

        members = {"start": None,
                   "checkBalance": None, "send": None,
                   "getReceiveAddress": None,
                   "getLatestTransactions": None,
                   "options": None, "default_options": None
                   }
        secrets = {}
        config = {
            "name": "Wallet Name",
        }

        wrapper = self.__shouldPassValidation(members, config, secrets)

    def test_walletWrapper_validation_withConfigOptions(self):

        members = {"start": None,
                   "checkBalance": None, "send": None,
                   "getReceiveAddress": None,
                   "getLatestTransactions": None,
                   "options": None
                   }
        secrets = {}
        config = {
            "name": "Wallet Name",
            "options": {}
        }

        wrapper = self.__shouldPassValidation(members, config, secrets)

    def test_walletWrapper_validation_withConfigOptions_andValidateOptions(self):

        members = {"start": None,
                   "checkBalance": None, "send": None,
                   "getReceiveAddress": None,
                   "getLatestTransactions": None,
                   "options": None, "validate_options": None,
                   }
        secrets = {}
        config = {
            "name": "Wallet Name",
            "options": {}
        }

        wrapper = self.__shouldPassValidation(members, config, secrets)

        called = wrapper.wallet.calledMethods
        self.assertEqual(len(called), 1)
        self.assertEqual(called[0], "validate_options")

    def test_walletWrapper_validation_withConfigOptions_andValidateOptions(self):

        members = {"start": None,
                   "checkBalance": None, "send": None,
                   "getReceiveAddress": None,
                   "getLatestTransactions": None,
                   "options": None, "validate_options": None
                   }
        secrets = {}
        config = {
            "name": "Wallet Name",
            "options": {}
        }

        wrapper = self.__shouldPassValidation(members, config, secrets)

        called = wrapper.wallet.calledMethods
        self.assertEqual(len(called), 1)
        self.assertEqual(called[0], "validate_options")

    def test_walletWrapper_validation_checkDependenciesSuccess(self):
        members = {"start": None,
                   "checkBalance": None, "send": None,
                   "getReceiveAddress": None,
                   "getLatestTransactions": None,
                   "check_dependencies_missing": None
                   }
        secrets = {}
        config = {
            "name": "Wallet Name",
        }

        wrapper = self.__shouldPassValidation(members, config, secrets)

        called = wrapper.wallet.calledMethods
        self.assertEqual(len(called), 1)
        self.assertEqual(called[0], "check_dependencies_missing")

    def test_walletWrapper_validation_checkDependenciesFail(self):
        members = {"start": None,
                   "checkBalance": None, "send": None,
                   "getReceiveAddress": None,
                   "getLatestTransactions": None,
                   "check_dependencies_missing": utils.funcToMethod(
                       lambda: utils.raiseErr(Exception("ErrMsg")))
                   }
        secrets = {}
        config = {
            "name": "Wallet Name",
        }

        ex, tb = self.__shouldFailValidation(members, config, secrets)

        self.assertEqual(str(ex),
                         "[Errno Agent 'Wallet Name' has missing dependencies: ] ErrMsg")

    def test_walletWrapper_validation_withEnv(self):
        members = {"start": None,
                   "checkBalance": None, "send": None,
                   "getReceiveAddress": None,
                   "getLatestTransactions": None,
                   "secrets": {},
                   "uses_secret_variables": ["EXTRA_ENV_VALUE"]
                   }
        secrets = {
            "EXTRA_ENV_VALUE": "my secret value"
        }
        config = {
            "name": "Wallet Name",
        }

        wrapper = self.__shouldPassValidation(members, config, secrets)

        self.assertEqual(len(wrapper.wallet.secrets.keys()), 1)
        self.assertEqual(list(wrapper.wallet.secrets.keys())
                         [0], "EXTRA_ENV_VALUE")
        self.assertEqual(
            wrapper.wallet.secrets["EXTRA_ENV_VALUE"], "my secret value")

    def test_walletWrapper_validation_withEnv_MissingEnv(self):
        members = {"start": None,
                   "checkBalance": None, "send": None,
                   "getReceiveAddress": None,
                   "getLatestTransactions": None,
                   "secrets": {},
                   "uses_secret_variables": ["EXTRA_ENV_VALUE"]
                   }
        secrets = {}
        config = {
            "name": "Wallet Name",
        }

        ex, tb = self.__shouldFailValidation(members, config, secrets)

        self.assertEqual(
            str(ex), "\"Not all keys were found : ['EXTRA_ENV_VALUE']\"")

    def test_walletWrapper_validation_withEnv_MissingWalletEnvField(self):
        members = {"start": None,
                   "checkBalance": None, "send": None,
                   "getReceiveAddress": None,
                   "getLatestTransactions": None,
                   "uses_secret_variables": ["EXTRA_ENV_VALUE"]
                   }
        secrets = {
            "EXTRA_ENV_VALUE": "my secret value"
        }
        config = {
            "name": "Wallet Name",
        }

        ex, tb = self.__shouldFailValidation(members, config, secrets)

        expectedMessageEnd = "should have member : secrets"
        self.assertEqual(
            str(ex)[-len(expectedMessageEnd):], expectedMessageEnd)
