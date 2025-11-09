import configparser
from pathlib import Path
from importlib import resources

class ConfigManager:
    def __init__(self, config_file):
        self.config_parser = configparser.ConfigParser()

        # current_dir = Path(__file__).parent
        # config_path = current_dir / config_file 

        # # self.config_parser.read(config_path)
        with resources.files('omnicart_pipeline').joinpath(config_file).open('r') as file:
            self.config_parser.read_file(file)

    def get_pipeline_name(self):
        return self.config_parser.get('pipeline', 'name')

    def get_load_base_url(self):
        return self.config_parser.get('LOAD', 'base_url')

    def get_load_limit(self):
        return self.config_parser.getint('LOAD', 'limit')


config = ConfigManager("pipeline.cfg")
print(config.get_pipeline_name())