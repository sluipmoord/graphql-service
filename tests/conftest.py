import os

import pytest
from flask import g

from bettr.app import create_app
from bettr.database import db


USER = {
    "cognito_username": "19b5fbf1-a986-48b6-b9a7-f09e31ba6321",
    "email": "bevan@teamgeek.io",
    "name": "Bevan",
    "cognito_groups": [],
}
IDENTITY_ID = "eu-west-1:f3ef5e7d-4fa1-49e7-afd3-451aff5ee641"


@pytest.fixture
def patch_aws_calls(mocker):
    mocker.patch(
        "bettr.utils.get_cognito_identity_id", return_value=IDENTITY_ID
    )
    mocker.patch("bettr.utils.attach_iot_policy")


@pytest.fixture
def app(patch_aws_calls):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    app = create_app(os.path.join(dir_path, "./settings.py"))
    db.create_all(app=app)
    yield app

    db.drop_all(app=app)


@pytest.fixture
def app_context(app):
    with app.app_context() as app_context:
        yield app_context


@pytest.fixture
def request_context(app):
    with app.test_request_context() as request_context:
        g.user = USER
        yield request_context
