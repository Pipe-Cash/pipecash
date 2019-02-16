from __future__ import absolute_import, print_function

from pipecash import scenario
from pipecash import secretsManager
from pipecash import pipeObserver
from pipecash import observedMethod
from pipecash import logWrapper
from pipecash import pipeScheduler

import time

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

    sc = scenario.Scenario(scenariopath, secrets)
    sc.start()

    pipeScheduler.schedulerInstance.start()
    while(True):
        time.sleep(1)
