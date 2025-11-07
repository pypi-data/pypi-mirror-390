import re
from typing import Dict, Optional

# 以下示例常量位置：把你从 PHP 转换得到的完整 dict 放到这里（覆盖示例数据）
PROVINCE_MAP = {
    "北京市": 110000,
    "天津市": 120000,
    # ...把完整的省映射放这里（name -> code）...
}

CITY_MAP = {
    "北京市": 110100,
    "天津市": 120100,
    # ...把完整的市映射放这里（name -> code）...
}

DISTRICT_MAP = {
    "东城区": 110101,
    "西城区": 110102,
    "海淀区": 110108,
    # ...把完整的区映射放这里（name -> code）...
}


class AddressParser:
    def __init__(self,
                 province_map: Optional[Dict[str, int]] = None,
                 city_map: Optional[Dict[str, int]] = None,
                 district_map: Optional[Dict[str, int]] = None):
        """
        province_map / city_map / district_map: dict[name]->code
        推荐将你提供的 PHP 数组转换为 JSON，再 load 成 Python dict 传入。
        如果不传入参数，默认使用文件顶部的 PROVINCE_MAP / CITY_MAP / DISTRICT_MAP。
        """
        # 使用传入映射或文件顶部的默认映射
        self.province_map = province_map or PROVINCE_MAP
        self.city_map = city_map or CITY_MAP
        self.district_map = district_map or DISTRICT_MAP

        # 按名称长度降序，优先匹配长的名称（避免“市”“省”类短名误匹配）
        self._province_names = sorted(self.province_map.keys(), key=len, reverse=True)
        self._city_names = sorted(self.city_map.keys(), key=len, reverse=True)
        self._district_names = sorted(self.district_map.keys(), key=len, reverse=True)

    @staticmethod
    def _normalize(s: str) -> str:
        if not s:
            return ""
        s = s.strip()
        # 全角空格、连续空白统一为单空格
        s = re.sub(r'\s+', ' ', s.replace('\u3000', ' '))
        return s

    def parse(self, addr: str) -> Dict[str, Optional[str]]:
        """
        返回字典:
        {
            "province": 名称或 None,
            "province_code": int or None,
            "city": 名称 or None,
            "city_code": int or None,
            "district": 名称 or None,
            "district_code": int or None,
            "detail": 剩余详细地址 (trim)
        }
        """
        addr = self._normalize(addr or "")
        result = {
            "province": None, "province_code": None,
            "city": None, "city_code": None,
            "district": None, "district_code": None,
            "detail": ""
        }
        if not addr:
            return result

        # 先尝试省匹配（在字符串任意位置匹配，但优先开头）
        remaining = addr
        matched = None
        for name in self._province_names:
            if remaining.startswith(name) or name in remaining:
                matched = name
                break
        if matched:
            result["province"] = matched
            result["province_code"] = self.province_map.get(matched)
            # 删除匹配片段（第一次出现）
            remaining = remaining.replace(matched, "", 1).strip()

        # 再尝试市匹配
        matched = None
        for name in self._city_names:
            if remaining.startswith(name) or name in remaining:
                matched = name
                break
        if matched:
            result["city"] = matched
            result["city_code"] = self.city_map.get(matched)
            remaining = remaining.replace(matched, "", 1).strip()

        # 再尝试区匹配
        matched = None
        for name in self._district_names:
            if remaining.startswith(name) or name in remaining:
                matched = name
                break
        if matched:
            result["district"] = matched
            result["district_code"] = self.district_map.get(matched)
            remaining = remaining.replace(matched, "", 1).strip()

        # 反向推断：如果 city 缺失但 district_code 有，则通过 district_code 推断 city
        if not result["city"] and result["district_code"]:
            try:
                dcode = int(result["district_code"])
                # 市级编码通常是前6位中间部分，例如 district 110101 -> city_code 110100
                candidate_city_code = (dcode // 100) * 100
                for cname, ccode in self.city_map.items():
                    if int(ccode) == int(candidate_city_code):
                        result["city"] = cname
                        result["city_code"] = ccode
                        break
            except Exception:
                pass

        # 反向推断：如果 province 缺失但 city_code 有，则通过 city_code 推断 province
        if not result["province"] and result["city_code"]:
            try:
                ccode = int(result["city_code"])
                candidate_province_code = (ccode // 10000) * 10000
                for pname, pcode in self.province_map.items():
                    if int(pcode) == int(candidate_province_code):
                        result["province"] = pname
                        result["province_code"] = pcode
                        break
            except Exception:
                pass

        # 如果省已知但 city 未知，仍可尝试在剩余字符串中匹配城市名（覆盖之前逻辑）
        if result["province"] and not result["city"]:
            for name in self._city_names:
                if name in remaining:
                    result["city"] = name
                    result["city_code"] = self.city_map.get(name)
                    remaining = remaining.replace(name, "", 1).strip()
                    break

        result["detail"] = remaining
        return result

    def set_maps(self,
                 province_map: Optional[Dict[str, int]] = None,
                 city_map: Optional[Dict[str, int]] = None,
                 district_map: Optional[Dict[str, int]] = None):
        """在运行时更新映射并重建内部排序列表"""
        if province_map is not None:
            self.province_map = province_map
            self._province_names = sorted(self.province_map.keys(), key=len, reverse=True)
        if city_map is not None:
            self.city_map = city_map
            self._city_names = sorted(self.city_map.keys(), key=len, reverse=True)
        if district_map is not None:
            self.district_map = district_map
            self._district_names = sorted(self.district_map.keys(), key=len, reverse=True)


# 简单使用示例（在项目中请把 PHP 数组转换为 JSON，再 load 到 Python dict）
# from address_pars import AddressParser
# parser = AddressParser(province_map=prov_dict, city_map=city_dict, district_map=district_dict)
# print(parser.parse("北京市海淀区中关村大街27号"))