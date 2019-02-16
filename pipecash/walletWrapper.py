from __future__ import absolute_import, print_function

from types import MethodType

from pipecash import logWrapper
from pipecash import validationUtils as validate

from pipecash.observedMethod import observedMethodInstance as obs


class WalletWrapper:

    @obs.observedMethod
    def __init__(self, _wallet, _configuration, _secrets):
        self.wallet = _wallet
        self.configuration = _configuration

        self.type = type(self.wallet).__name__
        self.name = self.configuration["name"]
        validate.objectType(self.name, str, "Wallet Name")

        validate.objectMember(self.wallet, "start", MethodType)
        validate.objectMember(self.wallet, "checkBalance", MethodType)
        validate.objectMember(self.wallet, "send", MethodType)
        validate.objectMember(self.wallet, "getReceiveAddress", MethodType)
        validate.objectMember(self.wallet, "getLatestTransactions", MethodType)

        self.__initOptions()
        self.__initSecrets(_secrets)
        self.__checkDependencies()

    @obs.observedMethod
    def start(self):
        self.wallet.start(logWrapper.walletLoggerInstance)

    def __initOptions(self):
        if not hasattr(self.wallet, "options"):
            return
        validate.objectMember(self.wallet, "options", dict)
        if "options" in self.configuration:
            validate.dictMember(self.configuration, "options", dict)
            self.wallet.options = self.configuration["options"]
        else:
            validate.objectMember(self.wallet, "default_options", dict)
            self.wallet.options = self.wallet.default_options

        if(hasattr(self.wallet, "validate_options")):
            validate.objectMember(self.wallet, "validate_options", MethodType)
            try:
                self.wallet.validate_options()
            except Exception as ex:
                raise Exception("validate_options of %s failed" %
                                self.type, ex)

    def __initSecrets(self, _secrets):
        if hasattr(self.wallet, "uses_secret_variables"):
            validate.objectMember(self.wallet, "secrets")
            validate.objectMember(self.wallet, "uses_secret_variables", list)
            if len(self.wallet.uses_secret_variables) > 0:
                for i in self.wallet.uses_secret_variables:
                    validate.objectType(
                        i, str, "Wallet Secrets Variable Request")
                secrets = _secrets.get(*self.wallet.uses_secret_variables)
                self.secrets = secrets
                self.wallet.secrets = secrets

    def __checkDependencies(self):
        if hasattr(self.wallet, "check_dependencies_missing"):
            validate.objectMember(
                self.wallet, "check_dependencies_missing", MethodType)
            try:
                self.wallet.check_dependencies_missing()
            except Exception as ex:
                raise EnvironmentError(
                    "Agent '%s' has missing dependencies: " % self.name, ex)

    def __mergeDictionaries(self, dict1, dict2):
        result = dict1.copy()   # start with dict1's keys and values
        # modifies result with dict2's keys and values & returns None
        result.update(dict2)
        return result
