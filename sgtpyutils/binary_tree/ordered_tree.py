from .full_tree_ex import BinaryTree
from typing import List, Type, overload
from .node import Node

class BinaryTree(BinaryTree):
    def __from_inner_order(otheroder: List, inorder: List, order: int = 0) -> BinaryTree:
        if not otheroder or not inorder:
            return None
        l = len(otheroder)
        # 创建根节点，根节点是前序遍历的第一个数，根节点是后序遍历的最后一个数
        root = otheroder[0] if order == 0 else otheroder[l-1]
        node = Node(root)
        index = inorder.index(root)  # 找到中序遍历根节点所在位置

        l_inorder = inorder[:index]
        r_inorder = inorder[index+1:]
        if order == 0:
            # 对于中序遍历，根节点左边的节点即左子树，根节点右边的节点即右子树
            l_oth = otheroder[1:index+1]
            r_oth = otheroder[index+1:]
            node.lchild = BinaryTree.__from_inner_order(
                l_oth, l_inorder, order)
            node.rchild = BinaryTree.__from_inner_order(
                r_oth, r_inorder, order)
        else:
            l_oth = otheroder[:index]
            r_oth = otheroder[index:l-1]
            node.lchild = BinaryTree.__from_inner_order(
                l_oth, l_inorder, order)
            node.rchild = BinaryTree.__from_inner_order(
                r_oth, r_inorder, order)
        node.data = root
        return node

    def from_inner_order(otheroder: List, inorder: List, order: int = 0) -> BinaryTree:
        '''
        通过两个顺序还原二叉树
        order:int
          0:通过前序和中序获取
          1:通过后序和中序获取
        '''
        t = type(otheroder)
        otheroder = BinaryTree.__convert_data(otheroder)
        inorder = BinaryTree.__convert_data(inorder)
        r = BinaryTree.__from_inner_order(otheroder, inorder, order)
        return BinaryTree(r, as_type=t)

    def from_preorder_and_inorder(preorder: List, inorder: List) -> BinaryTree:
        return BinaryTree.from_inner_order(preorder, inorder, 0)

    def from_postorder_and_inorder(postorder: List, inorder: List) -> BinaryTree:
        return BinaryTree.from_inner_order(postorder, inorder, 1)

