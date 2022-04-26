class Response:
    def __init__(self, code, message) -> None:
        self.code = code
        self.message = message
    
    def show(self) -> str:
        print(self.code, self.message)