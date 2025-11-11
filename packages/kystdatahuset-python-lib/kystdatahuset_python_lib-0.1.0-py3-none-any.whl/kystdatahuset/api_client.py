from typing import Any, Dict, List, Tuple, Optional

from kystdatahuset.models import WebServiceResponse
from .const import API_URL
import requests
from kystdatahuset.logging import logger

def get_headers(jwt_token: Optional[str] = None, json: bool = False) -> Dict[str, str]:
    """
    Build headers for API requests.
    """
    headers: Dict[str, str] = {}
    if jwt_token:
        headers["Authorization"] = f"Bearer {jwt_token}"
    if json:
        headers["Content-Type"] = "application/json"
        headers["Accept"] = "application/json"
    return headers


def post_api_formdata(jwt_token: str, fragment: str, data: List[Tuple[str, Any]], filename: str) -> WebServiceResponse:
    """
    POST multipart/form-data with a file and form fields.
    """
    url = f"{API_URL}/{fragment}"

    with open(filename, "rb") as f:
        files = {"file": (filename, f, "application/octet-stream")}
        response = requests.post(url, headers=get_headers(jwt_token), data=data, files=files)

    if response.ok:
        try:
            logger.info(f"✅ POST (FormData) {url} successful!")
            data = response.json()
            return data
        except ValueError:            
            return WebServiceResponse[Any](**{"success": True, "msg": response.text, "data": None})
    else:
        logger.error(f"❌ POST (FormData) {url} failed with {response.status_code}")
        logger.debug(response.text)
        raise Exception(f"API POST (FormData) failed with status code {response.status_code}: {response.text}")


def get_api(jwt_token: str, fragment: str, params: Optional[Dict[str, Any]] = None) -> WebServiceResponse:
    """
    Perform a GET request and parse JSON response.
    """
    url = f"{API_URL}/{fragment}"
    response = requests.get(url, headers=get_headers(jwt_token, json=True), params=params)

    if response.ok:
        logger.info(f"✅ GET {url} successful!")
        try:
            data = response.json()
            logger.debug(f"Response JSON: {data}")
            return data
        except ValueError:
            return WebServiceResponse[str](**{"success": True, "msg": response.text, "data": None})
    else:
        logger.error(f"❌ GET {url} failed with {response.status_code}")
        logger.debug(response.text)
        raise Exception(f"API GET failed with status code {response.status_code}: {response.text}")

def delete_api(jwt_token: str, fragment: str, params: Optional[Dict[str, Any]] = None) -> WebServiceResponse:
    """
    Perform a DELETE request and parse the JSON response.
    """
    url = f"{API_URL}/{fragment}"
    response = requests.delete(url, headers=get_headers(jwt_token, json=True), params=params)

    if response.ok:
        logger.info(f"✅ DELETE {url} successful!")
        try:
            data = response.json()
            logger.debug(f"Response JSON: {data}")
            return data
        except ValueError:
            return WebServiceResponse[str](**{"success": True, "msg": response.text, "data": None})
    else:
        logger.error(f"❌ GET {url} failed with {response.status_code}")
        logger.debug(response.text)
        raise Exception(f"API GET failed with status code {response.status_code}: {response.text}")


def post_api_json(jwt_token: str, fragment: str, payload: Dict[str, Any]) -> WebServiceResponse:
    """
    Perform a POST request with a JSON body and parse JSON response.
    """
    url = f"{API_URL}/{fragment}"
    response = requests.post(url, headers=get_headers(jwt_token, json=True), json=payload)

    if response.ok:
        logger.info(f"✅ JSON POST to {url} successful!")
        try:
            data = response.json()
            logger.debug(f"Response JSON: {data}")
            return data
        except ValueError:
            return WebServiceResponse[str](**{"success": True, "message": response.text, "data": None})
    else:
        logger.error(f"❌ JSON POST to {url} failed with {response.status_code}")
        logger.debug(response.text)
        raise Exception(f"API JSON POST failed with status code {response.status_code}: {response.text}")
