from sgtpyutils.binary_tree import BinaryTree



def test_order():
    t = BinaryTree.from_full_tree('123456')
    '124536' == t.travel_preorder()
    '425163' == t.travel_inorder()
    '452631' == t.travel_postorder()


def test_full_tree():
    raw = 'icnerrseaetrvee'
    t = BinaryTree.from_full_tree_preorder(raw)
    result = t.to_list()
    assert 'icanreversetree' == result


def test_recover():
    post_order = '20f0Th{2tsIS_icArE}e7__w'
    in_order = '2f0t02T{hcsiI_SwA__r7Ee}'
    t = BinaryTree.from_postorder_and_inorder(post_order, in_order)
    result = t.travel_preorder()
    assert 'wctf2020{This_IS_A_7reE}' == result
