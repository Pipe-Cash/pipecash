from __future__ import absolute_import, print_function

import schedule as pythonScheduler
import threading

from types import MethodType
import time

from pipecash import validationUtils as validate
from pipecash.observedMethod import observedMethodInstance as obs


class Scheduler:
    __secondsPerLetter = {"s": 1, "m": 60, "h": 60*60, "d": 60*60*24}

    __stop = False

    def everyScheduleToSeconds(self, sch):
        every, t = str(sch).split("_")
        if(every != "every" or len(t) < 2):
            raise LookupError(
                "Can't parse schedule '%s' as seconds" % str(sch))
        num = int(t[0:-1])
        letter = t[-1:]
        return num * self.__secondsPerLetter[letter]

    def atScheduleToTime(self, sch):
        if(sch == "midnight"):
            return "00:00"
        if(sch == "noon"):
            return "12:00"
        hour = int(sch[0:-2])
        isPM = sch[-2:] == "pm"
        return "%i:00" % (hour + (12 if isPM else 0))

    @obs.observedMethod
    def __init__(self):
        self.__knownSchedules_every = [
            "every_1s", "every_2s", "every_5s", "every_10s", "every_30s",
            "every_1m", "every_2m", "every_5m", "every_10m", "every_30m",
            "every_1h", "every_2h", "every_5h", "every_12h",
            "every_1d", "every_2d", "every_7d", "every_30d"
        ]
        self.__knownSchedules_at = [
            "midnight", "1am", "2am", "3am", "4am", "5am",
            "6am", "7am", "8am", "9am", "10am", "11am",
            "noon", "1pm", "2pm", "3pm", "4pm", "5pm",
            "6pm", "7pm", "8pm", "9pm", "10pm", "11pm",
        ]

        self.__knownSchedules_other = ["never"]

        self.__knownSchedules_every_s = [self.everyScheduleToSeconds(
            i) for i in self.__knownSchedules_every]
        self.__knownSchedules_at_time = [
            self.atScheduleToTime(i) for i in self.__knownSchedules_at]
        self.__knownSchedules = self.__knownSchedules_every + \
            self.__knownSchedules_at + self.__knownSchedules_other
        self.__scheduledTasks = dict((k, []) for k in self.__knownSchedules)

    def isKnownSchedule(self, sch):
        return sch in self.knownSchedules()

    def knownSchedules(self):
        return list(self.__knownSchedules)

    @obs.observedMethod
    def registerTask(self, sch, task):
        if(not self.isKnownSchedule(sch)):
            raise IndexError("Unknown schedule '%s'" % str(sch))
        validate.objectMember(task, "__call__")
        self.__scheduledTasks[sch].append(task)

    @obs.observedMethod
    def start(self):
        self.__stop = False
        for sch in self.__knownSchedules_every:
            if any(self.__scheduledTasks[sch]):
                index = self.__knownSchedules_every.index(sch)
                s = self.__knownSchedules_every_s[index]
                self.__everyNSeconds_do(s, sch)
        for sch in self.__knownSchedules_at:
            if any(self.__scheduledTasks[sch]):
                index = self.__knownSchedules_at.index(sch)
                time = self.__knownSchedules_at_time[index]
                self.__eachDayAtTime_do(time, sch)

        thread = threading.Thread(target=self.__schedulerLoop)
        thread.setName("SCH")
        thread.start()

    def __schedulerLoop(self):
        while not self.__stop:
            pythonScheduler.run_pending()
            time.sleep(1)

    def __everyNSeconds_do(self, seconds, schedule):
        pythonScheduler.every(seconds).seconds.do(lambda: self.__job(schedule))

    def __eachDayAtTime_do(self, time, schedule):
        pythonScheduler.every().day.at(time).do(lambda: self.__job(schedule))

    @obs.observedMethod
    def stop(self):
        self.__stop = True

    def __job(self, triggeredSchedule):
        if self.__stop is True:
            return
        tasks = self.__scheduledTasks[triggeredSchedule]
        threads = []
        for t in tasks:
            thread = threading.Thread(target=t)
            thread.setName("SCH(%s)" % triggeredSchedule)
            thread.start()
            threads.append(thread)
        for t in threads:
            t.join()


schedulerInstance = Scheduler()
