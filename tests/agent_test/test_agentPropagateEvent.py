import unittest
import time


from pipecash.agentWrapper import AgentWrapper
from pipecash import logWrapper
from pipecash import pipeObserver

import tests.agent_test.mockAgents as mockAgents
from tests.logMock import LogMock

logMock = LogMock(logWrapper.loggerInstance)


class AgentPropagateTest(unittest.TestCase):

    def test_eventPropagation(self):
        sender1 = mockAgents.EventCreator_MockAgent()
        sender2 = mockAgents.EventCreator_MockAgent()
        target = mockAgents.EventReceiver_MockAgent()

        senderWrap1 = AgentWrapper(sender1, {
            "name": "sender1",
            "options": {
                "name": "sender1",
                "event": {"data": 3.14}
            }
        }, {})

        senderWrap2 = AgentWrapper(sender2, {
            "name": "sender2",
            "options": {
                "name": "sender2",
                "event": {"extraData": 42}
            },
            "propagate_origin_event": True
        }, {})

        targetWrap = AgentWrapper(target, {
            "name": "target",
            "options": {
                "name": "target",
                "eventData": "{{data}}"
            }
        }, {})

        senderWrap2.receiveEventsFrom(senderWrap1)
        targetWrap.receiveEventsFrom(senderWrap2)

        senderWrap1.start()
        senderWrap2.start()
        targetWrap.start()

        with logMock:
            senderWrap1._AgentWrapper__runCheck()
            time.sleep(0.005)

        expectedSender1Methods = [
            'validate_options', 'check_dependencies_missing', 'start', 'check'
        ]
        expectedSender2Methods = [
            'validate_options', 'check_dependencies_missing', 'start', 'receive'
        ]
        expectedTargetMethods = [
            'validate_options', 'check_dependencies_missing', 'start', 'receive'
        ]

        self.assertListEqual(sender1.calledMethods, expectedSender1Methods,
                             "Checking called methods of sender1...")
        self.assertListEqual(sender2.calledMethods, expectedSender2Methods,
                             "Checking called methods of sender2...")
        self.assertListEqual(target.calledMethods, expectedTargetMethods,
                             "Checking called methods of target...")
        self.assertListEqual(target.receivedData, ["3.14"])
        self.assertListEqual(logMock.logs, [
            "Running [Check] on EventCreator_MockAgent",
            "Running [Receive] on EventCreator_MockAgent",
            "Running [Receive] on EventReceiver_MockAgent"
        ])
        self.assertEqual(sender2.events, [str({'data': 3.14})])
        self.assertEqual(target.events, [str({'data': 3.14, 'extraData': 42})])
