import json
import traceback

from flask import Blueprint, current_app
from flask_cors import CORS
from flask_graphql import GraphQLView

from ..schema import schema

api = Blueprint("api", __name__)

CORS(api)


class AuthorizationMiddleware:
    def resolve(self, next, root, info, **args):
        return next(root, info, **args)


class ErrorMiddleware:
    def handle_error(self, err):
        tb = getattr(err, "__traceback__", None)
        if tb:
            traceback.print_tb(tb)
        raise err

    def resolve(self, next, root, info, **args):
        return next(root, info, **args).catch(self.handle_error)


api.add_url_rule(
    "/graphql",
    view_func=GraphQLView.as_view(
        "graphql",
        schema=schema,
        middleware=[ErrorMiddleware(), AuthorizationMiddleware()],
        graphiql=True,
    ),
)


@api.after_request
def after(response):
    if response.status_code >= 400:
        data = json.loads(response.get_data())
        current_app.logger.error(data)
    return response
