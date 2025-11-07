class UtilsJWTException(Exception):
    pass


class IncorrectTokenError(UtilsJWTException):
    pass


class TTLTokenExpiredError(UtilsJWTException):
    pass


class WrongTypeToken(UtilsJWTException):
    pass


class UnknownError(UtilsJWTException):
    pass


class NotValidSession(UtilsJWTException):
    pass
