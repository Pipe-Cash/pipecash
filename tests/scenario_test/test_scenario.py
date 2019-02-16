import unittest

from pipecash.scenario import Scenario

from pipecash import pipeScheduler
from pipecash import pipeObserver


class ScenarioTest(unittest.TestCase):

    scenarioPath = "./tests/scenario_test/test_scenario.json"

    def setUp(self):
        pipeScheduler.schedulerInstance = pipeScheduler.Scheduler()
        pipeObserver.observerInstance = pipeObserver.Observer()

    def test_loadScenario(self):
        scenario = Scenario(self.scenarioPath, {})
        scenario.start()

    def test_loadScenario_checkNames(self):
        scenario = Scenario(self.scenarioPath, {})
        scenario.start()

        agentNames = [
            'Agent 0 - has wallet',
            'Agent 1 - receive',
            'Agent 2 - receive',
            'Agent 3 - controled'
        ]
        self.assertListEqual([i.name for i in scenario.agents], agentNames)

        walletNames = ['Test Wallet 0', 'Test Wallet 1 - unused']
        self.assertListEqual([i.name for i in scenario.wallets], walletNames)

    def test_loadScenario_walletsOnlyWhereConfigured(self):
        scenario = Scenario(self.scenarioPath, {})
        scenario.start()

        wallets = [scenario.wallets[0].wallet, None, None, None]
        self.assertListEqual(
            [i.agent.wallet for i in scenario.agents], wallets)
        walletWraps = [scenario.wallets[0], None, None, None]
        self.assertListEqual(
            [i.walletWrapper for i in scenario.agents], walletWraps)

    def test_loadScenario_calledMethods(self):
        scenario = Scenario(self.scenarioPath, {})
        scenario.start()

        calledAgentMethods = [
            ['validate_options', 'check_dependencies_missing', 'start'],
            ['validate_options', 'check_dependencies_missing', 'start'],
            ['validate_options', 'check_dependencies_missing', 'start'],
            ['validate_options', 'check_dependencies_missing', 'start'],
        ]
        for i in range(len(scenario.agents)):
            self.assertListEqual(
                scenario.agents[i].agent.calledMethods, calledAgentMethods[i])
        calledWalletMethods = [
            ['validate_options', 'check_dependencies_missing', 'start'],
            ['validate_options', 'check_dependencies_missing', 'start'],
        ]
        for i in range(len(scenario.wallets)):
            self.assertListEqual(
                scenario.wallets[i].wallet.calledMethods, calledWalletMethods[i])

    def test_loadScenario_options(self):
        scenario = Scenario(self.scenarioPath, {})
        scenario.start()

        agentOptions = [{"foo": "bar"}, {"foo": "bar"},
                        {"foo": "default_value"}, {}]
        self.assertListEqual(
            [i.agent.options for i in scenario.agents], agentOptions)

        walletOptions = [{}, {"foo": "default_value"}]
        self.assertListEqual(
            [i.wallet.options for i in scenario.wallets], walletOptions)

    def test_loadScenario_schedule(self):
        scenario = Scenario(self.scenarioPath, {})
        scenario.start()

        scheduledTasks = pipeScheduler.schedulerInstance._Scheduler__scheduledTasks
        keysWithTasks = [
            s for s in scheduledTasks if len(scheduledTasks[s]) > 0]

        self.assertListEqual(sorted(keysWithTasks),
                             sorted(["every_1s", "every_2s", "every_5s", "every_10s"]))

        self.assertListEqual([len(scheduledTasks[k])
                              for k in keysWithTasks], [1, 1, 1, 1])

    def test_loadScenario_eventsAndControl(self):
        scenario = Scenario(self.scenarioPath, {})
        scenario.start()

        id0 = scenario.agents[0]._AgentWrapper__id
        id1 = scenario.agents[1]._AgentWrapper__id
        id2 = scenario.agents[2]._AgentWrapper__id

        listeners = pipeObserver.observerInstance._Observer__listeners

        self.assertEqual(len(listeners), 3)

        listeners0 = listeners[str((None, 'Event', id0))]
        listeners1 = listeners[str((None, 'Event', id1))]
        listeners2 = listeners[str((None, 'Event', id2))]

        self.assertEqual(len(listeners0), 2)
        self.assertEqual(len(listeners1), 1)
        self.assertEqual(len(listeners2), 1)

        self.assertListEqual(listeners0, [
            scenario.agents[1]._AgentWrapper__receiveEvent,
            scenario.agents[2]._AgentWrapper__receiveEvent
        ])

        self.assertListEqual(
            listeners1, [scenario.agents[3]._AgentWrapper__receiveControlEvent])
        self.assertListEqual(
            listeners2, [scenario.agents[3]._AgentWrapper__receiveControlEvent])
