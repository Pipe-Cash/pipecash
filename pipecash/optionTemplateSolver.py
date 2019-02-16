from __future__ import absolute_import, print_function

import re
import copy

from pipecash import logWrapper


class OptionTemplateSolver:
    regexPattern = re.compile('({{[^}]+}})')

    def solveOptions(self, optionDict, templateGlobals):
        result = {}
        templateGlobals = copy.deepcopy(templateGlobals)

        for o in optionDict.keys():
            solution = self.solve(optionDict[o], templateGlobals)
            result[o] = solution
        return result

    def solve(self, rawTemplate, templateGlobals):
        template = str(rawTemplate)
        matches = self.regexPattern.findall(template)

        if matches is None or len(matches) == 0:
            return rawTemplate

        for match in matches[::-1]:  # iterate in reversed order
            expression = match[2:-2]
            try:
                evaluation = eval(expression, templateGlobals)
                template = template.replace(match, str(evaluation))
            except Exception as ex:
                logWrapper.loggerInstance.warning(
                    "Failed to evaluate expression '%s'\n\twith data %s\n\tException: '%s'" % (
                        expression, str(templateGlobals), str(ex)))

        return template


templateSolverInstance = OptionTemplateSolver()
