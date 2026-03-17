from fastapi import HTTPException

class TokenNotFound(HTTPException):
    def __init__(self, status_code = 401, message = "Token not found"):
        super().__init__(status_code, message)

class ExpiredAccessToken(HTTPException):
    def __init__(self, status_code = 401, message = "Your access token is expired!"):
        super().__init__(status_code, message)

class InvalidAccessToken(HTTPException):
    def __init__(self, status_code = 401, message = "Invalid access token!"):
        super().__init__(status_code, message)

class InvalidRefreshToken(HTTPException):
    def __init__(self, status_code = 401, message = "Invalid refresh token!"):
        super().__init__(status_code, message)

class ExpiredRefreshToken(HTTPException):
    def __init__(self, status_code = 401, message = "Expired refresh token!"):
        super().__init__(status_code, message)

class UserCompromisation(HTTPException):
    def __init__(self, status_code = 401, message = "Possible user compromisation! Change your password!"):
        super().__init__(status_code, message)

class InvalidPasswordException(HTTPException):
    def __init__(self, status_code = 401, message = "Invalid password!"):
        super().__init__(status_code, message)