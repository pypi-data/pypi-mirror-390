# coding:utf-8

from typing import Optional
from typing import Type
from typing import TypeVar

from xkits_config import Settings

TCF = TypeVar("TCF", bound="ConfigFile")


class ConfigFile(Settings):
    DEFAULT_FILE: str = "xconfig"

    @property
    def filepath(self) -> str:
        return getattr(self, "__xconfig_file__")

    @filepath.setter
    def filepath(self, value: str) -> None:
        setattr(self, "__xconfig_file__", value)

    def dumps(self) -> str:
        raise NotImplementedError()

    def dumpf(self, path: Optional[str] = None) -> str:
        """dump config to file"""
        from xkits_file import SafeWrite  # pylint: disable=C0415
        filepath: str = path or self.filepath
        with SafeWrite(filepath, encoding=None, truncate=True) as whdl:
            whdl.write(self.dumps().encode("utf-8"))
            return filepath

    @classmethod
    def loads(cls: Type[TCF], data: str) -> TCF:
        raise NotImplementedError()

    @classmethod
    def loadf(cls: Type[TCF], path: str = DEFAULT_FILE) -> TCF:
        """load config from file"""
        from xkits_file import SafeRead  # pylint: disable=C0415
        with SafeRead(path, encoding=None) as rhdl:
            data: bytes = rhdl.read()

        instance = cls.loads(data=data.decode("utf-8"))
        instance.filepath = path
        return instance
