class FileWriteError(Exception):
    def __init__(self, message="Error writing to file."):
        self.message = message
        super().__init__(self.message)
