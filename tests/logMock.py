import logging


class HandlerMock(logging.Handler):
    def __init__(self, logCollection):
        self.logCollection = logCollection
        return super(HandlerMock, self).__init__(1)

    def emit(self, record):
        self.logCollection.append(record.msg)


class LogMock():
    logs = []

    def __init__(self, logger):
        self.logger = logger
        self.originalLevel = logger.level
        self.originalHandlers = list(logger.handlers)

    def __enter__(self):
        self.logs = []
        for h in list(self.logger.handlers):
            self.logger.removeHandler(h)
        self.logger.addHandler(HandlerMock(self.logs))
        self.logger.setLevel(1)

    def __exit__(self, type, value, tb):
        for h in list(self.logger.handlers):
            self.logger.removeHandler(h)
        for h in self.originalHandlers:
            self.logger.addHandler(h)
        self.logger.setLevel(self.originalLevel)
