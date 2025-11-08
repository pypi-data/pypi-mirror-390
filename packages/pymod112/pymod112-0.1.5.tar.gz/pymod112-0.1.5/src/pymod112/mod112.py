from typing import Dict, List
import pickle
import time
import os

CODE2ERROR = {
    "000": "不存在问题",
    "001": "缺失关键文件",
    "002": "参数location长度错误",
    "003": "参数code长度错误",
    "004": "参数id长度错误",
    "005": "参数id内容包含非法字符",
    "006": "参数id不合法",
    "007": "参数id中包含不存在的地区",
    "008": "参数id中包含不存在的时间",
}

RCLIST = ["24", "20"]


def code2location(code: str, rc_time: str = RCLIST[0]) -> List[str] | str:
    """
    通过中华人民共和国县以上行政区划代码获取对应单位名称(地方名称)\n
    \n
    参数\n
    code: str -> 长度为6的行政区划代码\n
    可选参数\n
    rc_time: str -> 指定区划代码年份， 默认为最新\n
    输出\n
    list -> [<省>, <市>, <县>]\n
    注1：存在不存在的省、市或县的返回的对应值为空字符串\n
    注2：部分地区（如直辖市）返回值中市对应的值为空字符串\n
    注3：如果关键文件缺失会返回字符串"001"\n
    """

    # 参数检查
    if not isinstance(code, str):  # pyright: ignore[reportUnnecessaryIsInstance]
        raise TypeError("'code' should be a string")
    elif not isinstance(rc_time, str):  # pyright: ignore[reportUnnecessaryIsInstance]
        raise TypeError("'rc_time' should be a string")
    elif len(code) != 6:
        return "003"

    # 查询
    workplace = os.getcwd()
    os.chdir(os.path.dirname(__file__))
    result: List[str] = []
    try:
        with open("./RegionCode_" + rc_time, "rb") as f:
            region_code: Dict[str, str] = pickle.load(f)  # 例{code:name}
        result = [
            region_code.get(f"{code[:2]}0000", ""),
            region_code.get(f"{code[:2]}{code[2:4]}00", ""),
            region_code.get(f"{code[:2]}{code[2:4]}{code[4:6]}", ""),
        ]
    except FileNotFoundError:
        return "001"
    except:
        pass
    os.chdir(workplace)
    return result


def location2code(location: List[str], rc_time: str = RCLIST[0]) -> str:
    """
    通过单位名称(地方名称)获取对应中华人民共和国县以上行政区划代码\n
    \n
    参数\n
    location: list -> 将单位名称(地方名称)按省、市、县顺序排列\n
    例：["四川省", "成都市", "青羊区"]\n
    可选参数\n
    rc_time: str -> 指定区划代码年份，默认为最新\n
    输出\n
    str -> 长度为6的行政区划代码\n
    注1：传入不存在地区则返回值为空字符串\n
    注2：部分地区（如直辖市）传入的列表或元组元素个数为2\n
    注3：如果关键文件缺失会返回字符串"001"\n
    注4：如果为直辖市则传入参数只需有两个元素，元素个数异常会返回字符串"002"\n
    """

    # 参数检查
    if not isinstance(
        location, (list, tuple)
    ):  # pyright: ignore[reportUnnecessaryIsInstance]
        raise TypeError("'location' should be a list or tuple")
    elif not isinstance(rc_time, str):  # pyright: ignore[reportUnnecessaryIsInstance]
        raise TypeError("'rc_time' should be a string")
    elif not (len(location) in (2, 3)):
        return "002"
    elif not (
        isinstance(location[0], str)  # pyright: ignore[reportUnnecessaryIsInstance]
        and isinstance(location[1], str)  # pyright: ignore[reportUnnecessaryIsInstance]
    ):
        raise TypeError("The element type in 'location' must be a string")
    elif len(location) == 3:
        if not (
            isinstance(location[2], str)
        ):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise TypeError("The element type in 'location' must be a string")

    # 查询
    workplace = os.getcwd()
    os.chdir(os.path.dirname(__file__))
    try:
        with open("./RegionCode_" + rc_time, "rb") as f:
            region_code: Dict[str, str] = pickle.load(f)  # 例{code:name}
    except FileNotFoundError:
        return "001"

    result: str = ""
    try:
        result += list(region_code.keys())[
            list(region_code.values()).index(location[0])
        ][:2]
        if len(location) == 2:
            result += "01"
            result += list(region_code.keys())[
                list(region_code.values()).index(location[1])
            ][4:6]
        else:
            result += list(region_code.keys())[
                list(region_code.values()).index(location[1])
            ][2:4]
            result += list(region_code.keys())[
                list(region_code.values()).index(location[2])
            ][4:6]
    except:
        result = ""

    os.chdir(workplace)
    return result


