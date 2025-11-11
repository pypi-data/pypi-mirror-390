# coding:utf-8

from typing import Union

TimeUnit = Union[float, int]


class DataUnit:
    def __init__(self, value: int):
        self.__value: int = value

    @property
    def bytes(self) -> int:
        return self.__value

    @property
    def human(self) -> str:  # pylint: disable=too-many-return-statements
        """Thousand base prefix (ISO 80000-1)"""
        if -1000 < self.__value < 1000:
            return f"{self.__value}"
        value: float = self.__value / 1000
        if -1000 < value < 1000:
            return f"{value:.2f}k"
        value /= 1000
        if -1000 < value < 1000:
            return f"{value:.2f}M"
        value /= 1000
        if -1000 < value < 1000:
            return f"{value:.2f}G"
        value /= 1000
        if -1000 < value < 1000:
            return f"{value:.2f}T"
        value /= 1000
        if -1000 < value < 1000:
            return f"{value:.2f}P"
        value /= 1000
        if -1000 < value < 1000:
            return f"{value:.2f}E"
        value /= 1000
        if -1000 < value < 1000:
            return f"{value:.2f}Z"
        value /= 1000
        return f"{value:.2f}Y"

    @property
    def ihuman(self) -> str:  # pylint: disable=too-many-return-statements
        """Thousand binary prefix (IEC 80000-13)"""
        if -1024 < self.__value < 1024:
            return f"{self.__value}B"
        value: float = self.__value / 1024
        if -1024 < value < 1024:
            return f"{value:.2f}KiB"
        value /= 1024
        if -1024 < value < 1024:
            return f"{value:.2f}MiB"
        value /= 1024
        if -1024 < value < 1024:
            return f"{value:.2f}GiB"
        value /= 1024
        if -1024 < value < 1024:
            return f"{value:.2f}TiB"
        value /= 1024
        if -1024 < value < 1024:
            return f"{value:.2f}PiB"
        value /= 1024
        if -1024 < value < 1024:
            return f"{value:.2f}EiB"
        value /= 1024
        if -1024 < value < 1024:
            return f"{value:.2f}ZiB"
        value /= 1024
        return f"{value:.2f}YiB"
