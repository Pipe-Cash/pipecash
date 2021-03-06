from __future__ import absolute_import, print_function

from pipecash import scenario
from pipecash import secretsManager
from pipecash import pipeObserver
from pipecash import observedMethod
from pipecash import logWrapper
from pipecash import pipeScheduler

import time
import json

def Run(scenariopath, secretspath, loglevel=1, agentloglevel=1, walletloglevel=1):

    if(secretspath is not None):
        secrets = secretsManager.SecretsManager.loadFromFile(secretspath)
    else:
        secrets = secretsManager.SecretsManager({})

    observedMethod.observedMethodInstance.observerInstance = pipeObserver.observerInstance
    pipeObserver.observerInstance.listen(
        None, None, None, logWrapper.observerPrint)

    logWrapper.loggerInstance.setLevel(loglevel)
    logWrapper.agentLoggerInstance.setLevel(agentloglevel)
    logWrapper.walletLoggerInstance.setLevel(walletloglevel)

    logWrapper.loggerInstance.info("Starting PipeCash...")

    sc = scenario.Scenario(scenariopath)
    sc.prepareToStart(secrets)
    sc.start()

    pipeScheduler.schedulerInstance.start()
    while(True):
        time.sleep(1)

def createSecretsFile(scenariopath, secretspath):
    sc = scenario.Scenario(scenariopath)
    namesOfSecrets = sc.getNeededSecrets()
    secretsDict = dict(zip(namesOfSecrets, [ "" ] * len(namesOfSecrets)))
    secretsJson = json.dumps(secretsDict, indent=2)

    if secretspath == None:
        print(secretsJson)
    else:
        with open(secretspath, "w") as writeFile:
            writeFile.write(secretsJson)