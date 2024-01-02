from typing import overload
import xml.etree.ElementTree as ET
XML_KEY_Attrs = '@attributes'
XML_KEY_Value = 'value'


class XmlParser:
    DESC_Version = '<?xml version: "1.0" encoding="UTF-8"?>'
    DESC_Xmlns = 'http://www.isapi.org/ver20/XMLSchema'
    ATTR_Utf8 = {'encoding': 'UTF-8'}
    ATTR_Xmlns = {'xmlns': DESC_Xmlns, 'version': '2.0'}

    @staticmethod
    @overload
    def dict2xml(data: dict, parent_tag: str = None) -> ET.Element:
        ...

    @staticmethod
    @overload
    def dict2xml(data: list, parent_tag: str = None) -> ET.Element:
        ...

    @staticmethod
    def dict2xml(data: dict, tag: str = None) -> ET.Element:
        '''
        @param tag:str:根层级名称
        @param data:dict:字典
        '''

        result = ET.Element(tag)
        if isinstance(data, list):
            for x in data:
                result.append(XmlParser.dict2xml(x))
            return result

        if not isinstance(data, dict):
            result.text = str(data)
            return result

        for x in data:
            if x == XML_KEY_Attrs:
                result.attrib = data[x]
                continue
            val = data[x]
            result.append(XmlParser.dict2xml(val, x))

        return result

    @staticmethod
    def dict2xmlstr(data: dict) -> str:
        x = XmlParser.dict2xml(data)
        return ET.tostring(x).decode()

    @staticmethod
    def element2dict(element: ET.Element) -> tuple[str, dict]:
        '''
        @return tuple[
            str:tag_name
            dict:详细字典
        ]
        '''
        index = -1
        try:
            # 去掉前缀（如果有的话）
            index = element.tag.index('}')
        except:
            pass
        element.tag = element.tag[index+1:]

        d = {}
        has_attrs = element.attrib
        if has_attrs:
            d[XML_KEY_Attrs] = has_attrs

        children = [x for x in element]
        if len(children) == 0:
            if not has_attrs:
                return element.text
            d[XML_KEY_Value] = element.text
            return d

        for child in children:
            child_data = XmlParser.element2dict(child)
            child_tag = child.tag
            if not child_tag in d:
                d[child_tag] = child_data
                continue
            prev_value = d[child_tag]

            if isinstance(prev_value, list):
                d[child_tag].append(child_data)
                continue
            # 首次出现多项 则转为列表
            d[child_tag] = [prev_value, child_data]

        return d

    @staticmethod
    @overload
    def xml2dict(element: str) -> dict:
        ...

    @staticmethod
    @overload
    def xml2dict(element: ET.Element) -> dict:
        ...

    @staticmethod
    def xml2dict(element) -> dict:
        if isinstance(element, str):
            if len(element) < 2:
                return {}
            element = ET.fromstring(element)

        return XmlParser.element2dict(element) or {}
