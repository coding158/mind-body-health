#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""打印阅读器所有子窗口的类名和位置，帮助定位 TreeView 控件"""
import win32gui

def find_reader():
    result = []
    def cb(hwnd, _):
        t = win32gui.GetWindowText(hwnd)
        if '新时代' in t and '典藏版' in t:
            result.append(hwnd)
    win32gui.EnumWindows(cb, None)
    return result[0] if result else None

def dump_children(hwnd, depth=0):
    indent = '  ' * depth
    cls   = win32gui.GetClassName(hwnd)
    txt   = win32gui.GetWindowText(hwnd)[:30]
    rect  = win32gui.GetWindowRect(hwnd)
    w = rect[2] - rect[0]
    h = rect[3] - rect[1]
    print(f'{indent}[{cls}] "{txt}"  size={w}x{h}  rect={rect}')

    # 递归枚举子窗口
    children = []
    def cb(child, _):
        children.append(child)
    try:
        win32gui.EnumChildWindows(hwnd, cb, None)
    except Exception:
        pass
    for c in children:
        # 只打直接子级（parent==hwnd）
        try:
            if win32gui.GetParent(c) == hwnd:
                dump_children(c, depth + 1)
        except Exception:
            pass

root = find_reader()
if not root:
    print('❌ 找不到阅读器窗口')
else:
    print(f'根窗口 HWND={root}')
    dump_children(root)
