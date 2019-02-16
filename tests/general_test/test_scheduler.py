import unittest

from tests import utils

from pipecash.pipeScheduler import Scheduler


class PipeSchedulerTest(unittest.TestCase):

    def setUp(self):
        self.schedulerInstance = Scheduler()

    def tearDown(self):
        self.schedulerInstance.stop()

    def test_scheduler_knownSchedules(self):
        knownSchedules_every = [
            "every_1s", "every_2s", "every_5s", "every_10s", "every_30s",
            "every_1m", "every_2m", "every_5m", "every_10m", "every_30m",
            "every_1h", "every_2h", "every_5h", "every_12h",
            "every_1d", "every_2d", "every_7d", "every_30d"
        ]
        knownSchedules_at = [
            "midnight", "1am", "2am", "3am", "4am", "5am",
            "6am", "7am", "8am", "9am", "10am", "11am",
            "noon", "1pm", "2pm", "3pm", "4pm", "5pm",
            "6pm", "7pm", "8pm", "9pm", "10pm", "11pm",
        ]

        for sch in knownSchedules_every + knownSchedules_at:
            self.assertTrue(self.schedulerInstance.isKnownSchedule(sch), "")

        unKnownSchedules = [
            "afternoon", "1:30am", "01:00", "13:00",
            "every 30s", "every_42s", "every_30ms"
            "batman", "", 0, 42, None, {}
        ]

        for sch in unKnownSchedules:
            self.assertFalse(self.schedulerInstance.isKnownSchedule(sch), "")

    def test_scheduler_knownSchedules(self):
        knownSchedules_every = [
            "every_1s", "every_2s", "every_5s", "every_10s", "every_30s",
            "every_1m", "every_2m", "every_5m", "every_10m", "every_30m",
            "every_1h", "every_2h", "every_5h", "every_12h",
            "every_1d", "every_2d", "every_7d", "every_30d"
        ]
        knownSchedules_at = [
            "midnight", "1am", "2am", "3am", "4am", "5am",
            "6am", "7am", "8am", "9am", "10am", "11am",
            "noon", "1pm", "2pm", "3pm", "4pm", "5pm",
            "6pm", "7pm", "8pm", "9pm", "10pm", "11pm",
        ]

        for sch in knownSchedules_every + knownSchedules_at:
            self.assertTrue(self.schedulerInstance.isKnownSchedule(sch), "")

        unKnownSchedules = [
            "afternoon", "1:30am", "01:00", "13:00",
            "every 30s", "every_42s", "every_30ms"
            "batman", "", 0, 42, None, {}
        ]
        for sch in unKnownSchedules:
            self.assertFalse(self.schedulerInstance.isKnownSchedule(sch), "")

    def test_scheduler_nameToSeconds(self):
        secondsPerLetter = {"s": 1, "m": 60, "h": 60*60, "d": 60*60*24}

        letter = 's'
        for letter in ['s', 'm', 'h', 'd']:
            for i in range(0, 60):
                self.assertEqual(
                    self.schedulerInstance.everyScheduleToSeconds(
                        "every_%s%s" % (i, letter)),
                    i * secondsPerLetter[letter])

    def test_scheduler_scheduleSimpleTask(self):
        varName = "test_scheduler_scheduleSimpleTask_1s"

        self.schedulerInstance.registerTask(
            "every_1s",
            lambda: setattr(self, varName, 42))

        self.schedulerInstance.start()

        t = utils.waitLoop(
            "wait for 1s schedule to set the variable",
            2, lambda: hasattr(self, varName))

        var = getattr(self, varName)

        self.assertGreater(t, 0.95)
        self.assertLess(t, 1.05)
        self.assertEqual(var, 42)

    def test_scheduler_scheduleSimpleTask2s(self):
        varName = "test_scheduler_scheduleSimpleTask_2s"
        self.schedulerInstance.registerTask(
            "every_2s",
            lambda: setattr(self, varName, 42))

        self.schedulerInstance.start()

        t = utils.waitLoop(
            "wait for 2s schedule to set the variable",
            3, lambda: hasattr(self, varName))

        var = getattr(self, varName)

        self.assertGreater(t, 1.95)
        self.assertLess(t, 2.05)
        self.assertEqual(var, 42)

    def test_scheduler_scheduleMultipleSimpleTasks(self):
        varName = "test_scheduler_scheduleMultipleSimpleTasks_var"

        for i in [1, 2, 3]:
            setattr(self, varName + str(i), 0)

        self.schedulerInstance.registerTask("every_1s",
                                            lambda: setattr(self, varName + "1", getattr(self, varName + "1") + 1))
        self.schedulerInstance.registerTask("every_1s",
                                            lambda: setattr(self, varName + "2", getattr(self, varName + "2") + 2))
        self.schedulerInstance.registerTask("every_1s",
                                            lambda: setattr(self, varName + "3", getattr(self, varName + "3") + 3))

        # Over 5 seconds, the variables will look like:
        #           1s    2s    3s    4s    5s
        # var 1 =   1,    2,    3,    4,    5
        # var 2 =   2,    4,    6,    8,    10
        # var 3 =   3,    6,    9,    12,   15

        self.schedulerInstance.start()

        t = utils.waitLoop("measure time to set all variables", 7,
                           lambda: getattr(self, varName + "1") == 5 and
                           getattr(self, varName + "2") == 10 and
                           getattr(self, varName + "3") == 15)

        self.assertGreater(t, 4.80, "Time: " + str(t))
        self.assertLess(t, 5.5, "Time: " + str(t))

        variables = [
            getattr(self, varName + "1"),
            getattr(self, varName + "2"),
            getattr(self, varName + "3")
        ]

        for i in [1, 2, 3]:
            self.assertEqual(variables[i-1], 5*i,
                             "Variables: " + str(variables))
