import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urlparse, parse_qs
import base64
import hashlib
import secrets

BASE = "https://id.dom.ru"
REALM = "b2c"
CLIENT_ID = "b2c-client"
REDIRECT_URI = "https://samara.dom.ru/user/change-agreement"
SCOPE = "openid"
RESPONSE_TYPE = "code"
PHONE = '+79991710455'
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8"
}


def generate_pkce_pair():
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b"=").decode("utf-8")
    digest = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    code_challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("utf-8")
    return code_verifier, code_challenge


def discover_endpoints():
    r = requests.get(f"{BASE}/realms/{REALM}/.well-known/openid-configuration", timeout=10)
    r.raise_for_status()
    conf = r.json()
    return conf["authorization_endpoint"], conf["token_endpoint"]


def get_login_form(session, auth_url, code_challenge):
    """Открываем страницу авторизации, получаем action"""

    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": RESPONSE_TYPE,
        "scope": SCOPE,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256"
    }
    r = session.get(auth_url, params=params, headers=HEADERS)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")
    form = soup.find("form")
    if not form or "action" not in form.attrs:
        raise RuntimeError("Форма авторизации не найдена.")
    action = form["action"]
    return action


def send_phone(session, action_url, phone_number):
    """Отправляем номер телефона и достаём csrfToken из JSON-блока"""
    payload = {
        "operation": "phone_auth",
        "phoneNumber": phone_number,
        "rememberMe": "on"
    }
    r = session.post(action_url, headers=HEADERS, data=payload)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    # Попробуем найти JSON со статусом processing
    async_script = soup.find("script", {"id": "__ASYNC_ACTION__"})
    if not async_script:
        raise RuntimeError("Не найден блок __ASYNC_ACTION__ — проверь HTML.")

    data = json.loads(async_script.text)
    next_data = data.get("next", {})

    csrf_token = next_data.get("csrfToken")
    next_url = next_data.get("url")

    if not csrf_token or not next_url:
        raise RuntimeError("Не удалось извлечь csrfToken или URL для check операции.")

    print(f"[DEBUG] csrfToken: {csrf_token}")
    print(f"[DEBUG] next_url: {next_url}")

    return csrf_token, next_url


def send_otp(session: requests.Session, action_url: str, csrf_token: str, otp: str):
    """
    Имитация JS KeycloakAsyncAction.authenticate():
    1. Отправляем POST с OTP
    2. Делаем GET на тот же action_url — там появляется redirect с code=
    """
    data = {
        "operation": "otp_auth",
        "csrfToken": csrf_token,
        "otp": otp
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": action_url,
        "Origin": "https://id.dom.ru",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    }

    print(f"[DEBUG] Отправляем OTP POST → {action_url}")
    post_resp = session.post(action_url, data=data, headers=headers, allow_redirects=False)

    # Если вернулся 200 — значит, JS ещё не инициировал redirect.
    if post_resp.status_code == 200:
        print("[DEBUG] Сервер ответил 200 — пытаемся получить redirect вручную...")
        get_resp = session.get(action_url, allow_redirects=False)
        return get_resp

    return post_resp

def extract_auth_code_from_redirect(resp):
    """Извлекает authorization_code и session_state из redirect Location"""
    redirect_url = resp.headers.get("Location", "")
    if not redirect_url:
        print("[ERROR] Не найден redirect после OTP шага.")
        return None, None

    parsed = urlparse(redirect_url)
    params = parse_qs(parsed.query)
    code = params.get("code", [None])[0]
    session_state = params.get("session_state", [None])[0]

    print(f"[INFO] Auth code: {code}")
    print(f"[INFO] Session state: {session_state}")
    return code, session_state


def exchange_code_for_token(session, token_url, code, code_verifier, redirect_uri="https://samara.dom.ru/user/change-agreement"):
    """
    Обменивает authorization_code на access/refresh токены
    """
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "code_verifier": code_verifier,
        "client_id": CLIENT_ID
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"
    }

    print("[INFO] Обмениваем authorization_code на access/refresh токены...")
    r = session.post(token_url, data=data, headers=headers)

    if r.status_code != 200:
        print(f"[ERROR] Ошибка при обмене токена ({r.status_code}): {r.text}")
        return None

    tokens = r.json()
    print("[✅] Успешно получили токены:")
    print(f"Access token: {tokens.get('access_token')}...")
    print(f"Refresh token: {tokens.get('refresh_token')}...")
    return tokens


def main():
    phone = PHONE
    session = requests.Session()

    # --- Этап 1: инициализация авторизации ---
    auth_url, token_url = discover_endpoints()
    code_verifier, code_challenge = generate_pkce_pair()
    print(f"[INFO] Используем endpoint: {auth_url}")

    # --- Этап 2: получение HTML формы логина ---
    action_url = get_login_form(session, auth_url, code_challenge)
    print(f"[INFO] Форма авторизации: {action_url}")

    # --- Этап 3: отправляем номер телефона ---
    csrf, action_url = send_phone(session, action_url, phone)
    print("[INFO] SMS отправлено, ожидаем код...")

    # --- Этап 4: получаем OTP от пользователя ---
    otp = input("Введите код из SMS: ").strip()

    # --- Этап 5: отправляем OTP ---
    resp = send_otp(session, action_url, csrf, otp)

    if resp.status_code in (302, 303):
        print("[INFO] Redirect после OTP подтверждения — извлекаем authorization_code...")
        code, session_state = extract_auth_code_from_redirect(resp)
        if not code:
            print("[ERROR] Не удалось извлечь authorization_code из redirect.")
            return
        # --- Этап 6: обмен authorization_code на токены ---
        tokens = exchange_code_for_token(session, token_url, code, code_verifier)
        if tokens:
            print("[INFO] ✅ Авторизация завершена успешно.")
        else:
            print("[ERROR] Не удалось получить токены.")
    else:
        print(f"[ERROR] OTP шаг вернул неожиданный ответ ({resp.status_code}):")
        print(resp.text[:400])


if __name__ == "__main__":
    main()