"""
DomRu python API client
"""

import json
import time
from typing import List
from urllib.parse import parse_qs, urlparse
from bs4 import BeautifulSoup
import requests
from requests import Session, Response


from .types import AuthTokens, Agreement, AgreementInfo, Region
from .exceptions import AuthenticationError, DataFetchError
from .utils import discover_openid_configuration, generate_pkce_pair

class DomRuClient:
    BASE = "https://id.dom.ru"
    REALM = "b2c"
    CLIENT_ID = "b2c-client"
    REDIRECT_URI = None
    SCOPE = "openid"
    RESPONSE_TYPE = "code"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.0.1 Safari/605.1.15",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8"
    }
    REST_HEADERS = {
        "X-Requested-With" : "XMLHttpRequest",
        "Sec-Fetch-Mode" : "cors",
        "Sec-Fetch-Site" : "same-site",
        "Sec-Fetch-Dest" : "empty",
        "Accept" : "*/*",
        "User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.0.1 Safari/605.1.15"
    }

    """
    DomRuClient class.
    Require:
        - phone: DomRu account phone number
        - region: Region your account
    """

    def __init__(self, phone:str, auth:AuthTokens = None) -> None:
        self.phone:str = phone
        self.session:Session = requests.Session()
        self.authorization:AuthTokens = AuthTokens
        self.code_verifier:str = None
        self.authorization_endpoint:str = None
        self.token_endpoint:str = None
        self.region:Region = None

        if (auth):
            self.authorization = auth

        # discover endpoints
        self._discover_endpoints()

    # ---------------- Endpoints ----------------
    def _discover_endpoints(self) -> None:
        configuration = discover_openid_configuration(self.BASE, self.REALM)
        self.authorization_endpoint = configuration["authorization_endpoint"]
        self.token_endpoint = configuration["token_endpoint"]

    # ---------------- Authorization Flow ----------------
    def _get_login_form(self, code_challenge) -> any:
        params = {
            "client_id": self.CLIENT_ID,
            "redirect_uri": self.REDIRECT_URI,
            "response_type": self.RESPONSE_TYPE,
            "scope": self.SCOPE,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256"
        }
        r = self.session.get(self.authorization_endpoint, params=params, headers=self.HEADERS)
        r.raise_for_status()

        soup = BeautifulSoup(r.text, "html.parser")
        form = soup.find("form")
        if not form or "action" not in form.attrs:
            raise AuthenticationError("Форма авторизации не найдена.")
        action = form["action"]
        return action
    
    def _send_phone(self, action_url) -> any:
        payload = {
            "operation": "phone_auth",
            "phoneNumber": self.phone,
            "rememberMe": "on"
        }

        r = self.session.post(action_url, data=payload, headers=self.HEADERS)
        r.raise_for_status()

        soup = BeautifulSoup(r.text, "html.parser")

        async_script = soup.find("script", {"id": "__ASYNC_ACTION__"})
        if not async_script:
            print(soup.prettify()) 
            raise DataFetchError("Не найден блок __ASYNC_ACTION__ — проверь HTML.")
        
        data = json.loads(async_script.text)
        next_data = data.get("next", {})

        csrf_token = next_data.get("csrfToken")
        next_url = next_data.get("url")

        if not csrf_token or not next_url:
            raise DataFetchError("Не удалось извлечь csrfToken или URL для check операции.")
        
        return csrf_token, next_url

    def _send_otp(self, action_url, csrf_token, otp) -> Response:
        data = {
            "operation": "otp_auth",
            "csrfToken": csrf_token,
            "otp": otp
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": action_url,
            "Origin": self.BASE,
            "User-Agent": self.HEADERS["User-Agent"]
        }

        post_resp = self.session.post(action_url, data=data, headers=headers, allow_redirects=False)
        
        if post_resp.status_code == 200:
            get_resp = self.session.get(action_url, allow_redirects=False)
            return get_resp
        return post_resp

    def _extract_auth_code_from_redirect(self, resp) -> str:
        redirect_url = resp.headers.get("Location", "")
        parsed = urlparse(redirect_url)
        params = parse_qs(parsed.query)
        code = params.get("code", [None])[0]
        return code

    def _exchange_code_for_token(self, code) -> None:
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.REDIRECT_URI,
            "code_verifier": self.code_verifier,
            "client_id": self.CLIENT_ID
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded", 
            "User-Agent": self.HEADERS["User-Agent"]
        
        }
        
        r = self.session.post(self.token_endpoint, data=data, headers=headers)
        r.raise_for_status()

        tokens = r.json()

        self.authorization.access_token = tokens.get("access_token")
        self.authorization.refresh_token = tokens.get("refresh_token")
        self.authorization.token_expiry = time.time() + tokens.get("expires_in", 3600)
    
    def _validate_access_token(self) -> None:
        if time.time() >= self.authorization.token_expiry:
            try:
                self.refresh_access_token()
            except Exception:
                raise AuthenticationError("An error occurred while updating the token.")
        if not self.authorization.access_token:
            raise AuthenticationError("The access token is unavailable - you need authorization again.")


    # ---------------- Public Methods ----------------
    def refresh_access_token(self):
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.authorization.refresh_token,
            "client_id": self.CLIENT_ID
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded", 
            "User-Agent": self.HEADERS["User-Agent"]
        }

        r = self.session.post(self.token_endpoint, data=data, headers=headers)
        r.raise_for_status()

        tokens = r.json()

        self.authorization.access_token = tokens.get("access_token")
        self.authorization.refresh_token = tokens.get("refresh_token")
        self.authorization.token_expiry = time.time() + tokens.get("expires_in", 3600)

        return self.authorization.access_token
    
    def get_agreements(self) -> List[Agreement]:
        resp_json = self.request("GET", "https://web-api.dom.ru/core-profile/v2/user/agreements?detailType=full", headers=self.REST_HEADERS).json()
        return [Agreement(**item) for item in resp_json]
    
    def get_agreement_info(self, agreementNumber) -> List[Agreement]:
        headers = self.REST_HEADERS
        headers["agreementNumber"] = agreementNumber

        resp = self.request("GET", "https://web-api.dom.ru/api-profile/v2/info/all", headers=headers)
        return AgreementInfo(**resp.json())

    def get_region_list(self):
        """
        Method to get a list of all regions
        """
        url = "https://web-api.dom.ru/api-content/v1/geography/get-cities-satellites"
        r = requests.get(url, headers=self.REST_HEADERS)
        r.raise_for_status()

        data = r.json()

        regions = [Region(**region) for region in data.values()]
        return regions

    def set_region(self, region:Region) -> None:
        """
        Method for setting regional variables
        """
        self.region = region
        self.REDIRECT_URI = f"https://{region.domain}.dom.ru/user/change-agreement"
        self.REST_HEADERS["Origin"] = f"https://{region.domain}.dom.ru"
        self.REST_HEADERS["ProviderId"] = str(region.provider_id)

    def start_authorization(self) -> tuple[str, str]:
        """
        Инициирует авторизацию: создаёт PKCE, отправляет телефон.
        Возвращает csrf_token и URL для ввода OTP.
        """
        self.code_verifier, code_challenge = generate_pkce_pair()
        action_url = self._get_login_form(code_challenge)
        csrf_token, otp_url = self._send_phone(action_url)
        return csrf_token, otp_url
    
    def finish_authorization(self, csrf_token: str, otp_url: str, otp: str) -> None:
        """
        Завершает авторизацию: отправляет OTP, извлекает authorization_code и получает токены.
        """
        resp = self._send_otp(otp_url, csrf_token, otp)
        code = self._extract_auth_code_from_redirect(resp)
        if not code:
            raise DataFetchError("Failed to get authorization_code")
        self._exchange_code_for_token(code)
    
    def request(self, method, url, **kwargs) -> Response:
        """
        Make an authorized request with a Bearer token
        """

        self._validate_access_token()

        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self.authorization.access_token}"
        return self.session.request(method, url, headers=headers, **kwargs)