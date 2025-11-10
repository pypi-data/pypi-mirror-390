from ghkit.enum import GEnum


class EnumTest(GEnum):
    """测试枚举"""

    A = 1, "选项A"
    B = 2, "选项B"
    C = 3, "选项C"


def test_enum_value():
    """测试枚举值"""
    assert EnumTest.A.value == 1
    assert EnumTest.B.value == 2
    assert EnumTest.C.value == 3


def test_enum_desc():
    """测试枚举描述"""
    assert EnumTest.A.desc == "选项A"
    assert EnumTest.B.desc == "选项B"
    assert EnumTest.C.desc == "选项C"


def test_enum_to_dict():
    """测试枚举转字典"""
    assert EnumTest.to_dict() == {1: "选项A", 2: "选项B", 3: "选项C"}


def test_enum_to_list():
    """测试枚举转列表"""
    assert EnumTest.to_list() == [
        {"value": 1, "desc": "选项A"},
        {"value": 2, "desc": "选项B"},
        {"value": 3, "desc": "选项C"},
    ]


def test_enum_get():
    """测试枚举获取"""
    assert EnumTest.get(1) == EnumTest.A
    assert EnumTest.get(2) == EnumTest.B
    assert EnumTest.get(3) == EnumTest.C
    assert EnumTest.get(4) is None
