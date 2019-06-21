import unittest
import time


from pipecash.agentWrapper import AgentWrapper
from pipecash import logWrapper

import tests.agent_test.mockAgents as mockAgents
from tests.logMock import LogMock

logMock = LogMock(logWrapper.loggerInstance)


class TransformEventTest(unittest.TestCase):

    def test_eventTransformation_extend(self):
        sender = mockAgents.EventCreator_MockAgent()
        target = mockAgents.EventReceiver_MockAgent()

        senderWrap = AgentWrapper(sender, {
            "name": "sender",
            "options": {
                "name": "sender",
                "event": {"data": 3.14}
            },
            "transform_event": "{{ { 'DaTa':data, 'extra':'yeah' } }}"
        }, {})
        
        targetWrap = AgentWrapper(target, {
            "name": "target",
            "options": {
                "name": "target",
                "eventData": "{{DaTa}}",
                "extraEventData": "{{extra}}"
            }
        }, {})

        targetWrap.receiveEventsFrom(senderWrap)

        senderWrap.start()
        targetWrap.start()

        with logMock:
            senderWrap._AgentWrapper__runCheck()
            time.sleep(0.005)

        expectedSenderMethods = [
            'validate_options', 'check_dependencies_missing', 'start', 'check'
        ]
        expectedTargetMethods = [
            'validate_options', 'check_dependencies_missing', 'start', 'receive'
        ]

        self.assertListEqual(sender.calledMethods, expectedSenderMethods,
                             "Checking called methods of sender...")
        self.assertListEqual(target.calledMethods, expectedTargetMethods,
                             "Checking called methods of target...")

        self.maxDiff = None
        self.assertListEqual(logMock.logs, [
            'Running [Check] on EventCreator_MockAgent',
            'EventCreator_MockAgent options evaluated to: ' + repr({'name': 'sender', 'event': "{'data': 3.14}"}),
            "EventCreator_MockAgent created event: " + repr({'DaTa': '3.14', 'extra': 'yeah'}),
            'Running [Receive] on EventReceiver_MockAgent',
            "EventReceiver_MockAgent options evaluated to: " + repr({'name': 'target', 'eventData': '3.14', 'extraEventData': 'yeah'}),
        ])

        self.assertListEqual(target.receivedData, [3.14])
        self.assertEqual(target.events, [str({'DaTa': 3.14, 'extra': 'yeah'})])

    def test_eventTransformation_split(self):
        sender = mockAgents.EventCreator_MockAgent()
        target = mockAgents.EventReceiver_MockAgent()

        senderWrap = AgentWrapper(sender, {
            "name": "sender",
            "options": {
                "name": "sender",
                "event": { "data": {"listOfData": [1,2,3,4,5] } }
            },
            "transform_event": "{{ [{'index':i} for i in data['listOfData']] }}"
        }, {})
        
        targetWrap = AgentWrapper(target, {
            "name": "target",
            "options": {
                "name": "target",
                "eventData": "{{index}}"
            }
        }, {})

        targetWrap.receiveEventsFrom(senderWrap)

        senderWrap.start()
        targetWrap.start()

        with logMock:
            senderWrap._AgentWrapper__runCheck()
            time.sleep(0.005)

        expectedSenderMethods = [
            'validate_options', 'check_dependencies_missing', 'start', 'check'
        ]
        expectedTargetMethods = [
            'validate_options', 'check_dependencies_missing', 'start', 'receive', 'receive', 'receive', 'receive', 'receive'
        ]

        self.assertListEqual(sender.calledMethods, expectedSenderMethods,
                             "Checking called methods of sender...")
        self.assertListEqual(target.calledMethods, expectedTargetMethods,
                             "Checking called methods of target...")

        self.maxDiff = None
        self.assertListEqual(logMock.logs, [
            'Running [Check] on EventCreator_MockAgent',
            'EventCreator_MockAgent options evaluated to: ' + repr({'name': 'sender', 'event': repr({ "data": {"listOfData": [1,2,3,4,5] } })}),
            "EventCreator_MockAgent created event: " + repr({'index': '1'}),
            'Running [Receive] on EventReceiver_MockAgent',
            "EventReceiver_MockAgent options evaluated to: " + repr({'name': 'target', 'eventData': '1'}),
            "EventCreator_MockAgent created event: " + repr({'index': '2'}),
            'Running [Receive] on EventReceiver_MockAgent',
            "EventReceiver_MockAgent options evaluated to: " + repr({'name': 'target', 'eventData': '2'}),
            "EventCreator_MockAgent created event: " + repr({'index': '3'}),
            'Running [Receive] on EventReceiver_MockAgent',
            "EventReceiver_MockAgent options evaluated to: " + repr({'name': 'target', 'eventData': '3'}),
            "EventCreator_MockAgent created event: " + repr({'index': '4'}),
            'Running [Receive] on EventReceiver_MockAgent',
            "EventReceiver_MockAgent options evaluated to: " + repr({'name': 'target', 'eventData': '4'}),
            "EventCreator_MockAgent created event: " + repr({'index': '5'}),
            'Running [Receive] on EventReceiver_MockAgent',
            "EventReceiver_MockAgent options evaluated to: " + repr({'name': 'target', 'eventData': '5'}),
        ])

        self.assertListEqual(target.receivedData, [1, 2, 3, 4, 5])
        self.assertEqual(target.events, [
            "{'index': 1}",
            "{'index': 2}",
            "{'index': 3}",
            "{'index': 4}",
            "{'index': 5}"
        ])
