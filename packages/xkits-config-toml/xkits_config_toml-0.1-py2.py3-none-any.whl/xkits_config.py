# coding:utf-8

from inspect import isclass
from typing import Any
from typing import Dict
from typing import Iterator
from typing import List
from typing import Type
from typing import TypeVar

from xkits_lib.annot import each_annot

from xkits_config_annot import Annot
from xkits_config_class import parse

__project__ = "xkits-config"
__version__ = "0.1"
__urlhome__ = "https://github.com/bondbox/xconfig/"
__description__ = "Config module"

# author
__author__ = "Mingzhe Zou"
__author_email__ = "zoumingzhe@outlook.com"


TS = TypeVar("TS", bound="Settings")


class Settings():

    def __iter__(self) -> Iterator[str]:
        return iter(vars(self))

    def __setitem__(self, name: str, value: Any) -> None:
        return self.set(name=name, value=value)

    def __getitem__(self, name: str) -> Any:
        return self.get(name=name)

    def __contains__(self, name: str) -> bool:
        return hasattr(self, name)

    def set(self, name: str, value: Any) -> None:
        setattr(self, name, value)

    def get(self, name: str) -> Any:
        return getattr(self, name)

    def dump(self) -> Dict[str, Any]:
        return {k: v.dump() if isinstance(v := self[k], Settings) else v for k in self}  # noqa:E501

    @classmethod
    def load(cls: Type[TS], **kwargs: Any) -> TS:
        args: Dict[str, Any] = {}

        for field in parse(cls):
            if (value := kwargs.get(field.name, field.default)) is Annot.NULL:
                raise ValueError(f"{cls.__name__}.{field.name} no default")

            if isinstance(value, Dict):
                _subclasses: List[Type[Settings]] = []

                for _arg in each_annot(field.type):
                    if isclass(_arg) and issubclass(_arg, Settings):
                        _subclasses.append(_arg)

                if len(_subclasses) > 1:
                    _subclass_str: str = ", ".join(f"'{_sub.__name__}'" for _sub in _subclasses)  # noqa:E501
                    raise TypeError(f"{cls.__name__}.{field.name} has multiple Settings: [{_subclass_str}]")  # noqa:E501

                if len(_subclasses) == 1:
                    value = _subclasses[0].load(**value)

            args[field.name] = value

        return cls(**args)
