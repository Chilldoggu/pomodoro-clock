import logging

class Log():
    def __init__(self) -> None:
        self.logObj = logging.getLogger(__name__)
        self.logObj.setLevel(logging.DEBUG)

        self.formatter = logging.Formatter("[%(levelname)s] %(asctime)s - %(message)s")

        self.file_handler = logging.FileHandler('logs.log')
        self.file_handler.setFormatter(self.formatter)

        self.logObj.addHandler(self.file_handler)

