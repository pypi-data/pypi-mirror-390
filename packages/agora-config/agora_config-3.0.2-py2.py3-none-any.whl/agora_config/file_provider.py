import json
import pathlib
import tempfile
from agora_logging import logger
from .dict_of_dict import DictOfDict
import os
import __main__


class FileProvider(DictOfDict):
    """
    Provides configuration settings using a specific file.  Internally the file is 'AEA.json'
    which is either the primary config file or the alternate config file.  Contents of the
    file must be valid json.
    """
    def __init__(self, filename, override_path=None):
        super().__init__()
        self.override = False
        if override_path is None:
            try:
                main_stript_path = __main__.__file__
                base_directory = os.path.dirname(os.path.abspath(main_stript_path))
            except:
                main_stript_path = "."
                base_directory = os.path.abspath(main_stript_path)
        else:
            self.override = True
            base_directory = override_path
        self.config_file = os.path.abspath(base_directory + '/' + "AEA.json")
        if filename == "AEA.json":
            self.primary = True
        else:
            self.primary = False
        self.last_modified_time = 0
        self.__read_config()

    # private methods

    def __read_config(self) -> dict:
        """
        Reads the configuration file
        """
        self.clear()
        file_path = pathlib.Path(self.config_file)
        if file_path.exists():
            data = file_path.read_text()
            try:
                self.merge(json.loads(data))
            except Exception as e:
                logger.exception(
                    e, f"Could not load config file '{file_path}' : {str(e)}")
                self.clear()
