import unittest

import traceback
from types import MethodType, FunctionType

from pipecash.agentWrapper import AgentWrapper
from pipecash.walletWrapper import WalletWrapper
from pipecash.secretsManager import SecretsManager

import tests.utils as utils
import tests.scenario_test.mocks as mocks


def TestAgentFactory(membersToInclude):

    class AgentMock():
        calledMethods = []

    a = AgentMock()

    membersDefaults = {
        "start": utils.methodMock(a, lambda: None, "start"),
        "options": {},
        "wallet": mocks.TestWallet(),
        "description": "A few words about the agent",
        "event_description": {},
        "default_options": {},
        "default_schedule": "every_1s",
        "uses_wallet": False,
        "uses_secret_variables": [],
        "secrets": {},
        "validate_options": utils.methodMock(a, lambda: None, "validate_options"),
        "check": utils.methodMock(a, lambda: None, "check"),
        "receive": utils.methodMock(a, lambda: None, "receive"),
        "is_unavailable": utils.methodMock(a, lambda: None, "is_unavailable"),
        "check_dependencies_missing": utils.methodMock(a, lambda: None, "check_dependencies_missing"),
    }

    unknownMembers = [i for i in membersToInclude if i not in membersDefaults]
    if len(unknownMembers) > 0:
        raise KeyError("Unknown wallet field : " + str(unknownMembers))

    for m in membersDefaults:
        if(m in membersToInclude):
            specified = membersToInclude[m]
            val = specified if specified is not None else membersDefaults[m]
            setattr(a, m, val)

    return a


