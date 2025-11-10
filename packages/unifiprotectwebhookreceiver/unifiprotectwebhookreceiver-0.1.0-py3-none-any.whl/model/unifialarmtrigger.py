from datetime import datetime

from pydantic import BaseModel, field_validator

from model.unifialarmsource import KeyEnum


class UnifiAlarmTrigger(BaseModel):
    key: KeyEnum
    device: str
    timestamp: datetime
    eventId: str

    @field_validator("timestamp", mode="before")
    def convert_millis_to_datetime(cls, v):
        if isinstance(v, (int, float)):
            # Convert milliseconds to seconds
            return datetime.fromtimestamp(v / 1000)
        return v
