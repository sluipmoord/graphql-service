import enum
import datetime
import json


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, enum.Enum):
            return str(obj)
        if isinstance(obj, datetime.date):
            return str(obj)
        if isinstance(obj, datetime.datetime):
            return str(obj)
        return json.JSONEncoder.default(self, obj)
