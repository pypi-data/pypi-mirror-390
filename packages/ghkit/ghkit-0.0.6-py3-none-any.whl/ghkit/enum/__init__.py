from enum import Enum
from typing import Any, Dict, List, Optional, TypeVar

T = TypeVar("T")


class GEnum(Enum):
    """枚举基类"""

    def __new__(cls, value: Any, desc: Any = None):
        """
        创建枚举成员
        :param value: 枚举成员的值
        :param desc: 枚举成员的描述信息
        """
        if issubclass(cls, str):
            obj = str.__new__(cls, value)
        elif issubclass(cls, int):
            obj = int.__new__(cls, value)
        else:
            obj = object.__new__(cls)
        obj._value_ = value
        obj._desc_ = desc
        return obj

    @property
    def desc(self) -> Any:
        """获取描述"""
        return self._desc_

    def __str__(self) -> str:
        """字符串表示"""
        return str(self.value)

    def __repr__(self) -> str:
        """对象表示"""
        return f"{self.__class__.__name__}(value='{self.value}', desc='{self.desc}')"

    @classmethod
    def to_dict(cls) -> Dict[Any, str]:
        """转换为字典，key为值，value为描述"""
        return {v.value: v.desc for v in cls.__members__.values()}

    @classmethod
    def to_list(cls) -> List[Dict[str, Any]]:
        """转换为列表，每个元素为包含value和desc的字典"""
        return [{"value": v.value, "desc": v.desc} for v in cls.__members__.values()]

    @classmethod
    def get(cls, value: Any) -> Optional["GEnum"]:
        """根据值获取枚举"""
        for v in cls.__members__.values():
            if v.value == value:
                return v
        return None
