import json

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from .json import JSONEncoder


def json_serializer(obj):
    return json.dumps(obj, cls=JSONEncoder)


db = SQLAlchemy(engine_options={"json_serializer": json_serializer})
migrate = Migrate()
