# coding:utf-8

from typing import Type
from typing import TypeVar

from xkits_config_file import ConfigFile

TCJ = TypeVar("TCJ", bound="ConfigJSON")


class ConfigJSON(ConfigFile):

    def dumps(self) -> str:
        """dump config to JSON string"""
        from json import dumps  # pylint: disable=import-outside-toplevel
        return dumps(super().dump())

    @classmethod
    def loads(cls: Type[TCJ], data: str) -> TCJ:
        """load config from JSON string"""
        from json import loads  # pylint: disable=import-outside-toplevel
        return cls.load(**loads(data))
