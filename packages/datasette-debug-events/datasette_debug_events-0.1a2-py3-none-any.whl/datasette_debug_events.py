from datasette import hookimpl
import json
import sys


@hookimpl
def track_event(event):
    name = event.name
    actor = event.actor
    properties = event.properties()
    msg = json.dumps(
        {
            "name": name,
            "actor": actor,
            "properties": properties,
        },indent=2
    )
    print(msg, file=sys.stderr, flush=True)
