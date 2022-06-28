from .full_tree import BinaryTree
from typing import List, Type, overload
from .node import Node

class BinaryTree(BinaryTree):

    @staticmethod
    def from_full_tree(data) -> BinaryTree:
        t = BinaryTree(as_type=type(data))
        if data is None:
            return t
        data = BinaryTree.__convert_data(data)
        [t.add_as_full_tree(x) for x in data]
        return t

    @staticmethod
    def __from_full_tree_order(data: List, order: int = 0) -> BinaryTree:
        node = Node(None)
        pos = len(data) >> 1
        if pos == 0:
            node.data = data.pop(0)
            return node
        if order == 0:
            node.data = data.pop(0)
        node.lchild = BinaryTree.__from_full_tree_order(data[0:pos], order)
        if order == 1:
            node.data = data.pop(0)
        node.rchild = BinaryTree.__from_full_tree_order(data[pos:], order)
        if order == 2:
            node.data = data.pop(0)
        return node

    @staticmethod
    def from_full_tree_order(data: List, order: int = 0):
        as_type = type(data)
        data = BinaryTree.__convert_data(data)
        assert int(bin(len(data)+1)
                   [3:]) == 0, 'only data length to 2^n can be resolved'
        tree_data = BinaryTree.__from_full_tree_order(data, order)
        return BinaryTree(tree_data, as_type=as_type)

    @staticmethod
    def from_full_tree_preorder(data: List):
        return BinaryTree.from_full_tree_order(data, 0)

    @staticmethod
    def from_full_tree_inorder(data: List):
        return BinaryTree.from_full_tree_order(data, 1)

    @staticmethod
    def from_full_tree_postorder(data: List):
        return BinaryTree.from_full_tree_order(data, 2)
