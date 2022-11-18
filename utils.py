from google.cloud import secretmanager
from google.oauth2 import id_token
from google.auth.transport import requests


client_secrets = secretmanager.SecretManagerServiceClient()


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


def get_secret(secret_id):
    response = client_secrets.access_secret_version(
        name=f"projects/cs493-portfolio-carterja/secrets"
             f"/{secret_id}/versions/1"
    )
    payload = response.payload.data.decode("UTF-8")
    return payload


def verify_token(headers, creds):
    if "Authorization" in headers:
        user_token = headers["Authorization"].split()[1]
        try:
            idinfo = id_token.verify_oauth2_token(
                user_token,
                requests.Request(),
                creds["web"].get("client_id"))

            return idinfo
        except Exception as e:
            print(e)
            raise AuthError({"Error": str(e)}, 401)
    else:
        raise AuthError({"code": "no auth header",
                        "description": "Authorization header is missing"}, 401)
