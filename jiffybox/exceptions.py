class JiffyException(Exception):
    """
    Generic Exception
    """
    pass


class JiffyMessageException(JiffyException):
    """
    Container for error messages from the API
    """
    pass


class JiffyAttributeException(JiffyException):
    """
    Missing attribute when constructing an object
    """
    pass
