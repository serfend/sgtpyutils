from typing import overload
from .data_tree import *

@overload
def merge_tree(merge_to: dict, merge_from: dict, children_key: str = 'children', id_key: str = 'id', remove_addtional: bool = True):
    pass


@overload
def merge_tree(merge_to: list, merge_from: list, children_key: str = 'children', id_key: str = 'id', remove_addtional: bool = True):
    pass


def merge_tree(merge_to, merge_from, children_key: str = 'children', id_key: str = 'id', remove_addtional: bool = True):
    # print('merge_to', merge_to, 'merge_from', merge_from)
    if merge_to is None or merge_from is None:
        return
    if not isinstance(merge_to, type(merge_from)):
        raise Exception(
            f'merge_to\'s type({type(merge_to)}) should equal to merge_from\'s({type(merge_from)}).')
    if not isinstance(merge_to, list) and not isinstance(merge_to, dict):
        raise Exception('obj should be list or dict')
    if isinstance(merge_to, list):
        # 收集目标
        merge_to_dict = {}
        for x in merge_to:
            merge_to_dict[x[id_key]] = x

        # 收集来源
        merge_from_dict = {}
        for x in merge_from:
            merge_from_dict[x[id_key]] = x

        # 找到目标原有的项并更新
        additional_merge_to_dict = {}
        for x in merge_to_dict:
            if not x in merge_from_dict:
                additional_merge_to_dict[x] = True  # merge_to 多出的
                continue
            item = merge_from_dict[x]
            merge_tree(merge_to_dict[x], item,
                       children_key, id_key, remove_addtional)
            del merge_from_dict[x]

        # 删除原来多余的项
        if remove_addtional:
            index_to_remove = []
            index_counter = 0  # 每次删除序号向前
            for index, x in enumerate(merge_to):
                if x[id_key] in additional_merge_to_dict:
                    index_to_remove.append(index-index_counter)
                    index_counter += 1
            for x in index_to_remove:
                merge_to.pop(x)

        # 找到来源多余的项附加
        for x in merge_from_dict:
            item = merge_from_dict[x]
            merge_to.append(item)
        return

    # 目标与来源同级
    if merge_to[id_key] != merge_from[id_key]:
        raise Exception('merge_to\'s id should equal to merge_from\'s.')

    # 将本级数据更新
    raw_children = merge_to.get(children_key)
    merge_to.update(merge_from)
    merge_to[children_key] = raw_children

    # 更新子层级数据
    from_children = merge_from.get(children_key)
    if from_children and len(from_children):
        if raw_children is None:
            merge_to[children_key] = []
        merge_tree(merge_to.get(children_key), from_children)
    return merge_to
