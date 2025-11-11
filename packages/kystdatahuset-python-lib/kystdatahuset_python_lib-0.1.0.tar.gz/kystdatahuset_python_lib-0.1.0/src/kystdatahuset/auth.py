import requests
import json

from kystdatahuset.models import AuthData, WebServiceResponse
from kystdatahuset.logging import logger
from .const import API_URL

def login(username: str, password: str) -> WebServiceResponse[AuthData]:
    reqUrl = f"{API_URL}/api/auth/login"

    headersList = {
        "User-Agent": "Kystdatahuset Python Library (https://your-client.com)",
        "accept": "*/*",
        "Content-Type": "application/json" 
    }

    payload = json.dumps({
        "username": username,
        "password": password
    })

    response = requests.request("POST", reqUrl, data=payload,  headers=headersList)

    if response.status_code == 200:
        logger.info("✅ Login successful!")
        return WebServiceResponse[AuthData](**response.json()) 
    else:
        logger.error(f"❌ Login failed with status code {response.status_code}")
        logger.debug(response.text)
        raise Exception(f"Login failed with status code {response.status_code}: {response.text}")