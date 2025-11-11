import json
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class Message:
    """Redis Streams message container.

    Description:
        A simple dataclass that encapsulates a message name and body payload
        for transmission over Redis Streams. Provides JSON encoding for
        serialization into Redis stream fields. This message structure is
        used by both AsyncRedisStreamer and RedisStreamer for publishing
        and consuming messages.

    Attributes:
        name (str): The message type or event name identifier used to route
            messages to appropriate handlers.
        body (Dict[str, Any]): The message payload as a dictionary containing
            the actual data to be transmitted.
    """

    name: str
    body: Dict[str, Any]

    def get_json_encoded(self) -> Dict[str, str]:
        """Return a JSON-encoded representation of the message.

        Description:
            Converts the message into a dictionary with the name as-is and
            the body JSON-serialized to a string. This format is compatible
            with Redis Streams XADD commands.

        Returns:
            Dict[str, str]: Dictionary with 'name' and JSON-encoded 'body'.
        """
        return {"name": self.name, "body": json.dumps(self.body, default=str)}
