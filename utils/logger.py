import colorama
import enum


class LogLevel(enum.Enum):
    INFO = 1
    WARNING = 2
    ERROR = 3


class Logger:
    mode = LogLevel.ERROR

    @classmethod
    def init(cls):
        colorama.init()

    @classmethod
    def log(cls, message):
        print(f"{colorama.Fore.LIGHTCYAN_EX}*INFO* {message} {colorama.Fore.RESET}")

    @classmethod
    def warning(cls, message):
        if Logger.mode.value > 1:
            print(f"{colorama.Fore.YELLOW}*WARNING* {message} {colorama.Fore.RESET}")

    @classmethod
    def error(cls, message):
        if Logger.mode.value > 2:
            print(f"{colorama.Fore.RED}*ERROR* {message} {colorama.Fore.RESET}")

