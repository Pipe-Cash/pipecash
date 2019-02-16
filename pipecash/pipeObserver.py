from __future__ import absolute_import, print_function

import threading

from pipecash import logWrapper


class Observer:
    __listeners = {}

    def __init__(self):
        self.__listeners = {}

    def listen(self, area, name, state, callback):
        '''Subscribe to the observed event.
        When the event occurs, the callback will be called.
        'None' value is considered a wildcard and will match
        all patterns in that position. If 3 None values are
        passed for area, name and state, the callback will
        be called on all events.

        The callback will receive 5 arguments:
        > area, name, state, sender, data'''

        key = str((area, name, state))
        if key not in self.__listeners:
            self.__listeners[key] = []
        self.__listeners[key].append(callback)

    def trigger(self, area, name, state, sender, data):
        '''
        Trigger the observed event.
        Notifies the observer that something has happened.
            area - where did it happen
            name - name of the event
            state - state of the event
            sender - the object asociated with the event
            data - details about the event
        '''

        keys = self.__getAllMatchingKeys(area, name, state)
        for k in keys:
            if k in self.__listeners:
                callbacks = self.__listeners[k]
                threads = []
                for c in callbacks:
                    thread = threading.Thread(target=lambda: self.__call(
                        c, area, name, state, sender, data))
                    thread.setName("OBS")
                    thread.start()
                    threads.append(thread)
                for t in threads:
                    t.join()

    def __call(self, callback, area, name, state, sender, data):
        try:
            callback(area, name, state, sender, data)
        except Exception as ex:
            logWrapper.loggerInstance.error(
                "ObserverCallbackError - %s\nData: %s \nError: %s" % (
                    repr([area, name, state]), repr(data), ex))

    def __getAllMatchingKeys(self, a, b, c):
        _ = None
        patterns = [
            (a, b, c), (_, b, c), (a, _, c), (a, b, _),
            (a, _, _), (_, b, _), (_, _, c), (_, _, _),
        ]
        keys = list(set([str(p) for p in patterns]))
        return keys


observerInstance = Observer()
