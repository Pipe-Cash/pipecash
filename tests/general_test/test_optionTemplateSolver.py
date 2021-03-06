import unittest
import sys

from pipecash.optionTemplateSolver import templateSolverInstance
from pipecash import logWrapper

from tests import utils
from tests.logMock import LogMock

logMock = LogMock(logWrapper.loggerInstance)


class OptionTemplateSolverTest(unittest.TestCase):

    def __test_output(self, line):
        self.logs.append(str(line))

    variables = {
        "a": 10,
        "b": 5,
        "s": "s",
    }

    def test_emptyBrackets_shouldProduce_emptyBrackets(self):
        self.__solving_A_shouldProduce_B('{{}}', '{{}}')

    def test_normalString_shouldProduce_normalString(self):
        self.__solving_A_shouldProduce_B('normal string', 'normal string')

    def test_42_shouldProduce_42(self):
        self.__solving_A_shouldProduce_B(42, 42)

    def test_True_shouldProduce_True(self):
        self.__solving_A_shouldProduce_B(True, True)

    def test_VariableA_shouldProduce_ValueOfA(self):
        self.__solving_A_shouldProduce_B('{{a}}', 10)

    def test_StrOnVarA_shouldProduce_StrA(self):
        self.__solving_A_shouldProduce_B('{{str(a)}}', '10')

    def test_APlusB_shouldProduce_Sum(self):
        self.__solving_A_shouldProduce_B('{{a+b}}', 15)

    def test_VariableInText_shouldProduce_SameText(self):
        self.__solving_A_shouldProduce_B(
            'in the {{a}} middle', 'in the {{a}} middle')

    def test_VariableInWord_shouldProduce_SameText(self):
        self.__solving_A_shouldProduce_B('also mi{{a}}ddle', 'also mi{{a}}ddle')

    def test_StrOnAPlusS_shouldProduce_10s(self):
        self.__solving_A_shouldProduce_B('{{str(a)+s}}', '10s')

    def test_IncorrectFormatting_shouldProduce_NoChange(self):
        self.__solving_A_shouldProduce_B('{ {a}}', '{ {a}}')

    def test_VarS_shouldProduce_ValS(self):
        self.__solving_A_shouldProduce_B('{{s}}', 's')

    def test_SPlusS_shouldProduce_SS(self):
        self.__solving_A_shouldProduce_B('{{s+s}}', 'ss')

    def test_RangeB_shouldProduce_ZeroToFour(self):
        self.__solving_A_shouldProduce_B(
            '{{list(range(b))}}', [0, 1, 2, 3, 4])

    def test_LenOfStr_shouldProduce_2(self):
        self.__solving_A_shouldProduce_B('{{len(s+s)}}', 2)

    def test_StringConstantsCombined_shouldProduce_ABC(self):
        self.__solving_A_shouldProduce_B("{{'ab' + 'c'}}", 'abc')

    def __solving_A_shouldProduce_B(self, a, b):
        results = templateSolverInstance.solveOptions(
            {"data": a}, self.variables)
        resultData = results["data"]
        assertMessage = "Expected resolving of %s\nto produce: %s\nbut it was: %s" % (
            repr(a), repr(b), resultData)
        self.assertEqual(resultData, b, assertMessage)

    def test_solving_UndefinedVariable_shlouldLogException(self):
        self.__solving_A_shlouldLogException("{{c}}")

    def test_solving_DevisionByTwo_shlouldLogException(self):
        self.__solving_A_shlouldLogException("{{1/0}}")

    def test_solving_SumStringAndInt_shlouldLogException(self):
        self.__solving_A_shlouldLogException("{{s+a}}")

    def test_TwoTagsNextToEachOther_shlouldLogException(self):
        self.__solving_A_shlouldLogException("{{1}}{{2}}")

    def test_TwoTagsFarFromEachOther_shlouldLogException(self):
        self.__solving_A_shlouldLogException("{{1}} Same Text {{a}}")


    def __solving_A_shlouldLogException(self, expression):
        msgStart = "Failed to evaluate expression"
        msgExMarker = "Exception: "

        with logMock:
            results = templateSolverInstance.solveOptions(
                {"data": expression}, self.variables)
            resultData = results["data"]


        self.assertEqual(len(logMock.logs), 1, "Expected exactly 1 warning message")

        expected = "".join([
            msgStart,
            " '", 
            expression[2:-2], 
            "'\n\twith data ", 
            str(self.variables), 
            "\n\tException: '",
            resultData,
            "'"
        ])
        self.assertEqual(logMock.logs[0], expected, "Message was not as expected.")

        exceptionIndex = logMock.logs[0].index(msgExMarker)+len(msgExMarker)
        exceptionMsg = logMock.logs[0][exceptionIndex:]