def mod112(
    id: str,
    time_check: bool = True,
    location_check: bool = False,
    details: bool = False,
    rc_time: str = RCLIST[0],
) -> bool | Dict[str, int | bool | str | list[str]]:
    """
    检验传入的ID是否是符合规范的中华人民共和国公民身份号码。\n
    该检验无法接入公安系统故无法检验传入的ID是否真实存在。\n
    \n
    参数\n
    id: str -> 传入内容即为需要检验的ID，最后一位自动忽略大小写\n
    time_check：bool -> 传入True则会检验时间是否合法以防止出现不存在的时间，时间基准来自于本地\n
    location_check：bool ->传入True则会检验地址真实性，默认不检查\n
    details: bool -> 传入True则会输出类型为dict, 传入False则会输出类型为bool\n
    输出\n
    bool -> True即表示id合法，False则表示不合法\n
    dict -> {"id":<你传入的id:str>,\n
             "province":[<编号:int>, <名称:str>],\n
             "city":[<编号:int>, <名称:str>],\n
             "county":[<编号:int>, <名称:str>],\n
             "birth_date":[<年:int>, <月:int>, <日:int>],\n
             "gender":<性别:str>,\n
             "result":<检验结果:bool>,\n
             "problem":<问题代码:str>}\n
    注1：输出详情中不存在的会用空字符串代替\n
    注2：问题代码为"000"时表示不存在问题\n
    """

    def analyse(code: str = "000") -> bool | Dict[str, int | bool | str | list[str]]:
        """
        结束函数
        """

        # 参数检查
        if not isinstance(code, str):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise TypeError("'code' should be a string")

        # 输出
        if details:  # 输出详情
            result: Dict[str, int | bool | str | list[str]] = {
                "id": id,
                "province": ["", ""],
                "city": ["", ""],
                "county": ["", ""],
                "birth_date": ["", "", ""],
                "gender": "",
                "result": False,
                "problem": code,
            }
            if code == "000":
                result["result"] = True
            if not (code in ("004", "005")):  # id不合法但长度内容符合要求
                result["birth_date"] = [
                    str(birth_date[0]),
                    str(birth_date[1]),
                    str(birth_date[2]),
                ]
                result["gender"] = "男" if gender == 1 else "女"
            result.update(location)
            return result
        else:  # 简单输出
            if code == "000":
                return True
            else:
                return False

    # 变量设置
    location = {"province": ["", ""], "city": ["", ""], "county": ["", ""]}

    # 参数类型检查
    if not isinstance(id, str):  # pyright: ignore[reportUnnecessaryIsInstance]
        raise TypeError("'id' should be a string")
    if not isinstance(time_check, bool):  # pyright: ignore[reportUnnecessaryIsInstance]
        raise TypeError("'time_check' should be a bool")
    if not isinstance(details, bool):  # pyright: ignore[reportUnnecessaryIsInstance]
        raise TypeError("'details' should be a bool")
    if not id[:17].isnumeric():  # 前17位必须是数字
        return analyse("005")
    if not (
        id[17:18].isnumeric() or id[17:18] in ("x", "X")
    ):  # 最后一位必须是数字或大小写X
        return analyse("005")

    # 参数预处理
    if len(id) == 18:
        address = [id[:2], id[2:4], id[4:6]]
        birth_date = [int(id[6:10]), int(id[10:12]), int(id[12:14])]
        gender = int(id[16:17]) % 2
        check_code = id[17:18]
    else:
        return analyse("004")

    # 合法性检查
    # 校验码
    calculation_result = 0
    list1 = list(id[:17])
    for position, i in enumerate(list1):  # mod11-2(1)
        calculation_result += int(i) * 2 ** (18 - (position + 1))
    calculation_result = (12 - (calculation_result % 11)) % 11  # mod11-2(2)
    if check_code in ("x", "X") and calculation_result == 10:
        pass
    elif str(calculation_result) == check_code:
        pass
    else:
        return analyse("006")

    location["province"][0] = address[0]
    location["city"][0] = address[1]
    location["county"][0] = address[2]
    # 地址真实性
    if location_check:
        if isinstance(code2location(id[0:6], rc_time), str):
            return analyse("001")
        else:
            location["province"][1], location["city"][1], location["county"][1] = (
                code2location(id[0:6], rc_time)
            )
            if location["province"][1] == "":
                return analyse("007")
    else:
        pass

    # 时间合理性（只检测时间是否存在或在未来）
    if time_check:
        if birth_date[0] < 1900:  # 出生时间早于1900年
            return analyse("008")
        elif birth_date[0] < int(time.strftime("%Y", time.localtime())):  # 过去年
            if birth_date[1] <= 12 and 1 <= birth_date[1]:  # 月
                if birth_date[1] in [1, 3, 5, 7, 8, 10, 12]:  # 大月的日
                    if birth_date[2] <= 31 and 1 <= birth_date[2]:
                        pass
                    else:
                        return analyse("008")
                elif birth_date[1] in [4, 6, 9, 11]:  # 小月的日
                    if birth_date[2] <= 30 and 1 <= birth_date[2]:
                        pass
                    else:
                        return analyse("008")
                else:  # 2月
                    if birth_date[0] % 4 == 0:  # 闰月的日
                        if birth_date[2] <= 29 and 1 <= birth_date[2]:
                            pass
                        else:
                            return analyse("008")
                    else:  # 平月的日
                        if birth_date[2] <= 28 and 1 <= birth_date[2]:
                            pass
                        else:
                            return analyse("008")
            else:
                return analyse("008")
        elif birth_date[0] == int(time.strftime("%Y", time.localtime())):  # 同年
            if birth_date[1] < int(time.strftime("%m", time.localtime())):  # 过去月
                pass
            elif birth_date[1] == int(time.strftime("%m", time.localtime())):  # 同月
                if birth_date[2] <= int(
                    time.strftime(r"%d", time.localtime())
                ):  # 非未来日
                    pass
                else:  # 同年同月未来日
                    return analyse("008")
            else:  # 同年未来月
                return analyse("008")
        else:  # 未来年
            return analyse("008")
    else:
        pass
        analyse()

    # 输出
    return analyse("000")
