# coding:utf-8

from typing import Type
from typing import TypeVar

from xkits_config_file import ConfigFile

TCT = TypeVar("TCT", bound="ConfigTOML")


class ConfigTOML(ConfigFile):

    def dumps(self) -> str:
        """dump config to toml string"""
        from toml import dumps  # pylint: disable=import-outside-toplevel
        return dumps(super().dump())

    @classmethod
    def loads(cls: Type[TCT], data: str) -> TCT:
        """load config from toml string"""
        from toml import loads  # pylint: disable=import-outside-toplevel
        return cls.load(**loads(data))
