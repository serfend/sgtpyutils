from .base_tree import BinaryTree
from typing import List, Type, overload
from .node import Node

class BinaryTree(BinaryTree):

    def add_as_full_tree(self, item):
        '''
        按满二叉树添加
        '''
        node = Node(item)
        if self.root is None:
            self.root = node
            return
        queue = [self.root]
        while queue:
            cur = queue.pop(0)
            if cur.lchild is None:
                cur.lchild = node
                return
            queue.append(cur.lchild)
            if cur.rchild is None:
                cur.rchild = node
                return
            queue.append(cur.rchild)

    def to_list(self):
        '''
        按从左到右，从上到下的顺序输出
        '''
        queue = [self.root]
        result = []
        while queue:
            cur = queue.pop(0)
            result.append(cur.data)
            if cur.lchild:
                queue.append(cur.lchild)
            if cur.rchild:
                queue.append(cur.rchild)
        return self.__convert_list(result)

    def __repr__(self) -> str:
        data = [str(x) for x in self.to_list()]
        return ''.join(data)

