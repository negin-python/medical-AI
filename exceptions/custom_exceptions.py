class AppException(Exception):
    def __init__(self,message,status_code,error_code):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)