from flask.json import JSONEncoder
from datetime import date


class JSONEncoderISO8601(JSONEncoder):
    """A JSONEnCoder that encodes dates using ISO8601 instead of rfc 2616"""

    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()

        return super().default(obj)
