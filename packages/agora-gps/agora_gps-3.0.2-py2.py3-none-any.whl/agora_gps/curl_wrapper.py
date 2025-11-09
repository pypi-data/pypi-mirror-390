import requests
from agora_logging import logger

class CurlWrapper:
    def __init__(self, ) -> None:
        super().__init__()

    def get_response(self, url:str, header:dict):
        try:
            response = requests.get(url, headers=header)
            return response
        except Exception as e:
            logger.error(f"Error: {e}")
            return None

    def post_request(self, url:str, data, header:dict):
        try:
            response = requests.post(url, headers=header, data=data)
            return response
        except Exception as e:
            logger.error(f"Error: {e}")
            return None

    def put_request(self, url:str, data, header:dict):
        try:
            response = requests.put(url, headers=header, data=data)
            return response
        except Exception as e:
            logger.error(f"Error: {e}")
            return None

    def delete_request(self, url:str, header:dict):
        try:
            response = requests.delete(url, headers=header)
            return response
        except Exception as e:
            logger.error(f"Error: {e}")
            return None