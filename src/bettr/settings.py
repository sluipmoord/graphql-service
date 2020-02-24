import base64
import os
from distutils.util import strtobool

import boto3

APP_NAME = "Bettr"


def get_encrypted_setting(key, default):
    key_value = os.environ.get(key, default=default)
    try:
        binary_data = base64.b64decode(key_value)
        kms = boto3.client("kms")
        meta = kms.decrypt(CiphertextBlob=binary_data)
        plaintext = meta[u"Plaintext"]
        return plaintext.decode()
    except Exception:
        return key_value


BASE_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "..", ".."
)

STATIC_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "static"
)

STATIC_ROOT = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "static"
)

STATIC_URL = os.environ.get("STATIC_URL", default=None)

IS_LOCAL = strtobool(os.environ.get("IS_LOCAL", default="False"))
IS_PRODUCTION = os.environ.get("FLASK_ENV", "development") == "production"
STAGE = os.environ.get("STAGE", "dev")

AWS_REGION = os.environ.get("AWS_REGION", default="eu-west-1")

LOGGER_LEVEL = os.environ.get("LOGGER_LEVEL", default="INFO")

SQLALCHEMY_DATABASE_URI = get_encrypted_setting(
    "SQLALCHEMY_DATABASE_URI", default=""
)

SQLITE_URI_PREFIX = "sqlite:///"
if SQLALCHEMY_DATABASE_URI.startswith(SQLITE_URI_PREFIX):
    SQLALCHEMY_DATABASE_URI = "{}{}".format(
        SQLITE_URI_PREFIX,
        os.path.join(
            BASE_DIR, SQLALCHEMY_DATABASE_URI[len(SQLITE_URI_PREFIX) :]
        ),
    )
SQLALCHEMY_ECHO = strtobool(os.environ.get("SQLALCHEMY_ECHO", default="False"))
SQLALCHEMY_TRACK_MODIFICATIONS = strtobool(
    os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS", default="False")
)

COGNITO_CLIENT_ID = os.environ.get("COGNITO_CLIENT_ID", default="")
COGNITO_CLIENT_SECRET = os.environ.get("COGNITO_CLIENT_SECRET", default="")
COGNITO_IDENTITY_POOL_ID = os.environ.get(
    "COGNITO_IDENTITY_POOL_ID", default=""
)
COGNITO_USER_POOL_ID = os.environ.get("COGNITO_USER_POOL_ID", default="")