class AgentValidationTest(unittest.TestCase):

    def __shouldPassValidation(self, members, config, secrets):
        agent = TestAgentFactory(members)
        msg = "\n--------\nDetails:\n> With Members:\n%s\n> Config\n%s\n> Env\n%s" % (
            repr(members), repr(config), repr(secrets))
        try:
            agentWrapper = AgentWrapper(agent, config, SecretsManager(secrets))
            return agentWrapper
        except Exception as ex:
            tb = traceback.format_exc()
            self.fail("Expected agent validation to pass, but it failed :\n%s%s\n%s" % (
                str(ex), msg, tb)
            )

    def __shouldFailValidation(self, members, config, secrets):
        agent = TestAgentFactory(members)
        msg = "\n--------\nDetails:\n> With Members:\n%s\n> Config\n%s\n> Env\n%s" % (
            repr(members), repr(config), repr(secrets))

        return utils.expectError(
            lambda: AgentWrapper(agent, config, SecretsManager(secrets)),
            "Agent validation was expected to fail but didn't : " + msg)

    #   #############################
    #   #### CORRECT INPUT TESTS ####
    #   #############################

    def test_agentWrapper_validation_shouldPass_minimal(self):
        members = {"start": None, "description": None, }
        config = {"name": "Agent Name"}
        secrets = {}
        wrapper = self.__shouldPassValidation(members, config, secrets)

    def test_agentWrapper_validation_shouldPass_default_schedule(self):
        members = {"start": None, "description": None,
                   "default_schedule": None, "check": None}
        config = {"name": "Agent Name"}
        secrets = {}
        wrapper = self.__shouldPassValidation(members, config, secrets)

    def test_agentWrapper_validation_shouldPass_scheduleInConfig(self):
        members = {"start": None, "description": None,
                   "default_schedule": None, "check": None}
        config = {"name": "Agent Name", "schedule": "every_1s"}
        secrets = {}
        wrapper = self.__shouldPassValidation(members, config, secrets)

    def test_agentWrapper_validation_shouldPass_check(self):
        members = {"start": None, "description": None,
                   "check": None}
        config = {"name": "Agent Name"}
        secrets = {}
        wrapper = self.__shouldPassValidation(members, config, secrets)
        wrapper.setControllerAgent(wrapper)

    def test_agentWrapper_validation_shouldPass_uses_secret_variables(self):
        members = {"start": None, "description": None,
                   "uses_secret_variables": None}
        config = {"name": "Agent Name"}
        secrets = {}
        wrapper = self.__shouldPassValidation(members, config, secrets)

    def test_agentWrapper_validation_shouldPass_uses_secret_variables_TEST_VAR(self):
        members = {"start": None, "description": None,
                   "uses_secret_variables": ["TEST_VAR"]}
        config = {"name": "Agent Name"}
        secrets = {"TEST_VAR": "Test"}
        wrapper = self.__shouldPassValidation(members, config, secrets)
        self.assertEqual(len(wrapper.agent.secrets), 1, wrapper.agent.secrets)
        self.assertEqual(wrapper.agent.secrets["TEST_VAR"], "Test")

    def test_agentWrapper_validation_shouldPass_default_options(self):
        members = {"start": None, "description": None,
                   "options": None, "default_options": {"foo": "bar"}}
        config = {"name": "Agent Name"}
        secrets = {}
        wrapper = self.__shouldPassValidation(members, config, secrets)
        self.assertEqual(wrapper.agent.options["foo"], "bar")

    def test_agentWrapper_validation_shouldPass_validate_options(self):
        members = {"start": None, "description": None,
                   "options": None, "default_options": None, "validate_options": None}
        config = {"name": "Agent Name"}
        secrets = {}
        wrapper = self.__shouldPassValidation(members, config, secrets)
        called = wrapper.agent.calledMethods
        self.assertEqual(len(called), 1)
        self.assertEqual(called[0], "validate_options")

    def test_agentWrapper_validation_shouldPass_validate_options_fromConfig(self):
        members = {"start": None, "description": None,
                   "options": None, "validate_options": None}
        config = {"name": "Agent Name", "options": {}}
        secrets = {}
        wrapper = self.__shouldPassValidation(members, config, secrets)
        called = wrapper.agent.calledMethods
        self.assertEqual(len(called), 1)
        self.assertEqual(called[0], "validate_options")

    def test_agentWrapper_validation_shouldPass_uses_wallet(self):
        members = {"start": None, "description": None,
                   "wallet": None, "uses_wallet": True}
        config = {"name": "Agent Name", "options": {}}
        secrets = {"WALLET_KEY": "TestKey"}
        wrapper = self.__shouldPassValidation(members, config, secrets)
        wallet = WalletWrapper(mocks.TestWallet(), {
                               "name": "W1"}, SecretsManager(secrets))
        wrapper.setWallet(wallet)
        self.assertEqual(wrapper.walletWrapper, wallet)
        self.assertEqual(wrapper.walletWrapper.wallet, wallet.wallet)

    def test_agentWrapper_validation_shouldPass_receive(self):
        members = {"start": None, "description": None,
                   "receive": None}
        config = {"name": "Agent Name", "options": {}}
        secrets = {}
        wrapper = self.__shouldPassValidation(members, config, secrets)
        wrapper.receiveEventsFrom(wrapper)

    def test_agentWrapper_validation_shouldPass_check_dependencies_missing(self):
        members = {"start": None, "description": None,
                   "check_dependencies_missing": None}
        config = {"name": "Agent Name", "options": {}}
        secrets = {}
        wrapper = self.__shouldPassValidation(members, config, secrets)
        called = wrapper.agent.calledMethods
        self.assertEqual(len(called), 1)
        self.assertEqual(called[0], "check_dependencies_missing")

    #   #############################
    #   ### TESTS EXPECTED ERRORS ###
    #   #############################

    def test_agentWrapper_validation_lessThanMinimal_shouldFail_noInit(self):
        members = {"description": None, }
        config = {"name": "Agent Name"}
        secrets = {}
        ex, tb = self.__shouldFailValidation(members, config, secrets)

        errMsg = "should have member : start"

        self.assertEqual(str(ex)[-len(errMsg):], errMsg,
                         "Actual Error did not match expected: \nActual  :%s\nExpected:%s\n----\n Occured in: \n%s" % (str(ex), errMsg, tb))

    def test_agentWrapper_validation_lessThanMinimal_shouldFail_NoDescription(self):
        members = {"start": None, }
        config = {"name": "Agent Name"}
        secrets = {}
        ex, tb = self.__shouldFailValidation(members, config, secrets)

        errMsg = "should have member : description"

        self.assertEqual(str(ex)[-len(errMsg):], errMsg,
                         "Actual Error did not match expected: \nActual  :%s\nExpected:%s\n----\n Occured in: \n%s" % (str(ex), errMsg, tb))

    def test_agentWrapper_validation_minimal_wrongInitType(self):
        members = {"start": lambda: None, "description": None, }
        config = {"name": "Agent Name"}
        secrets = {}
        ex, tb = self.__shouldFailValidation(members, config, secrets)

        errMsg = ".start should be of type <%s>, but was <%s>" % (
            MethodType.__name__, FunctionType.__name__)

        self.assertEqual(str(ex)[-len(errMsg):], errMsg,
                         "Actual Error did not match expected: \nActual  :%s\nExpected:%s\n----\n Occured in: \n%s" % (str(ex), errMsg, tb))

    def test_agentWrapper_validation_minimal_wrongDescriptionType(self):
        members = {"start": None, "description": 42, }
        config = {"name": "Agent Name"}
        secrets = {}
        ex, tb = self.__shouldFailValidation(members, config, secrets)

        errMsg = ".description should be of type <str>, but was <int>"

        self.assertEqual(str(ex)[-len(errMsg):], errMsg,
                         "Actual Error did not match expected: \nActual  :%s\nExpected:%s\n----\n Occured in: \n%s" % (str(ex), errMsg, tb))

    def test_agentWrapper_validation_shouldFail_defaultSchedule_noCheck(self):
        members = {"start": None, "description": None,
                   "default_schedule": None}
        config = {"name": "Agent Name"}
        secrets = {}
        ex, tb = self.__shouldFailValidation(members, config, secrets)
        errMsg = "should have member : check"
        self.assertEqual(str(ex)[-len(errMsg):], errMsg,
                         "Actual Error did not match expected: \nActual  :%s\nExpected:%s\n----\n Occured in: \n%s" % (str(ex), errMsg, tb))

    def test_agentWrapper_validation_shouldFail_scheduleInConfig_noCheck(self):
        members = {"start": None, "description": None, }
        config = {"name": "Agent Name", "schedule": "every_1s"}
        secrets = {}
        ex, tb = self.__shouldFailValidation(members, config, secrets)
        errMsg = "should have member : check"
        self.assertEqual(str(ex)[-len(errMsg):], errMsg,
                         "Actual Error did not match expected: \nActual  :%s\nExpected:%s\n----\n Occured in: \n%s" % (str(ex), errMsg, tb))

    def test_agentWrapper_validation_shouldFail_controlled_noCheck(self):
        members = {"start": None, "description": None, }
        config = {"name": "Agent Name"}
        secrets = {}
        wrapper = self.__shouldPassValidation(members, config, secrets)

        errMsg = "should have member : check"

        ex, tb = utils.expectError(
            lambda: wrapper.setControllerAgent(wrapper),
            "Setting Controller Agent should have failed")
        self.assertEqual(str(ex)[-len(errMsg):], errMsg,
                         "Actual Error did not match expected: \nActual  :%s\nExpected:%s\n----\n Occured in: \n%s" % (str(ex), errMsg, tb))

    def test_agentWrapper_validation_shouldFail_defaultScheduleIsWrongType(self):
        members = {"start": None, "description": None,
                   "default_schedule": 42, "check": None}
        config = {"name": "Agent Name"}
        secrets = {}

        ex, tb = self.__shouldFailValidation(members, config, secrets)
        errMsg = ".default_schedule should be of type <str>, but was <int>"
        self.assertEqual(str(ex)[-len(errMsg):], errMsg,
                         "Actual Error did not match expected: \nActual  :%s\nExpected:%s\n----\n Occured in: \n%s" % (str(ex), errMsg, tb))

    def test_agentWrapper_validation_shouldFail_CheckIsWrongType(self):
        members = {"start": None, "description": None,
                   "default_schedule": None, "check": 42}
        config = {"name": "Agent Name"}
        secrets = {}

        ex, tb = self.__shouldFailValidation(members, config, secrets)
        errMsg = ".check should be of type <%s>, but was <int>" % MethodType.__name__
        self.assertEqual(str(ex)[-len(errMsg):], errMsg,
                         "Actual Error did not match expected: \nActual  :%s\nExpected:%s\n----\n Occured in: \n%s" % (str(ex), errMsg, tb))

    def test_agentWrapper_validation_shouldFail_scheduleInConfig_wrongType(self):
        members = {"start": None, "description": None,
                   "default_schedule": None, "check": None}
        config = {"name": "Agent Name", "schedule": 1}
        secrets = {}

        ex, tb = self.__shouldFailValidation(members, config, secrets)
        errMsg = ".schedule should be of type <str> but was <int>"
        self.assertEqual(str(ex)[-len(errMsg):], errMsg,
                         "Actual Error did not match expected: \nActual  :%s\nExpected:%s\n----\n Occured in: \n%s" % (str(ex), errMsg, tb))

    def test_agentWrapper_validation_shouldFail_secrets_WrongVarName(self):
        members = {"start": None, "description": None,
                   "secrets": None, "uses_secret_variables": ["TEST_VAR"]}
        config = {"name": "Agent Name"}
        secrets = {"TEST_VAR_WrongVarName": "Test"}

        ex, tb = self.__shouldFailValidation(members, config, secrets)
        errMsg = "\"Not all keys were found : ['TEST_VAR']\""
        self.assertEqual(str(ex), errMsg,
                         "Actual Error did not match expected: \nActual  :%s\nExpected:%s\n----\n Occured in: \n%s" % (str(ex), errMsg, tb))

    def test_agentWrapper_validation_shouldFail_secrets_usedVarsNotAList(self):
        members = {"start": None, "description": None,
                   "uses_secret_variables": {"TEST_VAR": "42"}}
        config = {"name": "Agent Name"}
        secrets = {"TEST_VAR": "Test"}

        ex, tb = self.__shouldFailValidation(members, config, secrets)
        errMsg = "should be of type <list>, but was <dict>"
        self.assertEqual(str(ex)[-len(errMsg):], errMsg,
                         "Actual Error did not match expected: \nActual  :%s\nExpected:%s\n----\n Occured in: \n%s" % (str(ex), errMsg, tb))

    def test_agentWrapper_validation_shouldFail_secrets_usedVarNamesNotStrings(self):
        members = {"start": None, "description": None,
                   "uses_secret_variables": [42]}
        config = {"name": "Agent Name"}
        secrets = {"42": "Test"}

        ex, tb = self.__shouldFailValidation(members, config, secrets)
        errMsg = "Agent Secrets Variable Request <42> should be of type <str> but was <int>"
        self.assertEqual(str(ex)[-len(errMsg):], errMsg,
                         "Actual Error did not match expected: \nActual  :%s\nExpected:%s\n----\n Occured in: \n%s" % (str(ex), errMsg, tb))

    def test_agentWrapper_validation_shouldFail_validate_options_wrongType(self):
        members = {"start": None, "description": None,
                   "validate_options": 42, "default_options": None, "options": None}
        config = {"name": "Agent Name"}
        secrets = {}

        ex, tb = self.__shouldFailValidation(members, config, secrets)
        errMsg = ".validate_options should be of type <%s>, but was <int>" % MethodType.__name__
        self.assertEqual(str(ex)[-len(errMsg):], errMsg,
                         "Actual Error did not match expected: \nActual  :%s\nExpected:%s\n----\n Occured in: \n%s" % (str(ex), errMsg, tb))

    def test_agentWrapper_validation_shouldFail_noOptionSource(self):
        members = {"start": None, "description": None,
                   "options": None}
        config = {"name": "Agent Name"}
        secrets = {}

        ex, tb = self.__shouldFailValidation(members, config, secrets)
        errMsg = "should have member : default_options"
        self.assertEqual(str(ex)[-len(errMsg):], errMsg,
                         "Actual Error did not match expected: \nActual  :%s\nExpected:%s\n----\n Occured in: \n%s" % (str(ex), errMsg, tb))

    def test_agentWrapper_validation_shouldFail_setWallet_withNonWallet(self):
        members = {"start": None, "description": None,
                   "wallet": None, "uses_wallet": True}
        config = {"name": "Agent Name", "options": {}}
        secrets = {"WALLET_KEY": "TestKey"}
        wallet = 42
        wrapper = self.__shouldPassValidation(members, config, secrets)
        errMsg = "should be of type <WalletWrapper> but was <int>"

        ex, tb = utils.expectError(lambda: wrapper.setWallet(wallet),
                                   "Setting wallet should have failed")

        self.assertEqual(str(ex)[-len(errMsg):], errMsg,
                         "Actual Error did not match expected: \nActual  :%s\nExpected:%s\n----\n Occured in: \n%s" % (str(ex), errMsg, tb))

    def test_agentWrapper_validation_shouldFail_setWallet_withWalletInsteadOfWalletWrapper(self):
        members = {"start": None, "description": None,
                   "wallet": None, "uses_wallet": True}
        config = {"name": "Agent Name", "options": {}}
        secrets = {"WALLET_KEY": "TestKey"}
        wallet = mocks.TestWallet()
        wrapper = self.__shouldPassValidation(members, config, secrets)
        errMsg = "should be of type <WalletWrapper> but was <TestWallet>"

        ex, tb = utils.expectError(lambda: wrapper.setWallet(wallet),
                                   "Setting wallet should have failed")

        self.assertEqual(str(ex)[-len(errMsg):], errMsg,
                         "Actual Error did not match expected: \nActual  :%s\nExpected:%s\n----\n Occured in: \n%s" % (str(ex), errMsg, tb))

    def test_agentWrapper_validation_shouldFail_checkDependenciesMissing_raises(self):
        members = {"start": None, "description": None,
                   "check_dependencies_missing": utils.funcToMethod(
                       lambda: utils.raiseErr(Exception("Dependancy Missing")))}
        config = {"name": "Agent Name", "options": {}}
        secrets = {}
        ex, tb = self.__shouldFailValidation(members, config, secrets)
        errMsg = "Agent 'Agent Name' has missing dependencies: Dependancy Missing"

        self.assertEqual(str(ex)[-len(errMsg):], errMsg,
                         "Actual Error did not match expected: \nActual  :%s\nExpected:%s\n----\n Occured in: \n%s" % (str(ex), errMsg, tb))

    def test_agentWrapper_validation_shouldFail_validateOptions_raises(self):
        members = {"start": None, "description": None,
                   "options": None, "default_options": None,
                   "validate_options": utils.funcToMethod(
                       lambda: utils.raiseErr(Exception("Invalid Options")))}
        config = {"name": "Agent Name"}
        secrets = {}
        ex, tb = self.__shouldFailValidation(members, config, secrets)
        errMsg = "validate_options of AgentMock failed : Invalid Options"

        self.assertEqual(str(ex)[-len(errMsg):], errMsg,
                         "Actual Error did not match expected: \nActual  :%s\nExpected:%s\n----\n Occured in: \n%s" % (str(ex), errMsg, tb))

    def test_agentWrapper_validation_shouldFail_receive_wrongType(self):
        members = {"start": None, "description": None,
                   "receive": 42}
        config = {"name": "Agent Name", "options": {}}
        secrets = {}
        wrapper = self.__shouldPassValidation(members, config, secrets)

        ex, tb = utils.expectError(lambda: wrapper.receiveEventsFrom(wrapper),
                                   "receiveEventsFrom Wrapper should fail if 'receive' is not a method")

        errMsg = ".receive should be of type <%s>, but was <int>" % MethodType.__name__

        self.assertEqual(str(ex)[-len(errMsg):], errMsg,
                         "Actual Error did not match expected: \nActual  :%s\nExpected:%s\n----\n Occured in: \n%s" % (str(ex), errMsg, tb))

    def test_agentWrapper_validation_shouldFail_receive_wrongSenderType(self):
        members = {"start": None, "description": None,
                   "receive": None}
        config = {"name": "Agent Name", "options": {}}
        secrets = {}
        wrapper = self.__shouldPassValidation(members, config, secrets)

        ex, tb = utils.expectError(lambda: wrapper.receiveEventsFrom(42),
                                   "receiveEventsFrom Wrapper should fail if 'receive' is not a method")

        errMsg = "Agent Event Sender <42> should be of type <AgentWrapper> but was <int>"

        self.assertEqual(str(ex)[-len(errMsg):], errMsg,
                         "Actual Error did not match expected: \nActual  :%s\nExpected:%s\n----\n Occured in: \n%s" % (str(ex), errMsg, tb))

    def test_agentWrapper_validation_shouldFail_receive_senderIsNone(self):
        members = {"start": None, "description": None,
                   "receive": None}
        config = {"name": "Agent Name", "options": {}}
        secrets = {}
        wrapper = self.__shouldPassValidation(members, config, secrets)

        ex, tb = utils.expectError(lambda: wrapper.receiveEventsFrom(None),
                                   "receiveEventsFrom Wrapper should fail if 'receive' is not a method")

        errMsg = "Agent Event Sender <None> should be of type <AgentWrapper> but was <NoneType>"

        self.assertEqual(str(ex)[-len(errMsg):], errMsg,
                         "Actual Error did not match expected: \nActual  :%s\nExpected:%s\n----\n Occured in: \n%s" % (str(ex), errMsg, tb))
