import time


class MockAgent:

    def start(self, log):
        self.calledMethods.append(self.start.__name__)
        self.log = log
        pass

    def __init__(self):
        self.calledMethods = []
        self.events = []
        self.description = "Test Agent " + self.__class__.__name__
        self.options = {}
        self.default_options = {}

    def validate_options(self):
        self.calledMethods.append(self.validate_options.__name__)

    def check(self, create_event):
        self.calledMethods.append(self.check.__name__)

    def receive(self, event, create_event):
        self.events.append(str(event))
        self.calledMethods.append(self.receive.__name__)

    def check_dependencies_missing(self):
        self.calledMethods.append(self.check_dependencies_missing.__name__)


class ThreadingTest_MockAgent(MockAgent):
    counter = 0

    def start(self, log):
        MockAgent.start(self, log)
        self.counter = 0

    def check(self, create_event):
        c = self.counter
        time.sleep(0.001)
        self.counter = c + 1
        return MockAgent.check(self, create_event)

    def receive(self, event, create_event):
        c = self.counter
        time.sleep(0.002)
        self.counter = c + 1
        return MockAgent.receive(self, event, create_event)


class EventReceiver_MockAgent(MockAgent):

    def __init__(self):
        MockAgent.__init__(self)
        self.receivedData = []
        self.default_options = {
            "eventData": "{{data}}"
        }

    def check(self, create_event):
        self.receivedData.append(self.options["eventData"])
        return MockAgent.check(self, create_event)

    def receive(self, event, create_event):
        self.receivedData.append(self.options["eventData"])
        return MockAgent.receive(self, event, create_event)


class EventCreator_MockAgent(MockAgent):

    def __init__(self):
        MockAgent.__init__(self)
        self.default_options = {
            "event": {"data": 42}
        }
        self.event_description = { "data": 42 }

    def check(self, create_event):
        create_event(self.options["event"])
        return MockAgent.check(self, create_event)

    def receive(self, event, create_event):
        create_event(self.options["event"])
        return MockAgent.receive(self, event, create_event)
