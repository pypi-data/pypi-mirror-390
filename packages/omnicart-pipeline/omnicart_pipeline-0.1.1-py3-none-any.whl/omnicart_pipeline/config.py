from configparser import ConfigParser
from importlib import resources
from .logging_config import setup_logger
from pathlib import Path


logger = setup_logger(__name__)

class ConfigManager(ConfigParser):
    "A simple ConfigManager class to read my configuration file and provide easy access to the settings"
    
    def __init__(self, file_path:str = "pipeline.cfg") -> None:
        super().__init__()
        self.config_file = self._validate_file_path(file_path)
        self.read(self.config_file)
        
    
    def _validate_file_path(self, file_path:str) -> Path | None:
        """
        A helper function to validate that file infact exists
        Args:
            path (str): A path to the file containing

        Raises:
            FileNotFoundError: This is raised if the path does not exists

        Returns: A valdi path or None
        """
        try:
            cfg_path = resources.files("omnicart_pipeline") / file_path
            
            with resources.as_file(cfg_path) as resolved_path:
                if not resolved_path.exists():
                    logger.exception(f"Configuration File {file_path} not found")
                    raise FileNotFoundError

                return resolved_path
        except Exception as e:
            logger.exception(f"Error locating configuration file {e}")
        # path_obj = Path(path)
        # if not path_obj.exists():
        #     #TODO: Include my logger here
        #     logger.exception(f"The Path to the file does not exist")
        #     raise FileNotFoundError(f"The Path to the file does not exist")
        # return path_obj

    def settings(self, section : str = None) -> dict:
        if section:
            if self.has_section(section):
                return dict(self[section])
            else:
                #TODO: Include my logger here
                logger.exception(f"Section '{section}' not found in config file")
                raise ValueError(f"Section '{section}' not found in config file")
        else:
            return {sec: dict(self[sec]) for sec in self.sections()}