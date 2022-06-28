from .node import Node
from typing import List, Type, overload
from ..extensions import flat

class BinaryTree():

    def __init__(self, root=None, as_type: Type = None):
        self.root = root
        self.as_type = as_type or (type(root) if root else List)
        pass

    @staticmethod
    def __convert_data(data) -> List:
        '''
            conver data to List
        '''
        if not data:
            return None
        if isinstance(data, str) or isinstance(data, bytes):
            data = [x for x in data]
        return list(data)

    def __convert_list(self, data_list: List) -> any:
        '''
            convert list to data determine by `as_type`
        '''
        if self.as_type == List:
            return data_list
        if self.as_type == str:
            return ''.join([str(x) for x in data_list])
        if self.as_type == bytes:
            return b''.join(bytes(x) for x in data_list)
        return data_list

    def __travel(self, node: Node, order: int = 0) -> List[Node]:
        if node is None:
            return None
        left = self.__travel(node.lchild, order)
        right = self.__travel(node.rchild, order)
        r = [left, right]
        r.insert(order, node)
        result = [x for x in flat(r) if x]
        return result  # concat result

    def travel(self, node: Node = None, order: int = 0) -> List:
        if node is None:
            node = self.root
        result = self.__travel(node, order)
        result = [x.data for x in result]
        return self.__convert_list(result)

    def travel_preorder(self, node: Node = None) -> List:
        return self.travel(node, 0)

    def travel_inorder(self, node: Node = None) -> List:
        return self.travel(node, 1)

    def travel_postorder(self, node: Node = None) -> List:
        return self.travel(node, 2)

