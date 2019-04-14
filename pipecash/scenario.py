from __future__ import absolute_import, print_function

import json
import importlib
import inspect

from pipecash import walletWrapper
from pipecash import agentWrapper
from pipecash import validationUtils as validate

from pipecash.observedMethod import observedMethodInstance as obs


class Scenario():

    @obs.observedMethod
    def __init__(self, path):
        with open(path, "r") as read_file:
            scenarioJson = json.load(read_file)
        self.name = scenarioJson["name"]
        self.description = scenarioJson["description"]
        self.author = scenarioJson["author"]

        for i in ["wallets", "agents", "wallet_links", "event_links", "control_links"]:
            validate.dictMember(scenarioJson, i, list)

        self.walletsJson = scenarioJson["wallets"]
        self.agentsJson = scenarioJson["agents"]
        self.wallet_links = scenarioJson["wallet_links"]
        self.event_links = scenarioJson["event_links"]
        self.control_links = scenarioJson["control_links"]

    def prepareToStart(self, secrets):
        self.secrets = secrets

        self.wallets = [walletWrapper.WalletWrapper(self.__parseWallet(w), w, secrets) for w in self.walletsJson]
        self.agents = [agentWrapper.AgentWrapper(self.__parseAgent(a), a, secrets) for a in self.agentsJson]

        for wLink in self.wallet_links:
            validate.objectType(wLink, dict, "Wallet Link")
            validate.dictMember(wLink, "source", int)
            validate.dictMember(wLink, "target", int)
            w = self.wallets[wLink["source"]]
            a = self.agents[wLink["target"]]
            a.setWallet(w)

        for eLink in self.event_links:
            validate.objectType(eLink, dict, "Event Link")
            validate.dictMember(eLink, "source", int)
            validate.dictMember(eLink, "target", int)
            source = self.agents[eLink["source"]]
            receiver = self.agents[eLink["target"]]
            receiver.receiveEventsFrom(source)

        for cLink in self.control_links:
            validate.objectType(cLink, dict, "Control Link")
            validate.dictMember(cLink, "source", int)
            validate.dictMember(cLink, "target", int)
            source = self.agents[cLink["source"]]
            receiver = self.agents[cLink["target"]]
            receiver.setControllerAgent(source)
        
    @obs.observedMethod
    def getNeededSecrets(self):

        wallets = [self.__parseWallet(w) for w in self.walletsJson]
        agents = [self.__parseAgent(a) for a in self.agentsJson]

        namesOfSecrets = []
        for i in wallets + agents:
            if hasattr(i, "uses_secret_variables"):
                namesOfSecrets = namesOfSecrets + i.uses_secret_variables

        namesOfSecrets = list(set(namesOfSecrets)) # unique names only
        return namesOfSecrets

    @obs.observedMethod
    def start(self):
        for w in self.wallets[::-1]:
            w.start()
        for a in self.agents[::-1]:
            a.start()

    def __parseWallet(self, walletJson):
        validate.dictMember(walletJson, "module", str)
        validate.dictMember(walletJson, "type", str)
        walletType = self.importClass(
            walletJson["module"], walletJson["type"])
        walletObject = walletType()

        return walletObject

    def __parseAgent(self, agentJson):
        validate.dictMember(agentJson, "module", str)
        validate.dictMember(agentJson, "type", str)
        agentType = self.importClass(
            agentJson["module"], agentJson["type"])
        agentObject = agentType()

        return agentObject

    @obs.observedMethod
    def importClass(self, moduleToImport, classToImport):
        module = importlib.import_module(moduleToImport)
        classes = inspect.getmembers(module, inspect.isclass)
        for cl in classes:
            if cl[0] == classToImport:
                return cl[1]

        raise Exception("Module %s doesn't contain class %s" % (
            moduleToImport, classToImport))
