

class TestAgent:

    def start(self, log):
        self.calledMethods.append(self.start.__name__)
        self.log = log
        pass

    def __init__(self):
        self.calledMethods = []
        self.events = []

        self.options = {}
        self.wallet = None
        self.description = ""
        self.event_description = {}
        self.default_options = {'foo': "default_value"}
        self.uses_wallet = True
        self.uses_secret_variables = []
        self.secrets = {}

    def validate_options(self):
        self.calledMethods.append(self.validate_options.__name__)

    def check(self, create_event):
        self.calledMethods.append(self.check.__name__)

    def receive(self, event, create_event):
        self.events.append(str(event))
        self.calledMethods.append(self.receive.__name__)

    def check_dependencies_missing(self):
        self.calledMethods.append(self.check_dependencies_missing.__name__)


class TestWallet:

    def start(self, log):
        self.calledMethods.append(self.start.__name__)
        self.log = log

    def __init__(self):
        self.calledMethods = []

        self.options = {}
        self.description = ""
        self.default_options = {'foo': "default_value"}
        self.uses_secret_variables = []
        self.secrets = {}

    def validate_options(self):
        self.calledMethods.append(self.validate_options.__name__)

    def check_dependencies_missing(self):
        self.calledMethods.append(self.check_dependencies_missing.__name__)

    def checkBalance(self):
        self.calledMethods.append(self.checkBalance.__name__)

    def send(self, amount, address):
        self.calledMethods.append(self.send.__name__)

    def getReceiveAddress(self):
        self.calledMethods.append(self.getReceiveAddress.__name__)

    def getLatestTransactions(self, numOfTransactions=10, transactionsToSkip=0):
        self.calledMethods.append(self.getLatestTransactions.__name__)
