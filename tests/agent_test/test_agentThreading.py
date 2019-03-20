import unittest
import threading

from pipecash.agentWrapper import AgentWrapper
import tests.agent_test.mockAgents as mockAgents


class AgentThreadingTest(unittest.TestCase):

    def test_agentMustHave_Only1Thread(self):
        agent = mockAgents.ThreadingTest_MockAgent()
        wrapper = AgentWrapper(agent, {"name": "threading-test"}, {})
        wrapper.start()

        calledMethods = ['validate_options',
                         'check_dependencies_missing', 'start']

        self.assertListEqual(agent.calledMethods, calledMethods)
        agent.calledMethods = []

        def do100times(action): return [action() for i in range(100)]

        def run100ChecksLambda(): return do100times(
            lambda: wrapper._AgentWrapper__runCheck())

        def run100ReceivesLambda(): return do100times(
            lambda: wrapper._AgentWrapper__receiveEvent(
                "area", "name", "state", self, {}))

        threads = []
        for i in range(5):
            threads.append(threading.Thread(target=run100ChecksLambda))
            threads.append(threading.Thread(target=run100ReceivesLambda))

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        expectedCount = 5*2*100
        self.assertEqual(agent.counter, expectedCount)
        self.assertEqual(len(agent.calledMethods), expectedCount)
