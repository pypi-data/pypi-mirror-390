"""
lib/exceptions.py

Custom exceptions defined here
"""

class SystemCallError(Exception):
    """ Raised when a system call returns a non-zero exit code
    """
    def __init__(self, message):
        super().__init__(message)

class AttributeSetSilentFailError(Exception):
    """ Raised when an attempt to set an attribute of the interface is made without returning an error code
    but where the attribute remains unchanged in actuality
    """
    def __init__(self, message):
        super().__init__(message)

# TEMPLATE --- DELETE IT AFTER, BEBOP!!!
class Error(Exception):
    """
    """
    def __init__(self, message):
        super().__init__(message)
