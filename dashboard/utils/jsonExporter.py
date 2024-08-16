import json
from io import StringIO
from django.core.serializers.json import DjangoJSONEncoder

class JSONExporter:

    def __init__(self, query):
        self.query = query

    def get_output(self, **kwargs):
        res = self.query.execute_query_only()
        return self._get_output(res, **kwargs)

    def _get_output(self, res, **kwargs):
        data = []
        for row in res.data:
            data.append(
                dict(zip(
                    [str(h) if h is not None else "" for h in res.headers],
                    row
                ))
            )

        json_data = json.dumps(data, cls=DjangoJSONEncoder)
        return json_data