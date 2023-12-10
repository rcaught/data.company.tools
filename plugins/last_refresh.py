import json
from datasette import hookimpl


@hookimpl
def get_metadata(datasette, key, database, table):
    try:
        last_refresh_file = open(f"{datasette.plugins_dir}/last_refresh.json", "r")
    except FileNotFoundError:
        return {"last_refresh": "unknown"}
    else:
        with last_refresh_file:
            return json.loads(last_refresh_file.read())
