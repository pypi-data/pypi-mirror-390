import base64
import re
from io import BytesIO

from PIL import Image

from pydantic import BaseModel, field_validator

from model.unifialarmcionditionlistitem import UnifiAlarmConditionListItem
from model.unifialarmsource import UnifiAlarmSource
from model.unifialarmtrigger import UnifiAlarmTrigger

THUMBNAIL_PATTERN = re.compile(r"^data:image/(jpeg|png);base64,[A-Za-z0-9+/]+=*$")


class UnifiAlarm(BaseModel):
    name: str
    sources: list[UnifiAlarmSource]
    conditions: list[UnifiAlarmConditionListItem]
    triggers: list[UnifiAlarmTrigger]
    eventLocalLink: str | None = None
    eventPath: str | None = None
    thumbnail: str | None = None

    @field_validator("thumbnail")
    def validate_thumbnail(cls, v):
        if not THUMBNAIL_PATTERN.match(v):
            raise ValueError("Invalid image data URL")
        header, b64data = v.split(",", 1)
        try:
            img_bytes = base64.b64decode(b64data)
            Image.open(BytesIO(img_bytes)).verify()
        except Exception:
            raise ValueError("Invalid or corrupt image data")
        return v
