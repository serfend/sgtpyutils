from typing import overload
import xml.etree.ElementTree as ET
XML_KEY_Attrs = '@attributes'
XML_KEY_Value = 'value'


@overload
def dict2xml(tag: str, data: dict) -> ET.Element:
    ...


def dict2xml(tag: str, data: dict) -> ET.Element:
    '''
    @param tag:str:根层级名称
    @param data:dict:字典
    '''
    result = ET.Element(tag)
    if not isinstance(data, dict):
        result.text = str(data)
        return result
    for x in data:
        val = data[x]
        if not isinstance(val, list):
            val = [val]  # 转换为列表统一处理
        for item in val:
            result.append(dict2xml(x, item))
    return result


def dict2xmlstr(tag: str, data: dict) -> str:
    x = dict2xml(tag, data)
    return ET.tostring(x).decode()


def xml_element2dict(element: ET.Element) -> tuple[str, dict]:
    '''
    @return tuple[
        str:tag_name
        dict:详细字典
    ]
    '''
    index = element.tag.index('}')
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
        child_data = xml_element2dict(child)
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


@overload
def xml2dict(element: str) -> dict:
    ...


@overload
def xml2dict(element: ET.Element) -> dict:
    ...


def xml2dict(element) -> dict:
    if isinstance(element, str):
        element = ET.fromstring(element)

    return xml_element2dict(element)
