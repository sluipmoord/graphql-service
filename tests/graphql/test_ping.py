from graphene.test import Client

from bettr.schema import schema


def test_ping(app_context, request_context):
    client = Client(schema)
    executed = client.execute(
        """
        {
            ping
        }
        """
    )

    assert executed["data"]["ping"] == "pong"
