from __future__ import absolute_import, print_function


def objectMember(validatedObject, memberName, expectedType=None, expectedValue=None):

    if not hasattr(validatedObject, memberName):
        message = "%s should have member : %s" % (validatedObject, memberName)
        raise TypeError(message)
    if expectedType is not None:
        member = getattr(validatedObject, memberName)
        memType = type(member)
        if memType.__name__ == "unicode":
            memType = str
        if memType.__name__ == "instance":
            memType = member.__class__
        message = "Member %s.%s should be of type <%s>, but was <%s>" % (
            type(validatedObject), memberName, expectedType.__name__, memType.__name__)
        if memType != expectedType:
            raise TypeError(message)
    if expectedValue is not None:
        if getattr(validatedObject, memberName) != expectedValue:
            message = "Value of %s.%s should be : %s" % (
                type(validatedObject), memberName, expectedValue)
            raise ValueError(message)


def dictMember(validatedDictionary, memberName, expectedType=None, expectedValue=None):
    if memberName not in validatedDictionary:
        message = "%s should have member : %s" % (dict, memberName)
        raise TypeError(message)
    if expectedType is not None:
        memType = type(validatedDictionary[memberName])
        if memType.__name__ == "unicode":
            memType = str
        if memType.__name__ == "instance":
            memType = validatedDictionary[memberName].__class__
        message = "Member %s.%s should be of type <%s> but was <%s>" % (
            memType, memberName, expectedType.__name__, memType.__name__)
        if memType != expectedType:
            raise TypeError(message)
    if expectedValue is not None:
        if validatedDictionary[memberName] != expectedValue:
            message = "Value of %s.%s should be : %s" % (
                dict, memberName, expectedValue)
            raise ValueError(message)


def objectType(validatedObject, expectedType, whatIsThisObject_str="Object"):
    objType = type(validatedObject)
    if objType.__name__ == "unicode":
        objType = str
    if objType.__name__ == "instance":
        objType = validatedObject.__class__

    message = "%s <%s> should be of type <%s> but was <%s>" % (
        whatIsThisObject_str, validatedObject, expectedType.__name__, objType.__name__)

    if not issubclass(objType, expectedType):
        raise TypeError(message)
