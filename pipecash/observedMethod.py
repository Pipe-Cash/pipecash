from __future__ import absolute_import, print_function


class ObservedMethod:
    observerInstance = None

    def observedMethod(self, functionOrMethod):

        def wrapper(*args, **kwargs):

            if(self.observerInstance == None):
                return functionOrMethod(*args, **kwargs)

            name = functionOrMethod.__name__

            className = None
            argNames = functionOrMethod.__code__.co_varnames
            if(argNames != None
                    and len(argNames) > 0
                    and argNames[0] == 'self'):
                selfArg = args[0]
                className = selfArg.__class__.__name__

            argsToLog = args
            if(className is not None):
                argsToLog = argsToLog[1:]

            result = None
            try:
                self.observerInstance.trigger(className, name, "Start", functionOrMethod, {
                                              'args': argsToLog, 'kwargs': kwargs})
                result = functionOrMethod(*args, **kwargs)
                self.observerInstance.trigger(
                    className, name, "Done", functionOrMethod, {'result': result})
            except Exception as error:
                self.observerInstance.trigger(
                    className, name, "Error", functionOrMethod, {'error': error})
                raise
            return result

        return wrapper


observedMethodInstance = ObservedMethod()
