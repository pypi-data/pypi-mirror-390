import logging
from domru_client import DomRuClient
from domru_client.types import AuthTokens, Region, Agreement, AgreementInfo
from domru_client.exceptions import AuthenticationError, DataFetchError
from domru_client.utils import discover_openid_configuration, get_discover_openid_configuration_url

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)

def getAuthData(auth:AuthTokens):
    return {
        "access_token" : auth.access_token,
        "refresh_token" : auth.refresh_token,
        "token_expiry" : auth.token_expiry
    }

def main():
    logging.info("🚀 Старт теста DomRuClient")
    auth:AuthTokens = AuthTokens

    # Укажи реальные данные (можно через .env или параметры окружения)
    phone = "+79991710758"
    auth.access_token = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJMbEc2dGNLcGhsRW1kandVa2ViZ200SmhSSVVER0dSNFBQR0I2YllGcnlJIn0.eyJleHAiOjE3NjI1NTM1NzksImlhdCI6MTc2MjUyNDc3OSwiYXV0aF90aW1lIjoxNzYyNTI0Nzc4LCJqdGkiOiJvbnJ0YWM6MWQ1YzdlZjQtYTgwZi0yMzEzLWEwOWQtZjAzOTMwMjc0NjIwIiwiaXNzIjoiaHR0cHM6Ly9pZC5kb20ucnUvcmVhbG1zL2IyYyIsImF1ZCI6ImFjY291bnQiLCJzdWIiOiJmOjg5MDMzNDcyLTBmZmMtNGU5NS05MGQ0LWI4NjYzMjU3YTBlYTowZTFiYWJiYy1iZmNkLTQyNWQtOGZkZS1jMWU3ODA5MTI3ZTYiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJiMmMtY2xpZW50Iiwic2lkIjoiMWNmY2Y5MjItYmMwNy00NTY2LWJhYjMtZTE1NTRmYjE4ZWFhIiwiYWNyIjoiMSIsImFsbG93ZWQtb3JpZ2lucyI6WyIqIl0sInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJvZmZsaW5lX2FjY2VzcyIsInVtYV9hdXRob3JpemF0aW9uIl19LCJyZXNvdXJjZV9hY2Nlc3MiOnsiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSIsInByZWZlcnJlZF91c2VybmFtZSI6Iis3OTk5MTcxMDc1OCJ9.mk_hvfLzv6w2GYiUbn1cJ4X7FXsv39Jw05A1qdpzJecpEZjmBemXEGti_R9Rw9Kf-bKlo-daK-HepYoFxPKlq3muIF20z9z-6ns8_nDLrIe0hAFAxEwKF5mYDiCug6OHVBVmLCks8eBAo5xcylObV0cytX6vgvImE5cz5nGO_nruoGlvubDeIHw6-Vz7qwakxkH_tNta6RHLdYqH0OIL2B08J7slAbiKATvfWte4qWi_HGrJpn_aAfZjhQ1ULcrcV4Dc8VFUeQDsqGKdyZFNLWYxFmeCMTyPCWQXRcsAVZ7-iBotbEavcXbYpTbhflM6ExHM5RIR_VapG_UfuEMhOg"
    auth.refresh_token = "eyJhbGciOiJIUzUxMiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICI3ZjA1MzlkMy0zMzU0LTQwMTAtODdlZC0yNmIxYjNiNjA1NDEifQ.eyJleHAiOjE3Njc3MDg3NzksImlhdCI6MTc2MjUyNDc3OSwianRpIjoiMjI0ZGVkZmMtMmFiOC0wMTVlLTg1Y2YtMDQ0NGY4YTdmMjY4IiwiaXNzIjoiaHR0cHM6Ly9pZC5kb20ucnUvcmVhbG1zL2IyYyIsImF1ZCI6Imh0dHBzOi8vaWQuZG9tLnJ1L3JlYWxtcy9iMmMiLCJzdWIiOiJmOjg5MDMzNDcyLTBmZmMtNGU5NS05MGQ0LWI4NjYzMjU3YTBlYTowZTFiYWJiYy1iZmNkLTQyNWQtOGZkZS1jMWU3ODA5MTI3ZTYiLCJ0eXAiOiJSZWZyZXNoIiwiYXpwIjoiYjJjLWNsaWVudCIsInNpZCI6IjFjZmNmOTIyLWJjMDctNDU2Ni1iYWIzLWUxNTU0ZmIxOGVhYSIsInNjb3BlIjoib3BlbmlkIHByb2ZpbGUgd2ViLW9yaWdpbnMgYmFzaWMgcm9sZXMgYWNyIn0.k-EkY8gG0PDWTDSeKRFBptp6KRkuPRrKY5Gf2T72YzpUxhX1dVf7OIPjt9e5UcaskKtzmue5AQDexGLxRtRbLg"
    auth.token_expiry=1762553579.1867368

    try:
        client = DomRuClient(phone=phone)
        client.set_region(Region(
            name = "Самара, Самарская область",
            domain = "samara",
            provider_id = 25,
            has_sso = 1
        ))

        # print(client.authorization)

        # csrf_token, otp_url = client.start_authorization()
        # opt_code = input("Введите код из SMS: ").strip()
        # client.finish_authorization(csrf_token, otp_url, opt_code)

        resp = client.get_agreements()
        for agreement in resp:
            print(agreement.number, agreement.address.full)
            print(client.get_agreement_info(agreement.number))


        # print(client.authorization.access_token)
        # client.refresh_access_token()
        # print(getAuthData(client.authorization))

        # print(client.get_region_list())

    except AuthenticationError as e:
        logging.error("❌ Ошибка авторизации: %s", e)
    except DataFetchError as e:
        logging.error("⚠️  Ошибка получения данных: %s", e)
    except Exception as e:
        logging.exception("💥 Непредвиденная ошибка")


if __name__ == "__main__":
    main()