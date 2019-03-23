from __future__ import absolute_import, print_function

"""Console script for pipecash."""
import sys
import click
import logging

from pipecash import runner

pathType = click.Path(exists=True, file_okay=True, dir_okay=False, writable=False,
                      readable=True, resolve_path=False, allow_dash=False, path_type=None)

logLevels = ["NOTSET", "DEBUG", "INFO", "WARN", "ERROR", "FATAL"]
logLevelValues = [
    logging.NOTSET, logging.DEBUG, logging.INFO,
    logging.WARN, logging.ERROR, logging.FATAL]

logLevelChoiceType = click.Choice(logLevels, case_sensitive=True)


@click.command()
@click.version_option("0.1.0.1")
@click.option('-s', '--scenarioPath', type=pathType, required=True, help='Path to the scenario JSON file.')
@click.option('--secretsPath', type=pathType, help='Path to the screts JSON file.')
@click.option('--logLevel', default="DEBUG", type=logLevelChoiceType, help="log level for the main log")
@click.option('--agentLogLevel', default="DEBUG", type=logLevelChoiceType, help="log level for the agent log")
@click.option('--walletLogLevel', default="DEBUG", type=logLevelChoiceType, help="log level for the wallet log")
def main(scenariopath, secretspath, loglevel, agentloglevel, walletloglevel):
    """Console script for pipecash."""

    runner.Run(scenariopath, secretspath,
                 logLevelValues[logLevels.index(loglevel)],
                 logLevelValues[logLevels.index(agentloglevel)],
                 logLevelValues[logLevels.index(walletloglevel)]
                 )

    return 0
