from __future__ import absolute_import, print_function

from datetime import datetime
import logging


def __createLogger(logName):
    logger = logging.getLogger(logName)

    format = '%(asctime)s: [%(threadName)s] [%(levelname)s] %(message)s'

    c_handler = logging.StreamHandler()
    formatter = logging.Formatter(format)
    c_handler.setFormatter(formatter)
    logger.addHandler(c_handler)

    return logger


def observerPrint(area, name, state, sender, data):
    dataMaxLen = 120
    dataStr = str(data)[:dataMaxLen] + \
        ("..." if len(data) > dataMaxLen else "")
    noneStr = "<None>"
    areaStr = noneStr if area is None else str(area)
    nameStr = noneStr if name is None else str(name)
    stateStr = noneStr if state is None else str(state)
    logStr = "%s.%s [%s] with data: \t\t%s" % (
        areaStr, nameStr, stateStr, dataStr)
    if state != "Error":
        loggerInstance.debug(logStr)
    else:
        loggerInstance.error(logStr)


loggerInstance = __createLogger("PipeCash")
agentLoggerInstance = __createLogger("PipeCash Agent")
walletLoggerInstance = __createLogger("PipeCash Wallet")
