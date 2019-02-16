from __future__ import absolute_import, print_function

import json

from pipecash import validationUtils as validate

from pipecash.observedMethod import observedMethodInstance as obs


class SecretsManager:
    __secrets = {}

    def __init__(self, values):
        self.__secrets = values

    @staticmethod
    def loadFromFile(path):
        with open(path, "r") as read_file:
            secretsValues = json.load(read_file)
            validate.objectType(secretsValues, dict,
                                "The contents of '%s'" % path)
            return SecretsManager(secretsValues)

    @obs.observedMethod
    def hasKey(self, key):
        return key in self.__secrets

    @obs.observedMethod
    def findMissingKeys(self, *keys):
        missingKeys = [k for k in keys if k not in self.__secrets]
        return missingKeys

    @obs.observedMethod
    def get(self, *keys):
        missingKeys = self.findMissingKeys(*keys)
        if len(missingKeys) > 0:
            raise KeyError("Not all keys were found : " + repr(missingKeys))
        return dict((k, self.__secrets[k]) for k in keys)

    @obs.observedMethod
    def getAll(self):
        return self.__secrets
