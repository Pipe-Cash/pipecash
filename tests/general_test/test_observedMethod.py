import unittest
import time

from pipecash.observedMethod import ObservedMethod
from pipecash.pipeObserver import Observer

ArgListNoArgs = str({'args': (), 'kwargs': {}})
ArgListWithArgs = str({'args': (1, 2), 'kwargs': {}})

ResultNone = "{'result': None}"
ResultOne = "{'result': 1}"

ExceptoionMsg = "{'error': AssertionError('testing the error',)}"

lines = []
linesFormat = "%s from %s with data: %s"


def __logObservations(area, name, state, sender, data):
    line = linesFormat % (str([area, name, state]), sender.__name__, str(data))
    lines.append(line)


observer = Observer()
obs = ObservedMethod()
obs.observerInstance = observer
observer.listen(None, None, None, __logObservations)


class ObservedMethodTest(unittest.TestCase):

    def __getLine(self, area, name, state, data):
        return linesFormat % (
            repr([area, name, state]), name, data)

    def test_observedFunction_successfulCall(self):
        lines[:] = []
        success()
        self.__waitForLogLines(2)
        expectedLines = sorted([
            self.__getLine(None, "success", "Start", ArgListNoArgs),
            self.__getLine(None, "success", "Done", ResultNone)
        ])
        actualLines = sorted(lines)
        self.assertEqual(actualLines[0], expectedLines[0])
        self.assertEqual(actualLines[1], expectedLines[1])

    def test_observedFunction_withArgs_successfulCall(self):
        lines[:] = []
        success(1, 2)
        self.__waitForLogLines(2)
        expectedLines = sorted([
            self.__getLine(None, "success", "Start", ArgListWithArgs),
            self.__getLine(None, "success", "Done", ResultOne)
        ])
        actualLines = sorted(lines)
        self.assertEqual(actualLines[0], expectedLines[0])
        self.assertEqual(actualLines[1], expectedLines[1])

    def test_observedFunction_failedCall(self):
        lines[:] = []
        try:
            fail()
            self.fail("Call should have thrown an exception")
        except AssertionError:
            pass
        self.__waitForLogLines(2)
        expectedLines = sorted([
            self.__getLine(None, "fail", "Start", ArgListNoArgs),
            self.__getLine(None, "fail", "Error", ExceptoionMsg)
        ])
        actualLines = sorted(lines)
        self.assertEqual(actualLines[0], expectedLines[0])
        self.assertEqual(actualLines[1], expectedLines[1])

    def test_observedFunction_withArgs_failedCall(self):
        lines[:] = []
        try:
            fail(1, 2)
            self.fail("Call should have thrown an exception")
        except AssertionError:
            pass
        self.__waitForLogLines(2)
        expectedLines = sorted([
            self.__getLine(None, "fail", "Start", ArgListWithArgs),
            self.__getLine(None, "fail", "Error", ExceptoionMsg)
        ])
        actualLines = sorted(lines)
        self.assertEqual(actualLines[0], expectedLines[0])
        self.assertEqual(actualLines[1], expectedLines[1])

    def test_observedMethod_successfulCall(self):
        lines[:] = []
        ToObserve().success()
        self.__waitForLogLines(2)
        expectedLines = sorted([
            self.__getLine("ToObserve", "success", "Start", ArgListNoArgs),
            self.__getLine("ToObserve", "success", "Done", ResultNone)
        ])
        actualLines = sorted(lines)
        self.assertEqual(actualLines[0], expectedLines[0])
        self.assertEqual(actualLines[1], expectedLines[1])

    def test_observedMethod_withArgs_successfulCall(self):
        lines[:] = []
        ToObserve().success(1, 2)
        self.__waitForLogLines(2)
        expectedLines = sorted([
            self.__getLine("ToObserve", "success", "Start", ArgListWithArgs),
            self.__getLine("ToObserve", "success", "Done", ResultOne)
        ])
        actualLines = sorted(lines)
        self.assertEqual(actualLines[0], expectedLines[0])
        self.assertEqual(actualLines[1], expectedLines[1])

    def test_observedMethod_failedCall(self):
        lines[:] = []
        try:
            ToObserve().fail()
            self.fail("Call should have thrown an exception")
        except AssertionError:
            pass
        self.__waitForLogLines(2)
        expectedLines = sorted([
            self.__getLine("ToObserve", "fail", "Start", ArgListNoArgs),
            self.__getLine("ToObserve", "fail", "Error", ExceptoionMsg)
        ])
        actualLines = sorted(lines)
        self.assertEqual(actualLines[0], expectedLines[0])
        self.assertEqual(actualLines[1], expectedLines[1])

    def test_observedMethod_withArgs_failedCall(self):
        lines[:] = []
        try:
            ToObserve().fail(1, 2)
            self.fail("Call should have thrown an exception")
        except AssertionError:
            pass
        self.__waitForLogLines(2)
        expectedLines = sorted([
            self.__getLine("ToObserve", "fail", "Start", ArgListWithArgs),
            self.__getLine("ToObserve", "fail", "Error", ExceptoionMsg)
        ])
        actualLines = sorted(lines)
        self.assertEqual(actualLines[0], expectedLines[0])
        self.assertEqual(actualLines[1], expectedLines[1])

    def __waitForLogLines(self, count):
        while(len(lines) < count):
            time.sleep(0.005)
        self.assertEqual(len(lines), count,
                         "Expecred exactly %s lines to be observed, but was %s\nLines:\n%s" % (
            str(count), len(lines), lines))

############################################


@obs.observedMethod
def success(*args):
    if(len(args) > 0):
        return args[0]


@obs.observedMethod
def fail(*args):
    raise AssertionError("testing the error")


class ToObserve:

    @obs.observedMethod
    def success(self, *args):
        if(len(args) > 0):
            return args[0]

    @obs.observedMethod
    def fail(self, *args):
        raise AssertionError("testing the error")
