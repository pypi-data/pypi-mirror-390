#!/usr/bin/env python3
# coding = utf8
from lazysdk import showdata


def convert2dict(header_str: str):
    header_temp = header_str.split('\n')
    header_dict = dict()
    for each in header_temp:
        if len(each) == 0:
            continue
        else:
            each_split = each.split(': ')
            header_dict[each_split[0]] = each_split[1]
    return header_dict


def get_lines():
    lines = []
    print("请输入多行数据，以空行结束：")
    while True:
        line = input()
        if line:
            lines.append(line)
        else:
            break

    print("您输入的多行数据是：")
    return "\n".join(lines)


if __name__ == '__main__':
    test_lines = get_lines()
    showdata.show_dict(convert2dict(header_str=test_lines))

