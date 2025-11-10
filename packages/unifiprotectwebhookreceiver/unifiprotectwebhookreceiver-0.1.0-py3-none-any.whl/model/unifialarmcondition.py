from pydantic import BaseModel


class UnifiAlarmCondition(BaseModel):
    type: str
    source: str
