from datetime import datetime
from typing_extensions import Annotated
from pydantic import PlainSerializer
from enum import Enum

BlockbaxDatetime = Annotated[
    datetime,
    PlainSerializer(
        lambda d: int(d.timestamp() * 1000),
        return_type=int,
        when_used="unless-none",
    ),
]
