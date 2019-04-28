import unittest
import time

from pipecash.agentWrapper import AgentWrapper
from pipecash import logWrapper

import tests.agent_test.mockAgents as mockAgents
from tests.logMock import LogMock

logMock = LogMock(logWrapper.loggerInstance)


class AgentControlTest(unittest.TestCase):

    def test_agentControl(self):
        sender = mockAgents.EventCreator_MockAgent()
        target = mockAgents.EventReceiver_MockAgent()

        senderWrap = AgentWrapper(sender, {"name": "MockAgent1"}, {})

        targetWrap = AgentWrapper(target, {"name": "MockAgent2"}, {})

        targetWrap.setControllerAgent(senderWrap)

        senderWrap.start()
        targetWrap.start()

        with logMock:
            senderWrap._AgentWrapper__runCheck()
            time.sleep(0.005)

        expectedSenderMethods = [
            'validate_options', 'check_dependencies_missing', 'start', 'check'
        ]
        expectedTargetMethods = [
            'validate_options', 'check_dependencies_missing', 'start', 'check'
        ]

        self.assertListEqual(sender.calledMethods, expectedSenderMethods,
                             "Checking called methods of sender...")
        self.assertListEqual(target.calledMethods, expectedTargetMethods,
                             "Checking called methods of target...")
        self.assertListEqual(target.receivedData, [42])
        self.assertListEqual(logMock.logs,
            [
                'Running [Check] on EventCreator_MockAgent',
                'EventCreator_MockAgent options evaluated to: ' + repr({'event': "{'data': 42}"}),
                "EventCreator_MockAgent created event: " + repr({'data': '42'}),
                'Running [Check] on EventReceiver_MockAgent',
                "EventReceiver_MockAgent options evaluated to: " + repr({'eventData': '42'}),
            ])
