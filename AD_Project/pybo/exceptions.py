class PyboServiceError(Exception):
    status_code = 400
    code = 'service_error'
    default_message = '요청을 처리할 수 없습니다.'

    def __init__(self, message=None):
        super().__init__(message or self.default_message)


class AuthenticationRequiredError(PyboServiceError):
    status_code = 401
    code = 'authentication_required'
    default_message = '로그인이 필요합니다.'


class InvalidCredentialsError(PyboServiceError):
    status_code = 400
    code = 'invalid_credentials'
    default_message = '아이디 또는 비밀번호가 올바르지 않습니다.'


class NotFoundError(PyboServiceError):
    status_code = 404
    code = 'not_found'
    default_message = '대상을 찾을 수 없습니다.'


class ValidationError(PyboServiceError):
    status_code = 400
    code = 'validation_error'
