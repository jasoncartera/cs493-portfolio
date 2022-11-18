from utils import utils
users = "users"

creds = {
    "web": {
        "client_id": utils.get_secret("client_id"),
        "project_id": "cs493-portfolio-carterja",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": utils.get_secret("client_secret")
    }
}