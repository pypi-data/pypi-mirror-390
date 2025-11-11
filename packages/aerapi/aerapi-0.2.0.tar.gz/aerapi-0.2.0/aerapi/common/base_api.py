import requests
import logging
import yaml
import os
from typing import Optional, Dict

from . import utils
from .api_config import APIConfig, ClientEnvConfig, get_default_config_path, get_config_dir


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseAPIClient():
    config: APIConfig = None

    def __init__(self, api_config: Optional[APIConfig | ClientEnvConfig] = None):
        """
        Initialize the BaseAPI with environment and client.

        Parameters:
        - api_config (Optional[APIConfig | ClientEnvConfig]): The environment (e.g., 'production', 'preprod').
        """

        if api_config == None:
            self.config = self.load_api_config()
            return
        
        if isinstance(api_config, APIConfig):
            self.config = api_config
            return

        if isinstance(api_config, ClientEnvConfig):
            self.config = self.load_api_config_from_yaml(api_config)
            return
        
        raise SystemError("Critical Error loading the BaseAPI.")
        

                
    def load_api_config(self) -> Optional[Dict]:
        """
        Load API configuration from the exported environment variables stored on OS.
        """
        api_key_id = os.getenv("AERAPI_API_KEY_ID", None)
        if api_key_id == None:
            raise ValueError(f"Unable to find enviornment variable 'AERAPI_API_KEY_ID'. Cannot configure API.")
        
        api_secret_key = os.getenv("AERAPI_API_SECRET_KEY", None)
        if api_secret_key == None:
            raise ValueError(f"Unable to find enviornment variable 'AERAPI_API_SECRET_KEY'. Cannot configure API.")

        base_url = os.getenv("AERAPI_BASE_URL", None)
        if base_url == None:
            raise ValueError(f"Unable to find enviornment variable 'AERAPI_BASE_URL'. Cannot configure API.")

        return APIConfig(
                base_url=base_url,
                api_key_id=api_key_id,
                api_secret_key=api_secret_key,
            )


    def load_api_config_from_yaml(self, api_config: ClientEnvConfig):
        """
        Get the API configuration for a specific environment and API name.

        Parameters:
        - api_config (ClientEnvConfig): The environment (e.g., 'preprod', 'demo').

        Returns:
        - dict: A dictionary containing 'api_key_id', 'api_secret_key', and 'base_url'.
        """
        try:
            # Open and load the YAML configuration file
            yaml_path = get_default_config_path()


            # Open and load the YAML configuration file
            with open(yaml_path, 'r') as file:
                config = yaml.safe_load(file)

            # Loop through the configurations for the given environment
            for entry in config['environments'].get(api_config.env, []):
                if entry['name'] == api_config.client:
                    return APIConfig(
                            base_url='https://' + entry['url'] + '/v1',
                            api_key_id=entry['api_key_id'],
                            api_secret_key=entry['api_secret_key'],
                        )

            # If no matching configuration is found, return None
            print(f"No configuration found for {api_config.env} environment with API name {api_config.client}.")
            return None

        except FileNotFoundError:
            print(f"Error: config.yaml file not found. Please create a config.yaml file in {get_config_dir()}")
            return None
        except yaml.YAMLError as e:
            print(f"Error parsing config.yaml: {e}")
            return None


    def get_auth_headers(self):
        """
        Create the headers needed for authentication with API keys.
        """
        return {
            'Api-Key-Id': self.config.api_key_id,
            'Api-Secret-Key': self.config.api_secret_key,
            'Content-Type': 'application/json',
        }


    def make_authenticated_request(self, config: APIConfig, url: str, method='GET', params=None, data=None, debug=False, multiSend=False, sendSize=100, timeout=30):
        """
        Make an authenticated request to a given API, with optional support for sending requests in chunks.

        Parameters:
        - url (str): API endpoint URL.
        - method (str): HTTP method ('GET', 'POST', etc.).
        - params (dict): Query parameters.
        - data (dict): Payload for POST/PUT requests.
        - debug (bool): Enable debug logging.
        - multiSend (bool): If True, splits requests into smaller chunks.
        - sendSize (int): Number of items per chunk in multi-send mode.
        - timeout (int): Timeout for the request in seconds.
        Returns:
        - list or dict: A list of responses for multi-send, or a single response for single requests.
        """
        
        headers = {
            'Api-Key-Id': config.api_key_id,
            'Api-Secret-Key': config.api_secret_key,
            'Content-Type': 'application/json',
        }

        full_url = f"{config.base_url.rstrip('/')}{url}"
        if debug:
            logger.info(f"Request URL: {full_url}")

        responses = []

        # Multi-send logic
        if multiSend:
            if 'items' in data and isinstance(data, dict):
                items = data['items']
            elif isinstance(data, list):
                items = data
            else:
                logger.error(f"Data not correctly formatted for a multisend")
                return None
            chunks = utils.chunkIt(items, max(1, len(items) // sendSize))
            for chunk in chunks:
                chunked_data = {"items": chunk}
                try:
                    response = self._send_request(method, full_url, headers, chunked_data, params, timeout, debug=debug)
                    if response:
                        responses.append(response)
                except requests.exceptions.RequestException as e:
                    logger.error(f"Error during chunked request: {e}")
                    return None

            return responses

        # Single request logic
        try:
            return self._send_request(method, full_url, headers, data, params, timeout, debug=debug)
        except requests.exceptions.RequestException as e:
            logger.error(f"Error during request: {e}")
            return None
    

    def _send_request(self, method, url, headers, data, params, timeout, debug):
        if method == 'GET':
            response = requests.get(url, headers=headers, params=params, timeout=timeout)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data, timeout=timeout)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, json=data, timeout=timeout)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers, params=params, timeout=timeout)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")


        # Log the status code for each request
        if debug:
            logger.info(f"Response Status Code: {response.status_code}")
            logger.info(f"Response JSON: {response.json()}")

        # Return JSON response if content exists, otherwise return an empty dict
        return response.json() if response.content else {}
