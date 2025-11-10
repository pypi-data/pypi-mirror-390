from pydantic import BaseModel

from model.unifialarmcondition import UnifiAlarmCondition


class UnifiAlarmConditionListItem(BaseModel):
    condition: UnifiAlarmCondition
