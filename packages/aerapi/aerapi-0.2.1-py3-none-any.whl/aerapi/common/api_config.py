import os
import yaml
from pathlib import Path
from dataclasses import dataclass

@dataclass
class APIConfig:
    base_url: str
    api_key_id: str
    api_secret_key: str

@dataclass
class ClientEnvConfig:
    env: str
    client: str


CONFIG_DIR = Path.home() / ".aerapi"
CONFIG_FILE = CONFIG_DIR / "config.yaml"


def get_api_config(env, name):
    """
    Get the API configuration for a specific environment and API name.
    
    Parameters:
    - env (str): The environment (e.g., 'preprod', 'demo').
    - name (str): The specific name of the API within the environment (e.g., 'api-api-preprod-amergin').

    Returns:
    - dict: A dictionary containing 'api_key_id', 'api_secret_key', and 'base_url'.
    """
    try:
        # Open and load the YAML configuration file
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        yaml_path = os.path.join(base_dir, 'config', 'config.yaml')

        # Open and load the YAML configuration file
        with open(yaml_path, 'r') as file:
            config = yaml.safe_load(file)

        # Loop through the configurations for the given environment
        for entry in config['environments'].get(env, []):
            if entry['name'] == name:
                # Return the API key, secret, and name as base_url
                return {
                    'api_key_id': entry['api_key_id'],
                    'api_secret_key': entry['api_secret_key'],
                    'base_url': 'https://' + entry['url'] + '/v1'
                }

        # If no matching configuration is found, return None
        print(f"No configuration found for {env} environment with API name {name}.")
        return None

    except FileNotFoundError:
        print("Error: config.yaml file not found.")
        return None
    except yaml.YAMLError as e:
        print(f"Error parsing config.yaml: {e}")
        return None

def ensure_config_dir_exists():
    """
    Create ~/.aerapi directory if it doesn't exist.
    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def get_config_dir():
    return CONFIG_DIR


def get_default_config_path() -> Path:
    ensure_config_dir_exists()
    return CONFIG_FILE