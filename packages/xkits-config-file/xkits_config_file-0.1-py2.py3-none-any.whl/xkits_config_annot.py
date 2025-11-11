# coding:utf-8

from typing import Any


class Annot():

    class _NULL_TYPE:  # pylint: disable=too-few-public-methods
        pass

    NULL = _NULL_TYPE()

    def __init__(self, name: str, type: Any, default: Any = NULL):  # noqa:E501, pylint: disable=redefined-builtin
        self.__name: str = name
        self.__type: Any = type
        self.__default: Any = default

    def __str__(self) -> str:
        return f"Annot(name={repr(self.name)},type={repr(self.type)},default={repr(self.default)})"  # noqa:E501

    @property
    def name(self) -> str:
        return self.__name

    @property
    def type(self) -> Any:
        return self.__type

    @property
    def default(self) -> Any:
        return self.__default
