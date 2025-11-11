

def split(
        list_in: list,
        split_gap: int
):
    """
    将输入的list按照split_gap进行分割
    """
    list_out = list()
    split_num = 0
    for i in range(len(list_in)):
        if i % split_gap == 0:
            list_out.append(list())
            split_num += 1
        list_out[split_num-1].append(list_in[i])
    return list_out


def list_difference(
        list_left: list,
        list_right: list,
        keep_sort: bool = False
):
    """
    返回两个list的差集，效果等于list_left-list_right，返回无序；

    在 Python 中，可以使用集合（`set`）的特性来取两个列表的差集。差集是指只在一个集合中出现而在另一个集合中没有的元素。
    使用集合的 `difference()` 方法可以实现列表的差集操作。
    需要注意的是，集合是无序的，因此在结果中元素的顺序可能与原始列表不同。如果需要保留原始列表的顺序，可以使用列表推导式来实现差集操作
    """
    if keep_sort:
        return [x for x in list_left if x not in list_right]  # 返回有序
    else:
        return list(set(list_left).difference(list_right))  # 返回无序


if __name__ == '__main__':
    print(list_difference(
        list_left=[4,1,2],
        list_right=[2,3],
        keep_sort=True
    ))