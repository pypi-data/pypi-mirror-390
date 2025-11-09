import configparser
import os
from importlib import resources

class ConfigManager:
    """
    This reads the pipeline.cfg file and makes its settings accessible anywhere.
    """

    def __init__(self, config_path: str = None):
        self.config = configparser.ConfigParser()

        # setting default project root
        if config_path is None:
            base_dir = resources.files("omnicart_pipeline")  # goes up one folder
            config_path = os.path.join(base_dir, "pipeline.cfg")

        # checking if the file exist
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}") 

        # Reading the file if it exists
        self.config.read(config_path) 
        

    @property
    def base_url(self):
        """This method returns the base url of the API"""
        return self.config.get("api","base_url",fallback="")

    @property
    def pagination_limit(self):
        """This returns the pagination limit (as an integer)"""
        return self.config.getint("api","pagination_limit",fallback=10)  

    @property
    def log_level(self):
        """This returns the logging level (such as:- INFO, DEBUG etc)"""
        return self.config.get("logging","level",fallback = "INFO")

    @property
    def log_file(self):
        """This returns the log file path"""
        return self.config.get("logging","log_file",fallback = "pipeline.log")



