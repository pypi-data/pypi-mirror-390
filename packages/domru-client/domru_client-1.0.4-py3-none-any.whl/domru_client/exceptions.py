class DomRuError(Exception):
    pass


class AuthenticationError(DomRuError):
    pass


class DataFetchError(DomRuError):
    pass