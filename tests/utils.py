import time
import sys
import traceback


def expectError(callable, message):
    try:
        callable()
    except Exception as ex:
        tb = traceback.format_exc()
        return ex, tb
    raise AssertionError(
        "Action was successful, but should have failed : %s\n" % message)


def raiseErr(error):
    raise error


def funcToMethod(func):
    class FuncHolder:
        def transformed(*args):
            return func()
    return FuncHolder().transformed


def methodMock(callCollectionObject, func, functionName):
    if not hasattr(callCollectionObject, "calledMethods"):
        callCollectionObject.calledMethods = []

    def mockWrapper(*args):
        callCollectionObject.calledMethods.append(functionName)
        return func(*args)
    return funcToMethod(mockWrapper)


def waitLoop(loop_message, time_s, conditionFunc):
    start = time.time()
    result = False
    while(result != True):
        t = time.time()
        if(t - start > time_s):
            raise TimeOutError(loop_message, time_s)
        result = conditionFunc()
    return time.time() - start


def __try(func):
    def wrapper():
        try:
            func()
            return True
        except Exception as ex:
            return False
    return wrapper


def tryWaitLoop(loop_message, time_s, tryFunc):
    return waitLoop(loop_message, time_s, __try(tryFunc))


class TimeOutError(Exception):
    def __init__(self, message, time_s):
        self.message = "Timed Out iterating on : '%s' after %s s" % (
            message, time_s)
        super(TimeOutError, self).__init__(self.message)
