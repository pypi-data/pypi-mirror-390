# coding:utf-8

from datetime import datetime
from typing import Optional


class Timestamp():
    def __init__(self, ts: Optional[datetime] = None) -> None:
        self.__timestamp: datetime = t.astimezone() if (
            t := ts or datetime.now()).tzinfo is None else t

    def __str__(self) -> str:
        return self.dump()

    @property
    def value(self) -> datetime:
        return self.__timestamp

    @property
    def delta(self) -> float:
        return (datetime.now(self.value.tzinfo) - self.value).total_seconds()

    def dump(self) -> str:
        return self.value.isoformat(timespec="milliseconds")

    @classmethod
    def load(cls, timestamp: str) -> "Timestamp":
        return cls(datetime.fromisoformat(timestamp))
