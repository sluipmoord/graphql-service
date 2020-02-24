import ast

import boto3
from flask import current_app, request
from graphene.relay import Node
from graphene_sqlalchemy.registry import get_global_registry


def to_local_id(global_id):
    return int(Node.from_global_id(global_id)[1])


def to_local_ids(obj, keys=[]):
    for key in keys:
        if key in obj:
            obj[key] = to_local_id(obj[key])


def to_global_id(model, id):
    registry = get_global_registry()
    _type = registry.get_type_for_model(model)
    if _type:
        return Node.to_global_id(str(_type), id)
    return None


def get_cognito_identity_id():
    cognito_identity_id = None

    if "serverless.event" in request.environ:
        cognito_identity_id = request.environ["serverless.event"][
            "requestContext"
        ]["identity"]["cognitoIdentityId"]

    if not cognito_identity_id:
        current_app.logger.warn(
            "AWS Lambda event is missing. "
            "Fetching Identity ID from Cognito..."
        )
        ci = boto3.client("cognito-identity")
        login_provider = "cognito-idp.{}.amazonaws.com/{}".format(
            current_app.config["AWS_REGION"],
            current_app.config["COGNITO_USER_POOL_ID"],
        )
        response = ci.get_id(
            IdentityPoolId=current_app.config["COGNITO_IDENTITY_POOL_ID"],
            Logins={login_provider: request.headers.get("Authorization")},
        )
        cognito_identity_id = response["IdentityId"]

    current_app.logger.debug("Cognito Idenity ID: %s", cognito_identity_id)
    return cognito_identity_id


def attach_iot_policy(user):
    stage = current_app.config["STAGE"]
    if stage == "local":
        stage = "dev"

    policy_name = "mm-{}-iot-policy".format(stage)

    client = boto3.client("iot")
    client.attach_principal_policy(
        policyName=policy_name, principal=user.cognito_identity_id
    )


def parse_tuple(s):
    t = ast.literal_eval(str(s))
    if type(t) == tuple:
        return t
    else:
        raise ValueError("{} is not a tuple".format(s))


def exclusive_str_search(sub, str):
    sub = sub.replace(" ", "").lower()
    search_str = str.replace(" ", "").lower()

    try:
        index = search_str.index(sub)
        before = search_str[:index]
        after = search_str[index + len(sub) :]

        # There's nothing before or after the string:
        if len(before) == 0 and len(after) == 0:
            return True

        # Make sure the string is encapsulated by special chars:
        result = True
        if len(before) > 0:
            if before[-1].isdigit():
                result = False

        if len(after) > 0:
            if after[0].isdigit():
                result = False

        return result
    except ValueError:
        return False


def list_objects_in_bucket(bucket: str, prefix: str) -> list:
    """List the objects in an S3 bucket.

    Args:
        bucket: S3 bucket name.
        prefix: Object prefix.

    Returns:
        List of object keys, which can be used to retrieve each object.

    """
    s3 = boto3.client("s3")
    response = s3.list_objects(Bucket=bucket, Prefix=prefix)
    keys = []
    if "Contents" in response:
        for obj in response["Contents"]:
            if obj["Key"] == prefix:
                continue
            keys.append(obj["Key"])
    return keys
