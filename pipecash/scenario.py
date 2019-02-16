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
    def __init__(self, path, secrets):
        self.secrets = secrets

        with open(path, "r") as read_file:
            scenarioJson = json.load(read_file)
        self.name = scenarioJson["name"]
        self.description = scenarioJson["description"]
        self.author = scenarioJson["author"]

        for i in ["wallets", "agents", "wallet_links", "event_links", "control_links"]:
            validate.dictMember(scenarioJson, i, list)

        walletsJson = scenarioJson["wallets"]
        agentsJson = scenarioJson["agents"]
        wallet_links = scenarioJson["wallet_links"]
        event_links = scenarioJson["event_links"]
        control_links = scenarioJson["control_links"]

        self.wallets = [self.__parseWallet(w) for w in walletsJson]
        self.agents = [self.__parseAgent(a) for a in agentsJson]

        for wLink in wallet_links:
            validate.objectType(wLink, dict, "Wallet Link")
            validate.dictMember(wLink, "source", int)
            validate.dictMember(wLink, "target", int)
            w = self.wallets[wLink["source"]]
            a = self.agents[wLink["target"]]
            a.setWallet(w)

        for eLink in event_links:
            validate.objectType(eLink, dict, "Event Link")
            validate.dictMember(eLink, "source", int)
            validate.dictMember(eLink, "target", int)
            source = self.agents[eLink["source"]]
            receiver = self.agents[eLink["target"]]
            receiver.receiveEventsFrom(source)

        for cLink in control_links:
            validate.objectType(cLink, dict, "Control Link")
            validate.dictMember(cLink, "source", int)
            validate.dictMember(cLink, "target", int)
            source = self.agents[cLink["source"]]
            receiver = self.agents[cLink["target"]]
            receiver.setControllerAgent(source)

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

        return walletWrapper.WalletWrapper(walletObject, walletJson, self.secrets)

    def __parseAgent(self, agentJson):
        validate.dictMember(agentJson, "module", str)
        validate.dictMember(agentJson, "type", str)
        agentType = self.importClass(
            agentJson["module"], agentJson["type"])
        agentObject = agentType()

        return agentWrapper.AgentWrapper(agentObject, agentJson, self.secrets)

    @obs.observedMethod
    def importClass(self, moduleToImport, classToImport):
        module = importlib.import_module(moduleToImport)
        classes = inspect.getmembers(module, inspect.isclass)
        for cl in classes:
            if cl[0] == classToImport:
                return cl[1]
        raise ModuleNotFoundError("Module %s doesn't contain class %s" % (
            moduleToImport, classToImport))
