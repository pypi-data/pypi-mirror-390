import configparser
from importlib import resources

class ConfigManager:
    def config(self):
        cfg_path = resources.files('pipeline').joinpath('pipeline.cfg')
        with cfg_path.open("r") as f:
            config = configparser.ConfigParser()
            config.read_file(f)
            base_url = config['API']['BASE_API_URL']
            limit = config.getint('API', 'LIMIT')
        
            return (base_url, limit)

