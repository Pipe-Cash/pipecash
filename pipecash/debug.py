path_to_scenario = "<path to scenario.json>"
path_to_secrets = "<path to secrets.json>"

from pipecash import runner

runner.Run(
    scenariopath=path_to_scenario,
    secretspath=path_to_secrets)