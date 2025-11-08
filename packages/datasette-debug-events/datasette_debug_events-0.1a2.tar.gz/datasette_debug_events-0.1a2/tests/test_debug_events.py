from datasette.app import Datasette
import json
import pytest


@pytest.mark.asyncio
async def test_debug_events(capsys):
    datasette = Datasette()
    response = await datasette.client.get("/-/auth-token?token={}".format(datasette._root_token))
    assert response.status_code == 302
    captured = capsys.readouterr()
    assert json.loads(captured.err) == {'name': 'login', 'actor': {'id': 'root'}, 'properties': {}}
