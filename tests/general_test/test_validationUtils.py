import unittest

from pipecash import validationUtils as vld


class MyObj(object):
    foo = None


class ValidationUtilsTest(unittest.TestCase):

    def __verify_A_withFunc_F_andArgs_B_shouldPass(self, A, F, *B):
        try:
            F(A, *B)
        except Exception as ex:
            self.fail("Failed Attempt to verify %s with %s(%s)\n\tError: %s" % (
                repr(A), F.__name__, repr(B), ex))

    def __verify_A_withFunc_F_args_B_shouldFail(self, A, F, *B):
        try:
            F(A, *B)
        except Exception as ex:
            print("\nExpected error was cought: " + str(ex))
            return ex

        self.fail("Expected failure when verifying %s with %s(%s)" % (
            repr(A), F.__name__, repr(B)))

    # TESTS FOR SUCCESSFUL VALIDATION

    def test_verify_objectType_42_is_int(self):
        self.__verify_A_withFunc_F_andArgs_B_shouldPass(
            42, vld.objectType, int)

    def test_verify_objectType_42_is_typeof42(self):
        self.__verify_A_withFunc_F_andArgs_B_shouldPass(
            42, vld.objectType, type(42))

    def test_verify_objectType_42_is_int_withDescription(self):
        self.__verify_A_withFunc_F_andArgs_B_shouldPass(
            42, vld.objectType, int, "The Answer")

    def test_verify_objectType_Foo_is_str(self):
        self.__verify_A_withFunc_F_andArgs_B_shouldPass(
            "foo", vld.objectType, str)

    def test_verify_objectType_obj_is_MyObj(self):
        self.__verify_A_withFunc_F_andArgs_B_shouldPass(
            MyObj(), vld.objectType, MyObj)

    def test_verify_objectType_obj_is_parentClass(self):
        self.__verify_A_withFunc_F_andArgs_B_shouldPass(
            MyObj(), vld.objectType, object)

    def test_verify_objectType_None_is_NoneType(self):
        self.__verify_A_withFunc_F_andArgs_B_shouldPass(
            None, vld.objectType, type(None))

    def test_verify_dictMember_dict_Foo_is_str_Bar(self):
        self.__verify_A_withFunc_F_andArgs_B_shouldPass(
            {"foo": "bar"}, vld.dictMember, "foo", str, "bar")

    def test_verify_dictMember_dict_Foo_is_int_42(self):
        self.__verify_A_withFunc_F_andArgs_B_shouldPass(
            {"foo": 42}, vld.dictMember, "foo", int, 42)

    def test_verify_dictMember_dict_Foo_is_None(self):
        self.__verify_A_withFunc_F_andArgs_B_shouldPass(
            {"foo": None}, vld.dictMember, "foo", type(None), None)

    def test_verify_objectMember_dict_Foo_is_str_Bar(self):
        obj = MyObj()
        obj.foo = "bar"
        self.__verify_A_withFunc_F_andArgs_B_shouldPass(
            obj, vld.objectMember, "foo", str, "bar")

    def test_verify_objectMember_dict_Foo_is_int_42(self):
        obj = MyObj()
        obj.foo = 42
        self.__verify_A_withFunc_F_andArgs_B_shouldPass(
            obj, vld.objectMember, "foo", int, 42)

    def test_verify_objectMember_dict_Foo_is_None(self):
        obj = MyObj()
        obj.foo = None
        self.__verify_A_withFunc_F_andArgs_B_shouldPass(
            obj, vld.objectMember, "foo", type(None), None)

    # TESTS FOR FAILED VALIDATION

    def test_verifyFail_objectType_42_is_stringInstance(self):
        ex = self.__verify_A_withFunc_F_args_B_shouldFail(
            42, vld.objectType, "")

    def test_verifyFail_objectType_42_is_noneInstance(self):
        ex = self.__verify_A_withFunc_F_args_B_shouldFail(
            42, vld.objectType, None)

    def test_verifyFail_objectType_42_is_str_withDescription(self):
        ex = self.__verify_A_withFunc_F_args_B_shouldFail(
            42, vld.objectType, str, "The Answer")

    def test_verify_objectType_str_Foo_is_int(self):
        ex = self.__verify_A_withFunc_F_args_B_shouldFail(
            "foo", vld.objectType, int)

    def test_verify_objectType_obj_is_noParamPassed(self):
        ex = self.__verify_A_withFunc_F_args_B_shouldFail(
            MyObj(), vld.objectType)

    def test_verify_objectType_obj_is_intInstance(self):
        ex = self.__verify_A_withFunc_F_args_B_shouldFail(
            MyObj(), vld.objectType, 42)

    def test_verify_objectType_NoneType_is_ofType_NoneType(self):
        ex = self.__verify_A_withFunc_F_args_B_shouldFail(
            type(None), vld.objectType, type(None))

    def test_verify_dictMember_dict_Foo_is_int_Bar(self):
        ex = self.__verify_A_withFunc_F_args_B_shouldFail(
            {"foo": "bar"}, vld.dictMember, "foo", int, "bar")

    def test_verify_dictMember_dict_Foo_is_str_wrongValue(self):
        ex = self.__verify_A_withFunc_F_args_B_shouldFail(
            {"foo": "bar"}, vld.dictMember, "foo", str, "wrong value")

    def test_verify_dictMember_dict_Foo_is_int_strValue(self):
        ex = self.__verify_A_withFunc_F_args_B_shouldFail(
            {"foo": 42}, vld.dictMember, "foo", int, str(42))

    def test_verify_dictMember_dict_Foo_is_noTypeArgPassed(self):
        ex = self.__verify_A_withFunc_F_args_B_shouldFail(
            {"foo": None}, vld.dictMember, "foo", "bar", "baz")

    def test_verify_dictMember_noParams(self):
        ex = self.__verify_A_withFunc_F_args_B_shouldFail(
            {"foo": None}, vld.dictMember)

    def test_verify_objectMember_dict_Foo_is_int_Bar(self):
        obj = MyObj()
        obj.foo = "bar"
        ex = self.__verify_A_withFunc_F_args_B_shouldFail(
            obj, vld.objectMember, "foo", int, "bar")

    def test_verify_objectMember_dict_Foo_is_str_wrongValue(self):
        obj = MyObj()
        obj.foo = "bar"
        ex = self.__verify_A_withFunc_F_args_B_shouldFail(
            obj, vld.objectMember, "foo", str, "wrong value")

    def test_verify_objectMember_dict_Foo_is_int_strValue(self):
        obj = MyObj()
        obj.foo = 42
        ex = self.__verify_A_withFunc_F_args_B_shouldFail(
            obj, vld.objectMember, "foo", int, str(42))

    def test_verify_objectMember_dict_Foo_is_noTypeArgPassed(self):
        obj = MyObj()
        obj.foo = "foo"
        ex = self.__verify_A_withFunc_F_args_B_shouldFail(
            obj, vld.objectMember, "foo", "bar", "baz")

    def test_verify_objectMember_noParams(self):
        obj = MyObj()
        obj.foo = "bar"
        ex = self.__verify_A_withFunc_F_args_B_shouldFail(
            obj, vld.objectMember)
