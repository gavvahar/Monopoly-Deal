import os

AUTHENTICATION_SOURCES = ["oauth2"]
OAUTH2_AUTO_CREATE_USER = True

authentik_url = os.environ.get("AUTHENTIK_URL", "")
app_slug = os.environ.get("PGADMIN_AUTHENTIK_APP_SLUG", "")

OAUTH2_CONFIG = [
    {
        "OAUTH2_NAME": "authentik",
        "OAUTH2_DISPLAY_NAME": "Authentik",
        "OAUTH2_CLIENT_ID": os.environ.get("PGADMIN_OAUTH2_CLIENT_ID", ""),
        "OAUTH2_CLIENT_SECRET": os.environ.get("PGADMIN_OAUTH2_CLIENT_SECRET", ""),
        "OAUTH2_TOKEN_URL": f"{authentik_url}/application/o/token/",
        "OAUTH2_AUTHORIZATION_URL": f"{authentik_url}/application/o/authorize/",
        "OAUTH2_API_BASE_URL": f"{authentik_url}/application/o/{app_slug}/",
        "OAUTH2_SERVER_METADATA_URL": f"{authentik_url}/application/o/{app_slug}/.well-known/openid-configuration",
        "OAUTH2_USERINFO_ENDPOINT": f"{authentik_url}/application/o/userinfo/",
        "OAUTH2_SCOPE": "openid email profile",
        "OAUTH2_ICON": "",
        "OAUTH2_BUTTON_COLOR": "#fd4b2d",
    }
]
