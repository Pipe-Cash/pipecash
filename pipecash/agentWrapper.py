from __future__ import absolute_import, print_function

from types import MethodType
from uuid import uuid4
from threading import Lock

from pipecash import validationUtils as validate
from pipecash import walletWrapper
from pipecash import optionTemplateSolver
from pipecash import pipeObserver
from pipecash import pipeScheduler
from pipecash import logWrapper

from pipecash.observedMethod import observedMethodInstance as obs


class AgentWrapper:

    @obs.observedMethod
    def __init__(self, _agent, _configuration, _secrets):

        self.__lock = Lock()
        self.__id = hash(id(self))

        self.walletWrapper = None
        self.options = {}
        self.propagate_origin_event = False
        self.configuration = _configuration
        self.agent = _agent

        # Use "__class__" instead of "type()" for Python2 compatablity
        self.type = self.agent.__class__.__name__
        validate.dictMember(self.configuration, "name", str)
        self.name = self.configuration["name"]

        validate.objectMember(self.agent, "start", MethodType)
        validate.objectMember(self.agent, "description", str)

        self.__initOptions()
        self.__initSchedule()
        self.__initSecrets(_secrets)
        self.__checkDependencies()
        self.__initEventConfiguration()
        self.__initConditions()
        self.__initExtendEvent()

    @obs.observedMethod
    def start(self):
        self.agent.start(logWrapper.agentLoggerInstance)

    @obs.observedMethod
    def setWallet(self, _walletWrapper):
        validate.objectMember(self.agent, "wallet")
        validate.objectMember(self.agent, "uses_wallet", bool, True)
        self.walletWrapper = _walletWrapper
        validate.objectType(self.walletWrapper,
                            walletWrapper.WalletWrapper, "Agent Wallet")
        self.agent.wallet = self.walletWrapper.wallet

    @obs.observedMethod
    def receiveEventsFrom(self, _sender):
        validate.objectMember(self.agent, "receive", MethodType)
        validate.objectType(_sender, AgentWrapper, "Agent Event Sender")
        pipeObserver.observerInstance.listen(
            None, "Event", _sender.__id, self.__receiveEvent)

    @obs.observedMethod
    def setControllerAgent(self, _sender):
        validate.objectMember(self.agent, "check", MethodType)
        validate.objectType(_sender, AgentWrapper, "Agent Controller")
        pipeObserver.observerInstance.listen(
            None, "Event", _sender.__id, self.__receiveControlEvent)

    def isWorking(self):
        return self.__lock.locked()

    def __createEvent(self, eventDict):
        if type(eventDict) is not dict:
            logWrapper.loggerInstance.warning(
                "Agent '%s' created an event of a wrong type (%s). Ignoring." % (
                    self.name, type(eventDict)))
            return

        if not self.__checkCondition("event_condition"):
            return

        if hasattr(self, "extend_event") and self.extend_event is not None:
            eventDict = self.__mergeDictionaries(self.extend_event, eventDict)

        pipeObserver.observerInstance.trigger(
            self.name, "Event", self.__id, self, eventDict)

    def __getEventCreator(self, currentEvent=None):
        if self.propagate_origin_event is not True:
            return self.__createEvent
        elif currentEvent is None:
            return self.__createEvent
        else:
            return lambda newEvent: self.__createEvent(self.__mergeDictionaries(currentEvent, newEvent))

    def __receiveEvent(self, area, name, state, sender, eventData):
        if not self.__checkCondition("receive_condition"):
            return

        logWrapper.loggerInstance.info(
            "Running [Receive] on " + self.agent.__class__.__name__)
        create_event = self.__getEventCreator(eventData)
        self.__runAction(lambda: self.agent.receive(eventData, create_event), "Receive_Event", True, eventData)

    def __receiveControlEvent(self, area, name, state, sender, eventData):
        if not self.__checkCondition("control_condition"):
            return

        logWrapper.loggerInstance.info(
            "Running [Check] on " + self.agent.__class__.__name__)
        create_event = self.__getEventCreator(eventData)
        self.__runAction(lambda: self.agent.check(create_event), "Control_Check", True, eventData)

    def __runCheck(self, *args):
        logWrapper.loggerInstance.info(
            "Running [Check] on " + self.agent.__class__.__name__)
        create_event = self.__getEventCreator(None)
        self.__runAction(lambda: self.agent.check(create_event), "Scheduled_Check", False, {})

    def __runAction(self, action, actionName, solveOptions=False, eventData={}):
        self.__lock.acquire()

        originalOptions = self.options
        if solveOptions:
            solvedOptions = optionTemplateSolver.templateSolverInstance.solveOptions(
                originalOptions, eventData)
            self.agent.options = solvedOptions

        try:
            action()
        except Exception as ex:
            pipeObserver.observerInstance.trigger(
                self.type, actionName, "Error", self, ex)
        finally:
            self.agent.options = originalOptions
            self.__lock.release()

    def __checkCondition(self, conditionName):
        result = False

        if not hasattr(self, conditionName):
            return True
        condition = getattr(self, conditionName)
        if condition is None:
            return True

        try:
            result = condition()
            if result == True:
                return True
            elif result == False:
                logWrapper.loggerInstance.debug(
                    "event_condition on %s retuned False" % (
                        self.agent.__class__.__name__))
                return False
            else:
                raise AssertionError("Evaluation result must be True or False")
        except Exception as ex:
            logWrapper.loggerInstance.error("Failed to check %s = %s.\n%s" % (
                conditionName, self.configuration[conditionName], str(ex)))
            return False

    def __initSecrets(self, _secrets):
        if "uses_secret_variables" in self.configuration:
            validate.dictMember(self.configuration,
                                "uses_secret_variables", list)
            if not hasattr(self.agent, "uses_secret_variables"):
                self.agent.uses_secret_variables = []
            else:
                validate.objectMember(
                    self.agent, "uses_secret_variables", list)
            for varName in self.configuration["uses_secret_variables"]:
                self.agent.uses_secret_variables.append(varName)

        if hasattr(self.agent, "uses_secret_variables"):
            validate.objectMember(self.agent, "uses_secret_variables", list)
            if len(self.agent.uses_secret_variables) > 0:
                for i in self.agent.uses_secret_variables:
                    validate.objectType(
                        i, str, "Agent Secrets Variable Request")
                self.secrets = _secrets.get(*self.agent.uses_secret_variables)
                self.agent.secrets = self.secrets

    def __initOptions(self):
        if not hasattr(self.agent, "options"):
            return

        if "options" in self.configuration:
            validate.dictMember(self.configuration, "options", dict)
            validate.objectMember(self.agent, "options")
            self.agent.options = self.configuration["options"]
        else:
            validate.objectMember(self.agent, "default_options", dict)
            self.agent.options = self.agent.default_options

        self.options = self.agent.options

        if(hasattr(self.agent, "validate_options")):
            validate.objectMember(self.agent, "validate_options", MethodType)
            try:
                self.agent.validate_options()
            except Exception as ex:
                raise Exception("validate_options of %s failed : " %
                                self.type + str(ex))

    def __initSchedule(self):
        if hasattr(self.agent, "default_schedule") or "schedule" in self.configuration:
            validate.objectMember(self.agent, "check", MethodType)
            if "schedule" in self.configuration:
                validate.dictMember(self.configuration, "schedule", str)
                pipeScheduler.schedulerInstance.registerTask(
                    self.configuration["schedule"],
                    self.__runCheck)
            elif hasattr(self.agent, "default_schedule"):
                validate.objectMember(self.agent, "default_schedule", str)
                pipeScheduler.schedulerInstance.registerTask(
                    self.agent.default_schedule,
                    self.__runCheck)

    def __initEventConfiguration(self):
        if "propagate_origin_event" in self.configuration:
            validate.dictMember(self.configuration,
                                "propagate_origin_event", bool)
            self.propagate_origin_event = self.configuration["propagate_origin_event"]

    def __initConditions(self):
        _secrets = None
        if hasattr(self.agent, "secrets"):
            _secrets = self.agent.secrets

        if "event_condition" in self.configuration:
            validate.dictMember(self.configuration, "event_condition", str)
            self.event_condition = self.__getConditionEvaluatorFunc(
                self.configuration["event_condition"],
                _secrets)
        if "receive_condition" in self.configuration:
            validate.objectMember(self.agent, "receive", MethodType)
            validate.dictMember(self.configuration, "receive_condition", str)
            self.receive_condition = self.__getConditionEvaluatorFunc(
                self.configuration["receive_condition"],
                _secrets)
        if "control_condition" in self.configuration:
            validate.objectMember(self.agent, "check", MethodType)
            validate.dictMember(self.configuration, "control_condition", str)
            self.control_condition = self.__getConditionEvaluatorFunc(
                self.configuration["control_condition"],
                _secrets)

    def __initExtendEvent(self):
        if "extend_event" in self.configuration:
            validate.dictMember(self.configuration, "extend_event", dict)
            self.extend_event = self.configuration["extend_event"]

    def __getConditionEvaluatorFunc(self, condition, secrets):
        addon = {}
        if secrets is not None:
            addon = {"secrets": secrets}

        def solve(globsDict): return bool(optionTemplateSolver.templateSolverInstance.solve(
            condition, self.__mergeDictionaries(globsDict, addon)))
        return solve

    def __checkDependencies(self):
        if hasattr(self.agent, "check_dependencies_missing"):
            validate.objectMember(
                self.agent, "check_dependencies_missing", MethodType)
            try:
                self.agent.check_dependencies_missing()
            except Exception as ex:
                raise EnvironmentError(
                    "Agent '%s' has missing dependencies: " % self.name + str(ex))

    def __mergeDictionaries(self, dict1, dict2):
        result = dict1.copy()   # start with dict1's keys and values
        # modifies result with dict2's keys and values & returns None
        result.update(dict2)
        return result
