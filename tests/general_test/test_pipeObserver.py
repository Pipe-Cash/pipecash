import unittest
import time

from pipecash import logWrapper
from pipecash.pipeObserver import Observer

from tests import utils
from tests.logMock import LogMock

logMock = LogMock(logWrapper.loggerInstance)


class ObserverTest(unittest.TestCase):

    def setUp(self):
        self.observerInstance = Observer()

    def test_observer_listen(self):
        varName = "test_observer_listen_result"
        self.observerInstance.listen("Tt", "Tt", "Tt",
                                     lambda a, n, s, o, d: setattr(self, varName, d))
        data = 42
        self.observerInstance.trigger("Tt", "Tt", "Tt", self, data)
        time.sleep(0.005)
        result = getattr(self, varName)
        key = "('Tt', 'Tt', 'Tt')"
        self.assertEqual(len(self.observerInstance._Observer__listeners), 1)
        self.assertTrue(key in self.observerInstance._Observer__listeners)
        self.assertEqual(
            len(self.observerInstance._Observer__listeners[key]), 1)
        self.assertEqual(result, data)

    def test_observer_listen_pattern(self):
        varName = "test_observer_listen_pattern_result"
        self.observerInstance.listen("Tt", None, None,
                                     lambda a, n, s, o, d: setattr(self, varName, d))
        data = 42
        self.observerInstance.trigger("Tt", "Tt", "Tt", self, data)
        time.sleep(0.005)
        result = getattr(self, varName)
        key = "('Tt', None, None)"
        self.assertEqual(len(self.observerInstance._Observer__listeners), 1)
        self.assertTrue(key in self.observerInstance._Observer__listeners)
        self.assertEqual(
            len(self.observerInstance._Observer__listeners[key]), 1)
        self.assertEqual(result, data)

    def test_observer_patterns(self):

        fullPattern = ["Tt", "Tt", "Tt"]
        allPatterns = self.observerInstance._Observer__getAllMatchingKeys(
            *fullPattern)
        expectedPatternsAll = [
            '(None, None, None)', "('Tt', 'Tt', 'Tt')",
            "('Tt', 'Tt', None)", "(None, 'Tt', 'Tt')", "('Tt', None, 'Tt')",
            "(None, None, 'Tt')", "('Tt', None, None)", "(None, 'Tt', None)", ]
        self.assertListEqual(sorted(allPatterns), sorted(expectedPatternsAll))

        nPattern = [None, "Tt", "Tt"]
        nPatterns = self.observerInstance._Observer__getAllMatchingKeys(
            *nPattern)
        expectedPatternsN = [
            '(None, None, None)', "(None, 'Tt', 'Tt')",
            "(None, None, 'Tt')", "(None, 'Tt', None)", ]
        self.assertListEqual(sorted(nPatterns), sorted(expectedPatternsN))

        limitedPattern = [None, None, "Tt"]
        limitedPatterns = self.observerInstance._Observer__getAllMatchingKeys(
            *limitedPattern)
        expectedPatternsLimited = [
            '(None, None, None)',
            "(None, None, 'Tt')", ]
        self.assertListEqual(sorted(limitedPatterns),
                             sorted(expectedPatternsLimited))

    def __wait_and_set_data(self, varName, val, secsToSleep):
        time.sleep(secsToSleep)
        setattr(self, varName, val)

    def test_observer_listenMultythreading(self):
        varName = "test_observer_listenMultythreading_result"
        errorName = "test_observer_listenMultythreading_error"

        def getMockFunc(i): return lambda a, n, s, o, d: self.__wait_and_set_data(
            varName + str(i), d, 0.1)

        for i in range(10):
            self.observerInstance.listen(None, "Tt", "Tt", getMockFunc(i))

        key = "(None, 'Tt', 'Tt')"
        self.assertEqual(len(self.observerInstance._Observer__listeners), 1)
        self.assertTrue(key in self.observerInstance._Observer__listeners)
        self.assertEqual(
            len(self.observerInstance._Observer__listeners[key]), 10)

        self.observerInstance.listen("Observer", "Callback", "Error",
                                     lambda a, n, s, o, d: self.__wait_and_set_data(errorName, d, 0))

        data = 42
        self.observerInstance.trigger("Tt", "Tt", "Tt", self, data)

        time.sleep(0.2)

        with self.assertRaises(AttributeError):
            error = getattr(self, errorName)
            self.assertIsNone(error)

        values = [getattr(self, varName + str(i)) for i in range(10)]

        self.assertEqual(values, [data]*10)

    def test_observer_callbackFail(self):

        self.observerInstance.listen("Tt", "Tt", "Tt",
                                     lambda a, n, s, o, d: utils.raiseErr(NotImplementedError(
                                         "Example of a NotImplementedError message")))
        with logMock:
            self.observerInstance.trigger("Tt", "Tt", "Tt", self, None)
            time.sleep(0.005)

        expectedError = "ObserverCallbackError - ['Tt', 'Tt', 'Tt']"
        expectedError += "\nData: None "
        expectedError += "\nError: Example of a NotImplementedError message"

        self.assertEqual(len(logMock.logs), 1)
        self.assertEqual(logMock.logs[0], expectedError)
