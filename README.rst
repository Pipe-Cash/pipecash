========
PIPECASH
========


.. image:: https://img.shields.io/pypi/v/pipecash.svg
        :target: https://pypi.python.org/pypi/pipecash

.. image:: https://img.shields.io/travis/Pipe-Cash/pipecash.svg
        :target: https://travis-ci.org/Pipe-Cash/pipecash

.. image:: https://readthedocs.org/projects/pipecash/badge/?version=latest
        :target: https://pipecash.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status


.. image:: https://pyup.io/repos/github/Pipe-Cash/pipecash/shield.svg
     :target: https://pyup.io/repos/github/Pipe-Cash/pipecash/
     :alt: Updates



* License: OPEN BLOCKCHAIN-SPECIFIC LICENSE
* Documentation: https://pipecash.readthedocs.io.
* Website: https://pipe.cash.


A framework for easy automation of Bitcoin related tasks. PipeCash is flexible due to it's plugin system and configuration options. Read more at http://pipe.cash/

Description
------------

PipeCash is a framework for automation of Bitcoin Related tasks.

It reads a configuration (json file) and executes the appropriate tasks (called "agents") at the appropriate times, in a way similar to IFTTT.

An agent may be scheduled (to run at specific times), controlled (to run when another agent tells it to), receive event data (when another agent produces an event), or just be started once and run in the background.

Agents represent simple actions:

* Sending an email
* Reading a file
* Getting specific data from the internet
* etc...

An agent can have access to a wallet and use the standard wallet interface to perform a money related task.
Such an agent should work the same, even if it uses a different wallet, or even a different currency.


This package contains the core functionality of PipeCash, needed to run any PipeCash instance.

The package does not contain any PipeCash agents or wallets. They must come from separate packages.

It does not contain any configurations either.
At this stage users will be required to create their own configurations.

Quick Start
------------

Run a scenario:

.. code-block:: bash

   pipecash -s /path/to/scenario.json

If the scenario needs secret variables, generate them:

.. code-block:: bash

   pipecash -s /path/to/scenario.json --createSecretsFile > secrets.json

Once the file is generated, open it and fill the secret variables.
To run the scenario together with the secrets, use:

.. code-block:: bash

   pipecash -s /path/to/scenario.json --secretsPath /path/to/secrets.json

Issues
------
To tell us about a bug, please see the issue template : https://github.com/Pipe-Cash/pipecash/issues/21
