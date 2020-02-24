import boto3
import click
import hmac
import hashlib
import base64

from flask import current_app
from flask.cli import AppGroup

cognito_cli = AppGroup(
    "cognito",
    short_help="Execute Amazon Cognito Identity Provider operations.",
)


@cognito_cli.command(
    "admin_initiate_auth",
    short_help=(
        "Initiate the Cognito authentication flow, as an administrator."
    ),
)
@click.argument("email")
@click.argument("password")
def admin_initiate_auth(email, password):
    cognito_idp = boto3.client("cognito-idp")

    client_secret = current_app.config["COGNITO_CLIENT_SECRET"]
    client_id = current_app.config["COGNITO_CLIENT_ID"]
    auth_params = {"USERNAME": email, "PASSWORD": password}

    if client_secret:
        auth_params["SECRET_HASH"] = get_secret_hash(
            client_id, client_secret, email
        )
    response = cognito_idp.admin_initiate_auth(
        UserPoolId=current_app.config["COGNITO_USER_POOL_ID"],
        ClientId=client_id,
        AuthFlow="ADMIN_NO_SRP_AUTH",
        AuthParameters=auth_params,
    )
    if "AuthenticationResult" in response:
        print(response["AuthenticationResult"]["IdToken"])
    else:
        print(response)


@cognito_cli.command("admin_create_user", short_help=("Create a new user."))
@click.argument("name")
@click.argument("family_name")
@click.argument("email")
@click.argument("phone_number")
@click.argument("temp_password")
def admin_create_user(name, family_name, email, phone_number, temp_password):
    cognito_idp = boto3.client("cognito-idp")
    response = cognito_idp.admin_create_user(
        UserPoolId=current_app.config["COGNITO_USER_POOL_ID"],
        Username=email,
        UserAttributes=[
            {"Name": "name", "Value": name},
            {"Name": "family_name", "Value": family_name},
            {"Name": "email", "Value": email},
            {"Name": "phone_number", "Value": phone_number},
            {"Name": "email_verified", "Value": "true"},
            {"Name": "phone_number_verified", "Value": "false"},
        ],
        TemporaryPassword=temp_password,
        MessageAction="SUPPRESS",
    )
    print(response)


@cognito_cli.command(
    "admin_change_password", short_help=("Change a user's password.")
)
@click.argument("email")
@click.argument("old_password")
@click.argument("new_password")
def admin_change_password(email, old_password, new_password):
    cognito_idp = boto3.client("cognito-idp")

    client_secret = current_app.config["COGNITO_CLIENT_SECRET"]
    client_id = current_app.config["COGNITO_CLIENT_ID"]

    auth_params = {"USERNAME": email, "PASSWORD": old_password}

    if client_secret:
        auth_params["SECRET_HASH"] = get_secret_hash(
            client_id, client_secret, email
        )

    response = cognito_idp.admin_initiate_auth(
        UserPoolId=current_app.config["COGNITO_USER_POOL_ID"],
        ClientId=current_app.config["COGNITO_CLIENT_ID"],
        AuthFlow="ADMIN_NO_SRP_AUTH",
        AuthParameters=auth_params,
    )

    if response.get("ChallengeName") == "NEW_PASSWORD_REQUIRED":

        auth_params = {"USERNAME": email, "NEW_PASSWORD": new_password}

        if client_secret:
            auth_params["SECRET_HASH"] = get_secret_hash(
                client_id, client_secret, email
            )
        response = cognito_idp.admin_respond_to_auth_challenge(
            UserPoolId=current_app.config["COGNITO_USER_POOL_ID"],
            ClientId=current_app.config["COGNITO_CLIENT_ID"],
            ChallengeName="NEW_PASSWORD_REQUIRED",
            ChallengeResponses=auth_params,
            Session=response.get("Session"),
        )
    else:
        access_token = response["AuthenticationResult"]["AccessToken"]
        response = cognito_idp.change_password(
            PreviousPassword=old_password,
            ProposedPassword=new_password,
            AccessToken=access_token,
        )

    print(response)


def get_secret_hash(client_id, client_secret, username):
    # A keyed-hash message authentication code (HMAC) calculated using
    # the secret key of a user pool client and username plus the client
    # ID in the message.

    message = username + client_id
    dig = hmac.new(
        client_secret.encode("UTF-8"),
        msg=message.encode("UTF-8"),
        digestmod=hashlib.sha256,
    ).digest()
    return base64.b64encode(dig).decode()
