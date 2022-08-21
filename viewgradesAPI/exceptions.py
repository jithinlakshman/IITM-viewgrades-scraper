class CredentialsError(Exception):
    """ Raised when credentials are wrong """
    pass


class ContentNotFoundError(Exception):
    """ Raised when grade data is asked for without logging in """
    pass
