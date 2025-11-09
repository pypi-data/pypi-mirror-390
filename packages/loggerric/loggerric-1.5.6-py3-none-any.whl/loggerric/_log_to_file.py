from enum import Enum, auto
from colorama import Fore
import os, re

def escape_ansi(text:str) -> str:
    """
    **Used to escape ansi (terminal color).**

    *Parameters*:
    - `text` (str): The text including the ansi.

    *Example*:
    ```python
    no_ansi = escape_ansi(text='myTextThatIncludesAnsi')
    ```
    """
    regex = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return regex.sub('', text)

class LogToFileLevel(Enum):
    """
    **Enums used for file logging.**
    """
    INFO = auto()
    WARN = auto()
    ERROR = auto()
    DEBUG = auto()
    PRETTY_PRINT = auto()
    TABLE = auto()
    PROGRESS_BAR = auto()
    TIMER = auto()
    PROMPT = auto()

class LogToFile:
    """
    **Contains methods for the automatic file logging.**
    """
    _active_levels = {
        LogToFileLevel.INFO, LogToFileLevel.WARN, LogToFileLevel.ERROR, LogToFileLevel.DEBUG, LogToFileLevel.PROMPT,
        LogToFileLevel.PRETTY_PRINT, LogToFileLevel.TABLE, LogToFileLevel.PROGRESS_BAR, LogToFileLevel.TIMER,
    }

    _should_dump = False
    _dump_path = os.path.join(os.getenv('HOMEDRIVE'), os.getenv('HOMEPATH'), 'loggerric_log_dump.log')

    @classmethod
    def set_dump_location(cls, full_directory:str, file_name:str) -> None:
        """
        **Set a location for the log file.**

        *Parameters*:
        - `full_directory` (str): Full path to the parent directory of the log file.
        - `file_name` (str): File name for the log, without extension.

        *Example*:
        ```python
        LogToFile.set_dump_location(full_directory='C:/Users', file_name='important_file')
        ```
        """
        assert os.path.exists(full_directory), f'Directory "{full_directory}" does not exist!'
        
        cls._dump_path = os.path.join(full_directory, file_name + '.log')

    @classmethod
    def start_logging(cls) -> None:
        """
        **Start logging to file.**
        """
        cls._should_dump = True

        print(f'{Fore.BLUE}Logging To File: {Fore.GREEN}Started{Fore.RESET}')

    @classmethod
    def stop_logging(cls) -> None:
        """
        **Stop logging to file.**
        """
        cls._should_dump = False

        print(f'{Fore.BLUE}Logging To File: {Fore.RED}Stopped{Fore.RESET}')

    @classmethod
    def enable(cls, levels:LogToFileLevel) -> None:
        """
        **Enable levels to log.**

        *Parameters*:
        - `levels` (LogToFileLevel): The levels to enable.

        *Example*:
        ```python
        LogToFile.enable(LogToFileLevel.WARN, ...)
        ```
        """
        cls._active_levels.update(levels)

    @classmethod
    def disable(cls, levels:LogToFileLevel) -> None:
        """
        **Disable levels to log.**

        *Parameters*:
        - `levels` (LogToFileLevel): The levels to disable.

        *Example*:
        ```python
        LogToFile.disable(LogToFileLevel.TIMER, ...)
        ```
        """
        cls._active_levels.difference_update(levels)

    @classmethod
    def _log(cls, data:str) -> None:
        if data:
            with open(cls._dump_path, 'a+t') as file:
                file.write(str(data) + '\n')