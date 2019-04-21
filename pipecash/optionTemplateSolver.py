from __future__ import absolute_import, print_function

import copy

from pipecash import logWrapper


class OptionTemplateSolver:

    def solveOptions(self, optionDict, templateGlobals):
        result = {}
        templateGlobals = copy.deepcopy(templateGlobals)

        for o in optionDict.keys():
            solution = self.solve(optionDict[o], templateGlobals)
            result[o] = solution
        return result

    def solve(self, rawValue, templateGlobals):
        valueString = str(rawValue).strip()
        isMatch = valueString.startswith("{{") and valueString.endswith("}}") and len(valueString) > 4

        if not isMatch:
            return rawValue

        expression = valueString[2:-2]
        try:
            evaluation = eval(expression, templateGlobals)
            return evaluation
        except Exception as ex:
            templateGlobalsNoBuiltins = { i: templateGlobals[i] for i in templateGlobals if i[0] != "_" }
            logWrapper.loggerInstance.warning(
                "Failed to evaluate expression '%s'\n\twith data %s\n\tException: '%s'" % (
                    expression, str(templateGlobalsNoBuiltins), str(ex)))
            return str(ex)


templateSolverInstance = OptionTemplateSolver()
