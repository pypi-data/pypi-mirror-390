# coding:utf-8

from typing import Type
from typing import TypeVar

from xkits_config_file import ConfigFile

TCY = TypeVar("TCY", bound="ConfigYAML")


class ConfigYAML(ConfigFile):

    def dumps(self) -> str:
        """dump config to yaml string"""
        from yaml import dump  # pylint: disable=import-outside-toplevel
        return dump(super().dump(), allow_unicode=True)

    @classmethod
    def loads(cls: Type[TCY], data: str) -> TCY:
        """load config from yaml string"""
        from yaml import safe_load  # pylint: disable=import-outside-toplevel
        return cls.load(**safe_load(data))
